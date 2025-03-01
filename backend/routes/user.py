from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import database, schemas, crud
from database.models import User
from config import *
from utils.security import hash_password, verify_password, create_access_token

router = APIRouter()

# 사용자 생성 API (POST 요청)
@router.post("/", response_model=schemas.UserTest)
async def createUser(user: schemas.UserCreate, db: AsyncSession = Depends(database.get_db)):
    """사용자 생성 API - Test"""
    return await crud.create_user(db, user)

# 모든 사용자 조회 API (GET 요청)
@router.get("/", response_model=list[schemas.UserTest])
async def readUsers(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(database.get_db)):
    """사용자 조회 API - Test"""
    return await crud.get_users(db, skip=skip, limit=limit)

# 회원가입
@router.post("/signup", response_model=schemas.UserResponse)
async def signup(user: schemas.UserCreate, db: AsyncSession = Depends(database.get_db)):
    """사용자 회원가입 - 중복 id, email 및 nickname 검사 후 저장"""
    # 중복 검사 (id, email)
    result = await db.execute(select(User).filter((User.id == user.id) | (User.email == user.email) | (User.nickname == user.nickname)))
    existing_user = result.scalars().first()

    if existing_user:
        if existing_user.id == user.id:
            raise HTTPException(status_code=400, detail="ID already exists")
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Email already exists")
        if existing_user.nickname == user.nickname:
            raise HTTPException(status_code=400, detail="Nickname already exists")
        
    # 비밀번호 해싱 후 저장
    hashed_pw = hash_password(user.password)
    new_user = User(id=user.id, nickname=user.nickname, email=user.email, hashed_password=hashed_pw)
    
    db.add(new_user)
    await db.commit()
    return new_user

@router.post("/login")
async def login(request: schemas.UserLogin, db: AsyncSession = Depends(database.get_db)):
    """사용자 로그인"""
    result = await db.execute(select(User).where(User.id == request.id))
    user = result.scalar()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.nickname})

    return {"access_token": access_token, "token_type": "bearer"}