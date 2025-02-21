from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from database import models, database, schemas, crud
from contextlib import asynccontextmanager
import os
import uuid

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

app.mount("/static", StaticFiles(directory=IMAGE_DIR), name="static")

# 사용자 생성 API (POST 요청)
@app.post("/users/", response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(database.get_db)):
    return await crud.create_user(db, user)

# 모든 사용자 조회 API (GET 요청)
@app.get("/users/", response_model=list[schemas.UserResponse])
async def read_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(database.get_db)):
    return await crud.get_users(db, skip=skip, limit=limit)

@app.post("/video/")
async def postVideo():
    """로컬에 있는 이미지 파일을 URL로 변환하여 반환"""
    image_files = os.listdir(IMAGE_DIR)
    
    # 이미지 파일들에 대한 URL 생성
    image_urls = [
        {"image_id": str(uuid.uuid4()), "image_url": f"/static/{filename}"}
        for filename in image_files
    ]
    
    return {"images": image_urls}