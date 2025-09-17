# backend/Dockerfile

# 1. 베이스 이미지 선택 (Python 3.11 슬림 버전)
FROM python:3.11-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 필요한 라이브러리 설치 (requirements.txt만 먼저 복사하여 캐시 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 나머지 소스 코드 복사
COPY . .

# 5. gunicorn 서버 실행
# 0.0.0.0:5000 포트로 app.py 파일의 app 객체를 실행
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]