# 업로드 데이터 저장 디렉토리
IMAGE_DIR = "uploaded_images"
VIDEO_DIR = "uploaded_videos"

# 보안 관련
SECRET_KEY="super_ultra_secret_key" # JWT 암호화 키
ALGORITHM = "HS256" # JWT 알고리즘
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30분 후 토큰 만료