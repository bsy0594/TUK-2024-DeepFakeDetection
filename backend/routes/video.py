from fastapi import FastAPI, Depends, UploadFile, File, Form, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from database import models, database, schemas, crud
from uuid_extensions import uuid7str
import os
import shutil
import random
from ml.process_video import extract_frames
# from ml.predict_deepfake_model import process_all_frames
from config import *

router = APIRouter()

os.makedirs(IMAGE_DIR, exist_ok=True)  # 디렉토리가 없으면 생성
os.makedirs(VIDEO_DIR, exist_ok=True)

@router.post("/")
async def postVideo(file: UploadFile = File(...), model: str = Form(...), db: AsyncSession = Depends(database.get_db)):
    """클라이언트가 업로드한 동영상을 서버에 저장하고, 저장된 URL을 반환"""
    # UUID 생성 및 디렉토리 생성
    video_id = uuid7str()  # 파일명 충돌 방지를 위한 UUID 생성
    video_directory = os.path.join(VIDEO_DIR, video_id)  # 저장할 디렉토리 경로
    os.makedirs(video_directory, exist_ok=True)  # 디렉토리가 없으면 생성

    # # 파일 저장
    video_filename = file.filename
    video_file_path = os.path.join(video_directory, video_filename)  # 저장할 경로

    with open(video_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 파일 저장
    image_directory = os.path.join(IMAGE_DIR, video_id)
    original_image_directory = os.path.join(image_directory, "original")
    gradcam_image_directory = os.path.join(image_directory, "gradcam")
    os.makedirs(original_image_directory, exist_ok=True)
    os.makedirs(gradcam_image_directory, exist_ok=True)
    extract_frames(video_file_path, original_image_directory)

    # 예측 - 노트북이라 비활성화
    # predictions = process_all_frames(image_directory, use_gradcam=True)

    # DB에 저장
    video = models.Video(id=video_id, is_deepfake=random.choice([True, False]), model=model)
    db.add(video)
    await db.commit()

    # 로컬에 있는 이미지 파일을 URL로 변환하여 반환
    image_files = os.listdir(original_image_directory)
    image_urls = [ # 노트북이라 비활성화
        # {"frame_index": index, "original_image": f"/static/{video_id}/original/{filename}", "gradcam_image": f"/static/{video_id}/gradcam/{filename}", "prediction": predictions[index]}
        {"frame_index": index, "original_image": f"/static/{video_id}/original/{filename}", "gradcam_image": f"/static/{video_id}/original/{filename}", "prediction": random.random()}
        for index, filename in enumerate(image_files)
    ]
    
    return {"model": model, "images": image_urls}