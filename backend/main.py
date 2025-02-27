from fastapi import FastAPI, Depends, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from database import models, database, schemas, crud
from contextlib import asynccontextmanager
from uuid_extensions import uuid7str
import os
import uuid
import shutil
import random
from ml.process_video import extract_frames
from ml.predict_deepfake_model import process_all_frames
from fastapi.middleware.cors import CORSMiddleware


# 애플리케이션 시작 시 데이터베이스 테이블 생성
async def init_db():
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("DB 연결을 설정합니다...")
    await init_db()  # 데이터베이스 연결 설정
    yield
    # print("DB 연결을 해제합니다...")
    # await app.state.db.close()  # DB 연결 해제

app = FastAPI(lifespan=lifespan)

origins = [
    r"https://tuk-2024-deepfakedetection.streamlit.app",  # 프론트 배포 도메인
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 허용할 origin 목록
    allow_credentials=True,  # 인증 정보 포함 허용 (예: 쿠키, Authorization 헤더)
    allow_methods=["*"],  # 모든 HTTP 메서드 허용 (GET, POST, PUT 등)
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

IMAGE_DIR = "images"
VIDEO_DIR = "videos"
# VIDEO_DIR = "images"

# 딥페이크 판단 임계값 설정
THRESHOLD = 0.5

os.makedirs(IMAGE_DIR, exist_ok=True)  # 디렉토리가 없으면 생성
os.makedirs(VIDEO_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=IMAGE_DIR), name="static")

# 사용자 생성 API (POST 요청)
@app.post("/users/", response_model=schemas.UserResponse)
async def createUser(user: schemas.UserCreate, db: AsyncSession = Depends(database.get_db)):
    return await crud.create_user(db, user)

# 모든 사용자 조회 API (GET 요청)
@app.get("/users/", response_model=list[schemas.UserResponse])
async def readUsers(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(database.get_db)):
    return await crud.get_users(db, skip=skip, limit=limit)

@app.post("/video/")
async def postVideo(file: UploadFile = File(...), model: str = Form(...), db: AsyncSession = Depends(database.get_db)):
    """클라이언트가 업로드한 동영상을 서버에 저장하고, 저장된 URL을 반환"""
    # UUID 생성 및 디렉토리 생성
    video_id = uuid7str()  # 파일명 충돌 방지를 위한 UUID 생성
    video_directory = os.path.join(VIDEO_DIR, video_id)  # 저장할 디렉토리 경로
    os.makedirs(video_directory, exist_ok=True)  # 디렉토리가 없으면 생성

    # # 파일 저장
    # file_extension = file.filename.split(".")[-1]  # 확장자 추출
    # # filename = f"{video_id}.{file_extension}"  # 고유한 파일명 생성
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

    # 예측 - 노트북이라 비활성화 - 활성화
    predictions = process_all_frames(image_directory, use_gradcam=True)
    
    is_deepfake = any(prob > THRESHOLD for prob in predictions)

    # 비디오 정보 DB에 저장
    video = models.Video(id=video_id, is_deepfake=is_deepfake, model=model)
    db.add(video)
    await db.commit()
    
    # 프레임별 예측 결과 저장
    frame_predictions = [
        models.FramePrediction(video_id=video_id, frame_number=index, deepfake_probability=pred)
        for index, pred in enumerate(predictions)
    ]
    db.add_all(frame_predictions)
    await db.commit()

    # 로컬에 있는 이미지 파일을 URL로 변환하여 반환
    # image_files = os.listdir(IMAGE_DIR)
    image_files = sorted(os.listdir(original_image_directory))
    image_urls = [ # 노트북이라 비활성화
        {"frame_index": index, "original_image": f"/static/{video_id}/original/{filename}", "gradcam_image": f"/static/{video_id}/gradcam/gradcam_{filename}", "prediction": predictions[index]}
        # {"frame_index": index, "original_image": f"/static/{video_id}/original/{filename}", "gradcam_image": f"/static/{video_id}/original/{filename}", "prediction": random.random()}
        for index, filename in enumerate(image_files)
    ]
    
    return {"model": model, "images": image_urls}