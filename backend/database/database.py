from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# 비동기 SQLAlchemy 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=True)

# 비동기 세션 설정
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# 데이터베이스 세션 의존성
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session