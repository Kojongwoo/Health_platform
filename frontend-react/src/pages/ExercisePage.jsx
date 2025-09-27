// src/pages/ExercisePage.jsx
import React, { useState, useEffect } from 'react';
import apiFetch from '../apiClient';
import '../App.css';

// 백엔드 기본 URL
const BASE_URL = 'http://127.0.0.1:5000';

function ExercisePage() {
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchExercises = async () => {
      try {
        const response = await apiFetch('/api/exercises');
        if (response.ok) setRecommendation(await response.json());
      } catch (error) { console.error("Error fetching exercises:", error); }
      setLoading(false);
    };
    fetchExercises();
  }, []);

  if (loading) return <div className="container">추천 운동을 불러오는 중...</div>;
  if (!recommendation) return <div className="container">추천할 운동이 없거나 프로필을 먼저 완성해주세요.</div>;

  return (
    <div className="container">
      <h2>오늘의 맞춤 운동 추천</h2>
      <p className="recommendation-reason">{recommendation.reason}</p>
      <ul>
<div className="exercise-list">
  {recommendation.recommendations.map((ex) => (
    <div key={ex.id} className="exercise-card">
      {/* 이미지를 위한 컨테이너 */}
      {ex.image_url && (
        <div className="exercise-image-container">
          <img 
            src={`${BASE_URL}${ex.image_url}`} 
            alt={ex.name} 
            className="exercise-image"
          />
        </div>
      )}
      
      {/* 텍스트 정보를 위한 컨테이너 */}
      <div className="exercise-details">
        <h3>{ex.name}</h3>
        <p className="exercise-description">{ex.description}</p>
        {ex.instructions && (
          <div className="exercise-instructions">
            <strong>운동 방법:</strong>
            <p>
              {ex.instructions.split('\\n').map((line, index) => (
                <React.Fragment key={index}>
                  {line}
                  <br />
                </React.Fragment>
              ))}
            </p>
          </div>
        )}
      </div>
    </div>
  ))}
</div>
      </ul>
    </div>
  );
}
export default ExercisePage;