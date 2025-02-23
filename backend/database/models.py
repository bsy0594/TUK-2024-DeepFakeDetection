from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Float, PrimaryKeyConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.dialects.postgresql import UUID
from uuid_extensions import uuid7
import datetime

class Base(DeclarativeBase, AsyncAttrs):
    pass

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid7())
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    # 관계 설정
    # videos = relationship("Video", back_populates="user", cascade="all, delete-orphan") - 로그인 기능을 구현하지 않아 비활성화

class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7())  # 비디오 고유 ID
    # user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)  # 외래 키 (User 테이블의 id 참조) - 지금은 로그인 기능을 구현하지 않아 비활성화
    is_deepfake = Column(Boolean, nullable=False)  # 딥페이크 여부 (True/False)
    model = Column(String, nullable=False)  # 사용된 모델
    # created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))  # 업로드 시간 - 지금은 오류가 발생하여 비활성화

    # 관계 설정
    # user = relationship("User", back_populates="videos") - 로그인 기능을 구현하지 않아 비활성화
    frames = relationship("FramePrediction", back_populates="video", cascade="all, delete-orphan")

class FramePrediction(Base):
    __tablename__ = "frame_predictions"

    # id = Column(UUID(as_uuid=True), primary_key=True, default=ulid.new, index=True)  # 프레임 예측 ID
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False, index=True)  # 영상 ID (UUID)
    frame_number = Column(Integer, nullable=False, index=True)  # 프레임 번호
    deepfake_probability = Column(Float, nullable=False)  # 딥페이크 확률 (0~1)

    __table_args__ = (PrimaryKeyConstraint("video_id", "frame_number"),)

    # 관계 설정
    video = relationship("Video", back_populates="frames")