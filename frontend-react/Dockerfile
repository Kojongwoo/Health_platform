# frontend-react/Dockerfile

# --- 1. 빌드 스테이지 ---
# Node.js 20 버전을 빌더로 지정
FROM node:20 as builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# React 앱을 빌드하여 /app/dist 폴더에 정적 파일 생성
RUN npm run build

# --- 2. 운영 스테이지 ---
# 가벼운 웹서버인 Nginx 이미지 사용
FROM nginx:stable-alpine

# 빌드 스테이지의 결과물(/app/dist)을 Nginx의 기본 웹 루트 폴더로 복사
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx 설정을 덮어쓰기 위해 아래에서 만들 설정 파일을 복사
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 80번 포트를 외부에 노출
EXPOSE 80