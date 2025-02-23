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

IMAGE_DIR = "images"
VIDEO_DIR = "videos"

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

    # 파일 저장
    file_extension = file.filename.split(".")[-1]  # 확장자 추출
    # filename = f"{video_id}.{file_extension}"  # 고유한 파일명 생성
    filename = file.filename
    file_path = os.path.join(video_directory, filename)  # 저장할 경로

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # DB에 저장
    video = models.Video(id=video_id, is_deepfake=random.choice([True, False]), model=model)
    db.add(video)
    await db.commit()

    # file_url = f"/static/{filename}"  # 저장된 파일의 URL 생성

    # return {"video_id": video_id, "video_url": file_url}

    # 로컬에 있는 이미지 파일을 URL로 변환하여 반환
    image_files = os.listdir(IMAGE_DIR)
    
    # # 이미지 파일들에 대한 URL 생성
    # image_urls = [
    #     {"image_id": str(uuid.uuid4()), "image_url": f"/static/{filename}", "prediction": random.random()}
    #     for filename in image_files
    # ]
    image_urls = [
        {"frame_index": index, "original_image": f"/static/{filename}", "gradcam_image": f"/static/{filename}", "prediction": random.random()}
        for index, filename in enumerate(image_files)
    ]
    
    return {"model": model, "images": image_urls}