# 1. 사용할 Python 기반 이미지 선택
# FROM python:3.13.2
FROM python:3.10

# 2. 컨테이너 내부에서 사용할 작업 디렉토리 설정
WORKDIR /app

# 3. 필요한 파일을 컨테이너 내부로 복사
COPY requirements.txt .

# Rust 설치
RUN apt update
# RUN apt install -y rustc cargo

# 4. pip를 최신 버전으로 업데이트
RUN python -m pip install --upgrade pip

# 5. 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 6. 프로젝트 코드 전체를 컨테이너 내부로 복사
# COPY . .

# 7. FastAPI 서버 실행
# ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app"]
