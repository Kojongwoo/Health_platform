// src/pages/LandingPage.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import '../App.css';

function LandingPage() {
  return (
    <div className="container">
      <h1>개인 맞춤형 건강 관리 플랫폼</h1>
      <p>
        환영합니다.
        <br />
        로그인하여 맞춤형 식단과 운동을 추천받아보세요.
      </p>
      <div>
        <Link to="/login"><button>로그인</button></Link>
        <Link to="/signup"><button>회원가입</button></Link>
      </div>
    </div>
  );
}

export default LandingPage;