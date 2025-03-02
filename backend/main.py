from fastapi import FastAPI, Depends, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from database import models, database, schemas, crud
from contextlib import asynccontextmanager
# from ml.predict_deepfake_model import process_all_frames
from fastapi.middleware.cors import CORSMiddleware
from config import *
from routes import video, user


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

app.mount("/static", StaticFiles(directory=IMAGE_DIR), name="static")

app.include_router(video.router, prefix="/video")
app.include_router(user.router, prefix="/user")

@app.get("/")
async def root():
    """API 서버 동작 여부 확인"""
    return {"message": "Hello, World!"}