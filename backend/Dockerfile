# 1. 사용할 Python 기반 이미지 선택
FROM python:3.13.2

# 2. 컨테이너 내부에서 사용할 작업 디렉토리 설정
WORKDIR /app

# 3. 필요한 파일을 컨테이너 내부로 복사
COPY requirements.txt .

# 4. 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. 프로젝트 코드 전체를 컨테이너 내부로 복사
COPY . .

# 6. FastAPI 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]