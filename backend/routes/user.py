from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from database import database, schemas, crud
from config import *

router = APIRouter()

# 사용자 생성 API (POST 요청)
@router.post("/", response_model=schemas.UserResponse)
async def createUser(user: schemas.UserCreate, db: AsyncSession = Depends(database.get_db)):
    return await crud.create_user(db, user)

# 모든 사용자 조회 API (GET 요청)
@router.get("/", response_model=list[schemas.UserResponse])
async def readUsers(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(database.get_db)):
    return await crud.get_users(db, skip=skip, limit=limit)