#!/usr/bin/env python3
"""
xai_inference.py (Fast Mode)

Accelerated saliency map generation using Captum Saliency and batch processing.
"""
import sys
from pathlib import Path
import os
import shutil
import argparse
import yaml
import torch
import numpy as np
from PIL import Image
import cv2

from captum.attr import Saliency
from torch.utils.data import DataLoader, Dataset

# 프로젝트 루트 및 스크립트 경로 설정
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
script_dir = Path(__file__).resolve().parent

# 모델 로드 및 트랜스폼 함수
def get_components():
    from src.models.deepfake_adapter import DeepfakeAdapter
    from src.utils.transforms import get_ffpp_transforms
    return DeepfakeAdapter, get_ffpp_transforms

# 인자 파서 정의
def parse_args():
    parser = argparse.ArgumentParser(description="Fast saliency maps via Captum Saliency and batching")
    parser.add_argument("--config", type=str,
                        default=str(project_root/"configs"/"ffpp_c23.yaml"),
                        help="Path to config YAML file.")
    parser.add_argument("--frames-dir", type=str,
                        default=str(script_dir/"temp_frames_infer"),
                        help="Directory containing extracted frames.")
    parser.add_argument("--output-dir", type=str,
                        default=str(script_dir/"xai_saliency"),
                        help="Directory to save saliency-overlaid images.")
    parser.add_argument("--target-class", type=int, default=1,
                        help="Target class index for attribution (1 = fake).")
    parser.add_argument("--batch-size", type=int, default=16,
                        help="Batch size for saliency computation.")
    parser.add_argument("--num-workers", type=int, default=4,
                        help="Number of DataLoader workers.")
    return parser.parse_args()

# 디렉터리 초기화 함수
# 폴더 자체를 삭제하지 않고 내부 파일만 제거하여 PermissionError 방지
def clear_dir(out_dir):
    # 디렉터리 존재하지 않으면 생성
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
        return
    # 내부 항목만 삭제
    for entry in os.scandir(out_dir):
        path = entry.path
        try:
            if entry.is_dir():
                shutil.rmtree(path)
            else:
                os.remove(path)
        except PermissionError:
            # 읽기 전용 파일인 경우 쓰기 권한 부여 후 재시도
            os.chmod(path, 0o666)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

# 프레임 데이터셋 (배치 처리용)
class SaliencyFrameDataset(Dataset):
    def __init__(self, frames, transform, input_size):
        self.frames = frames
        self.transform = transform
        # input_size may be an int or a sequence; ensure a tuple of (H, W)
        if isinstance(input_size, int):
            self.input_size = (input_size, input_size)
        else:
            self.input_size = tuple(input_size)
    def __len__(self):
        return len(self.frames)
    def __getitem__(self, idx):
        path = self.frames[idx]
        pil = Image.open(path).convert('RGB')
        pil_resized = pil.resize(self.input_size, Image.BILINEAR)
        tensor = self.transform(pil_resized)
        # return tensor, resized image array, original filename
        return tensor, np.array(pil_resized), path.name

