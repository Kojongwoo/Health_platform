// src/pages/Login.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // 페이지 이동을 위한 hook
import '../App.css';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate(); // useNavigate hook 사용

  const handleSubmit = async (event) => {
    event.preventDefault();
    const userData = { email, password };

    const response = await fetch('http://127.0.0.1:5000/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });

    const result = await response.json();
    if (response.ok) {
      alert(result.message);
      localStorage.setItem('token', result.token); // 받은 토큰을 브라우저에 저장
      navigate('/dashboard'); // 로그인 성공 시 메인 페이지로 이동
    } else {
      alert(result.error);
    }
  };

  return (
    <div className="container">
      <h1>로그인</h1>
      <form onSubmit={handleSubmit}>
        {/* 이메일, 비밀번호 input JSX (Signup.jsx와 유사하게 구성) */}
        <div className="form-group">
            <label htmlFor="email">이메일:</label>
            <input type="email" id="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>
        <div className="form-group">
            <label htmlFor="password">비밀번호:</label>
            <input type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </div>
        <button type="submit">로그인</button>
      </form>
    </div>
  );
}
export default Login;