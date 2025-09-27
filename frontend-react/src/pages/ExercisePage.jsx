// src/pages/ExercisePage.jsx
import React, { useState, useEffect } from 'react';
import apiFetch from '../apiClient';
import '../App.css';

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
        {recommendation.recommendations.map((ex) => (
          <li key={ex.id}>
            <strong>{ex.name}</strong>: {ex.description}
          </li>
        ))}
      </ul>
    </div>
  );
}
export default ExercisePage;