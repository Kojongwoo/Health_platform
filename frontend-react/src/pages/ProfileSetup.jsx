// src/pages/ProfileSetup.jsx
import React, { useState } from 'react';
import '../App.css';
import apiFetch from '../apiClient'; // fetch 대신 apiClient를 import

// onProfileUpdate 함수를 props로 받습니다.
function ProfileSetup({ onProfileUpdate }) {
  const [gender, setGender] = useState('male');
  const [height, setHeight] = useState('');
  const [weight, setWeight] = useState('');
  const [goal, setGoal] = useState('다이어트');
  const [age, setAge] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    const token = localStorage.getItem('token');

    const profileData = { 
      gender, 
      height: parseFloat(height), 
      weight: parseFloat(weight), 
      goal, 
      age:parseInt(age) 
    };
    
    try {
      const response = await apiFetch('/api/profile', {
        method: 'POST',
        body: JSON.stringify(profileData)
      });

      if (response.ok) {
        alert('프로필이 저장되었습니다!');
        onProfileUpdate();
      } else {
        alert('프로필 저장에 실패했습니다.');
      }
        } catch (error) {
      console.error("Profile setup error:", error);
    }
  };

  return (
    <div className="container">
      <h2>프로필 설정</h2>
      <p>맞춤형 추천을 위해 기본 정보를 입력해주세요.</p>
      <form onSubmit={handleSubmit}>
        {/* 폼 입력 필드들 (성별, 키, 몸무게, 목표) */}
        <div className="form-group">
            <label>성별:</label>
            <select value={gender} onChange={e => setGender(e.target.value)}>
                <option value="male">남성</option>
                <option value="female">여성</option>
                <option value="other">기타</option>
            </select>
        </div>
        
        <div className="form-group">
            <label>키 (cm):</label>
            <input type="number" value={height} onChange={e => setHeight(e.target.value)} required />
        </div>

        <div className="form-group">
            <label>몸무게 (kg):</label>
            <input type="number" value={weight} onChange={e => setWeight(e.target.value)} required />
        </div>

        <div className="form-group">
            <label>나이:</label>
            <input type="number" value={age} onChange={e => setAge(e.target.value)} required />
        </div>

        <div className="form-group">
            <label>목표:</label>
            <select value={goal} onChange={e => setGoal(e.target.value)}>
                <option value="다이어트">다이어트</option>
                <option value="근성장">근성장</option>
                <option value="건강유지">건강유지</option>
            </select>
        </div>
        <button type="submit">저장하기</button>
      </form>
    </div>
  );
}
export default ProfileSetup;