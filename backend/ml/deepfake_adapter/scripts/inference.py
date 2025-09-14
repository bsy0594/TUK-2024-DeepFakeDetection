#!/usr/bin/env python3
import sys
from pathlib import Path
import os
import shutil
import json
import cv2
import torch
import yaml
from PIL import Image
from torch.utils.data import DataLoader

# (1) 프로젝트 루트 잡기
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# ── 이 스크립트(.py) 파일이 있는 폴더(scripts) 기준으로 임시 폴더를 만듭니다.
script_dir = Path(__file__).resolve().parent

from src.datasets.ffpp_dataset import FFPPFrameDataset
from src.models.deepfake_adapter import DeepfakeAdapter
from src.utils.transforms import get_ffpp_transforms

def clear_dir(out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
        return
    for entry in os.scandir(out_dir):
        path = entry.path
        if entry.is_dir():
            shutil.rmtree(path)
        else:
            os.remove(path)

def extract_frames(video_path: str, out_dir: str, interval: int = 1):
    # out_dir 클리어
    clear_dir(out_dir)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")

    idx = 0
    saved = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % interval == 0:
            path = os.path.join(out_dir, f"frame_{idx:06d}.jpg")
            from PIL import Image
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            Image.fromarray(rgb).save(path)
            saved += 1
        idx += 1
    cap.release()
    return saved

class TempFrameDataset(torch.utils.data.Dataset):
    def __init__(self, paths, tf):
        self.paths, self.tf = paths, tf
    def __len__(self):
        return len(self.paths)
    def __getitem__(self, i):
        img = Image.open(self.paths[i]).convert("RGB")
        return self.tf(img), self.paths[i]

def main():
    # 2) 설정 파일 로드
    cfg_path = project_root / "configs" / "ffpp_c23.yaml"
    assert cfg_path.exists(), f"Config not found: {cfg_path}"
    cfg = yaml.safe_load(open(cfg_path, "r"))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 3) 비디오 → 프레임 추출
    video_path = project_root / "data" / "raw_videos" / "sample_video.mp4"
    assert video_path.exists(), f"Video not found: {video_path}"
    # → scripts 폴더 안에 temp_frames_infer 생성
    temp_dir = script_dir / "temp_frames_infer"

    print("▶ Extracting frames…")
    n_frames = extract_frames(str(video_path), str(temp_dir), interval=1)
    print(f"✔ Extracted {n_frames} frames to '{temp_dir}'\n")

    # 4) DataLoader 준비
    _, val_tf = get_ffpp_transforms(cfg["input_size"])
    frame_files = sorted(map(str, temp_dir.glob("*.jpg")))
    assert frame_files, f"No frames found for inference! (see DEBUG above)"
    print(f"▶ Building DataLoader with {len(frame_files)} frames")
    loader = DataLoader(
        TempFrameDataset(frame_files, val_tf),
        batch_size=cfg["batch_size"],
        shuffle=False,
        num_workers=0,
        pin_memory=True
    )
    print("✔ DataLoader ready\n")

    # 5) 모델 로드
    out_dir = Path(cfg["output_dir"])
    if not out_dir.is_absolute():
        out_dir = project_root / out_dir
    ckpt_path = out_dir / "best.pth"
    assert ckpt_path.exists(), f"Checkpoint not found: {ckpt_path}"

    model = DeepfakeAdapter(cfg).to(device)
    ckpt = torch.load(str(ckpt_path), map_location=device, weights_only=False)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    print("✔ Model loaded\n")

    # 6) 예측
    results = {}
    print("▶ Starting inference…")
    with torch.no_grad():
        for imgs, paths in loader:
            imgs = imgs.to(device)
            probs = torch.softmax(model(imgs), dim=1)[:, 1].cpu().tolist()
            for p, pr in zip(paths, probs):
                # frame_000000.jpg 처럼 파일명만 키로 사용
                results[Path(p).name] = pr
    print("✔ Inference done\n")

    # 7) JSON 저장
    out_json_dir = project_root / "outputs" / "predictions"
    out_json_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_json_dir / f"{video_path.stem}.json"
    # ensure_ascii=False 로 한글 경로/문자가 이스케이프되지 않도록
    with open(out_json, "w", encoding="utf-8") as fp:
        json.dump(results, fp, indent=2, ensure_ascii=False)
    print(f"✔ Saved prediction results to {out_json}")

if __name__ == "__main__":
    main()