def generate_saliency_maps(
    frames_dir: str,
    output_dir: str,
    target_class: int = 1,
    batch_size: int = 16,
    num_workers: int = 4,
    config_path: str = str(project_root / "configs" / "ffpp_c23.yaml")
):
    if not os.path.exists(frames_dir):
        raise FileNotFoundError(f"Frames directory '{frames_dir}' does not exist.")
    if not os.path.exists(output_dir):
        raise FileNotFoundError(f"Output directory '{output_dir}' does not exist.")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file '{config_path}' does not exist.")
    
    # 설정 로드 및 장치 선택
    cfg = yaml.safe_load(open(config_path, 'r'))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 모델 초기화
    DeepfakeAdapter, get_transforms = get_components()
    model = DeepfakeAdapter(cfg).to(device)
    ckpt_base = Path(cfg['output_dir'])
    if not ckpt_base.is_absolute():
        ckpt_base = project_root / ckpt_base
    ckpt = torch.load(str(ckpt_base / "best.pth"), map_location=device)
    model.load_state_dict(ckpt['model_state_dict'])
    model.eval()

    # Captum Saliency 설정 (한 번의 backward)
    saliency = Saliency(model)

    # 변환 함수 준비
    _, val_tf = get_transforms(cfg['input_size'])

    # 프레임 목록 및 출력 폴더 준비
    frames = sorted(Path(frames_dir).glob("*.jpg"))
    clear_dir(output_dir)

    # 데이터로더 구성
    ds = SaliencyFrameDataset(frames, val_tf, cfg['input_size'])
    loader = DataLoader(ds,
                        batch_size=batch_size,
                        shuffle=False,
                        num_workers=num_workers,
                        pin_memory=True)

    # 배치 단위 처리
    for batch_tensors, batch_imgs_np, batch_names in loader:
        batch_tensors = batch_tensors.to(device)
        # ensure gradients on inputs (silences the Captum warning)
        batch_tensors.requires_grad_()
        # Saliency attribution: shape [B, C, H, W]
        attrs = saliency.attribute(batch_tensors, target=target_class)
        # 후처리 및 저장
        for img_np, attr, name in zip(batch_imgs_np, attrs.cpu(), batch_names):
            # --- 여기에 추가 ---
            # DataLoader collate 때문에 img_np가 Tensor일 수 있으므로 numpy array로 변환
            import torch as _T
            if isinstance(img_np, _T.Tensor):
                img_np = img_np.cpu().numpy()
            # 배열이 float 등 다른 타입일 수 있으니 uint8로 맞춰 주기
            img_np = img_np.astype(np.uint8)
            # ----------------
            sal_map = torch.abs(attr).sum(dim=0).numpy()
            sal_map = (sal_map - sal_map.min())/(sal_map.max()-sal_map.min()+1e-8)
            heatmap = np.uint8(255 * sal_map)
            heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            overlay = cv2.addWeighted(img_bgr, 0.6, heatmap_color, 0.4, 0)
            overlay_rgb = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)
            out_path = Path(output_dir) / name.replace('.jpg', '_sal.jpg')
            Image.fromarray(overlay_rgb).save(out_path)

    print(f"✔ Saved saliency maps ({len(frames)}) to '{output_dir}' using batch size {batch_size}")

# 메인 실행
if __name__ == '__main__':
    args = parse_args()

    # 설정 로드 및 장치 선택
    cfg = yaml.safe_load(open(args.config, 'r'))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 모델 초기화
    DeepfakeAdapter, get_transforms = get_components()
    model = DeepfakeAdapter(cfg).to(device)
    ckpt_base = Path(cfg['output_dir'])
    if not ckpt_base.is_absolute():
        ckpt_base = project_root / ckpt_base
    ckpt = torch.load(str(ckpt_base / "best.pth"), map_location=device)
    model.load_state_dict(ckpt['model_state_dict'])
    model.eval()

    # Captum Saliency 설정 (한 번의 backward)
    saliency = Saliency(model)

    # 변환 함수 준비
    _, val_tf = get_transforms(cfg['input_size'])

    # 프레임 목록 및 출력 폴더 준비
    frames = sorted(Path(args.frames_dir).glob("*.jpg"))
    clear_dir(args.output_dir)

    # 데이터로더 구성
    ds = SaliencyFrameDataset(frames, val_tf, cfg['input_size'])
    loader = DataLoader(ds,
                        batch_size=args.batch_size,
                        shuffle=False,
                        num_workers=args.num_workers,
                        pin_memory=True)

    # 배치 단위 처리
    for batch_tensors, batch_imgs_np, batch_names in loader:
        batch_tensors = batch_tensors.to(device)
        # ensure gradients on inputs (silences the Captum warning)
        batch_tensors.requires_grad_()
        # Saliency attribution: shape [B, C, H, W]
        attrs = saliency.attribute(batch_tensors, target=args.target_class)
        # 후처리 및 저장
        for img_np, attr, name in zip(batch_imgs_np, attrs.cpu(), batch_names):
            # --- 여기에 추가 ---
            # DataLoader collate 때문에 img_np가 Tensor일 수 있으므로 numpy array로 변환
            import torch as _T
            if isinstance(img_np, _T.Tensor):
                img_np = img_np.cpu().numpy()
            # 배열이 float 등 다른 타입일 수 있으니 uint8로 맞춰 주기
            img_np = img_np.astype(np.uint8)
            # ----------------
            sal_map = torch.abs(attr).sum(dim=0).numpy()
            sal_map = (sal_map - sal_map.min())/(sal_map.max()-sal_map.min()+1e-8)
            heatmap = np.uint8(255 * sal_map)
            heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            overlay = cv2.addWeighted(img_bgr, 0.6, heatmap_color, 0.4, 0)
            overlay_rgb = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)
            out_path = Path(args.output_dir) / name.replace('.jpg', '_sal.jpg')
            Image.fromarray(overlay_rgb).save(out_path)

    print(f"✔ Saved saliency maps ({len(frames)}) to '{args.output_dir}' using batch size {args.batch_size}")
