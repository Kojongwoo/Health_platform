// src/components/ProtectedRoute.jsx
import React from 'react';
import { Navigate } from 'react-router-dom';

function ProtectedRoute({ children }) {
  // 로그인 시 브라우저에 저장했던 'token'을 가져옵니다.
  const token = localStorage.getItem('token');

  // token이 없으면 (로그인하지 않았으면)
  if (!token) {
    // Navigate 컴포넌트를 사용해 /login 경로로 보냅니다.
    return <Navigate to="/login" replace />;
  }

  // token이 있으면 (로그인했다면) 자식 컴포넌트(메인 대시보드 등)를 보여줍니다.
  return children;
}

export default ProtectedRoute;