// src/apiClient.js

const BASE_URL = 'http://127.0.0.1:5000';

// API 요청을 위한 범용 함수
async function apiFetch(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // 토큰이 있으면 Authorization 헤더에 추가
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // 401 Unauthorized 에러 처리 (토큰 만료 등)
  if (response.status === 401) {
    // 토큰을 삭제하고 로그인 페이지로 강제 이동
    localStorage.removeItem('token');
    alert('세션이 만료되었습니다. 다시 로그인해주세요.');
    window.location.href = '/login';
    // 에러를 발생시켜 이후 코드 실행을 중단
    throw new Error('Unauthorized');
  }

  return response;
}

export default apiFetch;