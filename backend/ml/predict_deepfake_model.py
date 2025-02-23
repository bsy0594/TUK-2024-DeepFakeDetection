import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image
import os
import json
from tqdm import tqdm
import numpy as np
import cv2

# ✅ 모델 불러오기
MODEL_PATH = "model/CelebDF_model_20_epochs_99acc.pt"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ✅ 모델 로드
checkpoint = torch.load(MODEL_PATH, map_location=device)
model = checkpoint['model']
model.load_state_dict(checkpoint['model_state_dict'])
model = model.to(device, memory_format=torch.channels_last)
model.eval()

# ✅ 마지막 Convolutional Layer 설정 (XceptionNet 구조에 맞게 수정)
target_layer = model.conv4  # 🚩 모델 구조에 따라 변경 필요

# ✅ 이미지 전처리
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# ✅ GradCAM 생성 함수
def generate_gradcam(input_tensor, model, target_layer):
    gradients = []
    activations = []

    def forward_hook(module, input, output):
        activations.append(output)

    def backward_hook(module, grad_in, grad_out):
        gradients.append(grad_out[0])

    # ✅ Hook 등록
    forward_handle = target_layer.register_forward_hook(forward_hook)
    backward_handle = target_layer.register_full_backward_hook(backward_hook)  # 여기를 수정

    # ✅ Forward Pass
    output = model(input_tensor)
    model.zero_grad()

    # ✅ Backward Pass
    target = output[:, 0]  # 클래스 0을 대상으로 (딥페이크 확률)
    target.backward()

    # ✅ Hook 제거
    forward_handle.remove()
    backward_handle.remove()

    # ✅ 활성화 및 Gradient 수집
    activation = activations[0].squeeze(0).cpu().detach().numpy()
    gradient = gradients[0].squeeze(0).cpu().detach().numpy()

    # ✅ Grad-CAM 계산
    weights = np.mean(gradient, axis=(1, 2))  # Global Average Pooling
    gradcam = np.maximum(np.sum(weights[:, np.newaxis, np.newaxis] * activation, axis=0), 0)

    # ✅ 정규화
    gradcam = (gradcam - gradcam.min()) / (gradcam.max() - gradcam.min() + 1e-8)
    gradcam = cv2.resize(gradcam, (224, 224))

    return gradcam



# ✅ GradCAM 결과를 이미지로 변환
def apply_gradcam_overlay(image_path, heatmap):
    img = cv2.imread(image_path)
    heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
    heatmap = np.uint8(255 * heatmap)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

    overlay = cv2.addWeighted(img, 0.6, heatmap, 0.4, 0)
    return overlay

# ✅ 이미지 로드 (배치 단위)
def load_images_in_batches(image_paths, batch_size=16):
    for i in range(0, len(image_paths), batch_size):
        batch_paths = image_paths[i: i + batch_size]
        images = [transform(Image.open(img_path).convert("RGB")) for img_path in batch_paths]
        yield torch.stack(images).to(device), batch_paths

# ✅ 예측 함수
def predict(images_tensor):
    with torch.no_grad():
        outputs = model(images_tensor)
        probabilities = torch.sigmoid(outputs).cpu().numpy()
    return probabilities

# ✅ 전체 프레임 처리
def process_all_frames(input_folder, output_file, batch_size=16, use_gradcam=False):
    image_files = sorted([os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".jpg")])
    if not image_files:
        print("❌ 이미지 파일이 없습니다.")
        return

    results = {}
    for batch_images, batch_paths in tqdm(load_images_in_batches(image_files, batch_size), total=len(image_files) // batch_size + 1, desc="🔍 Processing"):
        probs = predict(batch_images)
        for path, img_tensor, prob in zip(batch_paths, batch_images, probs):
            frame_name = os.path.basename(path)
            result_data = {"probability": float(prob)}

            # ✅ GradCAM 적용 여부
            if use_gradcam:
                heatmap = generate_gradcam(img_tensor, model, target_layer)
                gradcam_image = apply_gradcam_overlay(path, heatmap)

                # ✅ GradCAM 이미지 저장
                gradcam_filename = f"{os.path.splitext(frame_name)[0]}_gradcam.jpg"
                gradcam_path = os.path.join(input_folder, gradcam_filename)
                cv2.imwrite(gradcam_path, gradcam_image)

                # ✅ JSON에 GradCAM 경로 추가
                result_data["gradcam_path"] = gradcam_path

            results[frame_name] = result_data

    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)
    print(f"✅ 예측 결과 저장 완료: {output_file}")

# ✅ 실행 예시 (Main)
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="딥페이크 프레임 분석기 (CelebDF_model_20_epochs_99acc 모델)")
    parser.add_argument("--input", type=str, required=True, help="프레임이 저장된 폴더 경로")
    parser.add_argument("--output", type=str, default="results/deepfake_results.json", help="결과 저장 파일")
    parser.add_argument("--batch_size", type=int, default=16, help="배치 크기 (기본값: 16)")
    parser.add_argument("--use_gradcam", action="store_true", help="GradCAM 적용 여부 (옵션 선택 시 적용)")

    args = parser.parse_args()
    process_all_frames(args.input, args.output, args.batch_size, args.use_gradcam)
