// src/pages/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ProfileSetup from './ProfileSetup';
import '../App.css';
import apiFetch from '../apiClient';

function Dashboard() {
    const navigate = useNavigate();
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [foodName, setFoodName] = useState('');
    const [calories, setCalories] = useState('');

    // --- 수정 기능을 위한 state 추가 ---
    const [editingMealId, setEditingMealId] = useState(null); // 현재 수정 중인 항목의 id
    const [editedFoodName, setEditedFoodName] = useState('');
    const [editedCalories, setEditedCalories] = useState('');

    const fetchDashboardData = async () => {
        try {
        // fetch를 apiFetch로 변경
        const response = await apiFetch('/api/dashboard');
        if (response.ok) {
            const data = await response.json();
            setDashboardData(data);
        } else {
            setDashboardData(null);
        }
        } catch (error) {
        // 401 에러는 apiClient에서 처리하므로 여기서는 다른 네트워크 에러만 잡힙니다.
        console.error("Dashboard data fetch error:", error);
        }
        setLoading(false);
    };

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    const handleMealSubmit = async (event) => {
        event.preventDefault();
        try {
        const response = await apiFetch('/api/meals', {
            method: 'POST',
            body: JSON.stringify({ food_name: foodName, calories: parseInt(calories) })
        });

        if (response.ok) {
            setFoodName('');
            setCalories('');
            fetchDashboardData();
        } else {
            const result = await response.json();
            alert(result.error || '식단 기록에 실패했습니다.');
        }
        } catch (error) {
        console.error("Meal submit error:", error);
        }
    };

  // --- 삭제 처리 함수 추가 ---
    const handleDelete = async (mealId) => {
        if (window.confirm('정말로 이 항목을 삭제하시겠습니까?')) {
            try {
                const response = await apiFetch(`/api/meals/${mealId}`, { method: 'DELETE' });
                if (response.ok) {
                    fetchDashboardData(); // 삭제 성공 후 목록 새로고침
                } else {
                    alert('삭제에 실패했습니다.');
                }
            } catch (error) {
                console.error("Delete error:", error);
            }
        }
    };

    // --- 수정 모드 시작 함수 추가 ---
    const handleEdit = (meal) => {
        setEditingMealId(meal.id);
        setEditedFoodName(meal.food_name);
        setEditedCalories(meal.calories);
    };

    // --- 수정 완료 처리 함수 추가 ---
    const handleUpdate = async (mealId) => {
        try {
            const response = await apiFetch(`/api/meals/${mealId}`, {
                method: 'PUT',
                body: JSON.stringify({ food_name: editedFoodName, calories: parseInt(editedCalories) })
            });
            if (response.ok) {
                setEditingMealId(null); // 수정 모드 종료
                fetchDashboardData(); // 수정 성공 후 목록 새로고침
            } else {
                alert('수정에 실패했습니다.');
            }
        } catch (error) {
            console.error("Update error:", error);
        }
    };

    if (loading) return <div>로딩 중...</div>;
    if (!dashboardData) return <ProfileSetup onProfileUpdate={fetchDashboardData} />;

    const { profile, recommended_calories, total_calories_today, meals_today, bmr, bmi } = dashboardData;

    return (
        <div>
            <div className="container">
                <h2>{profile.name}님의 대시보드 ({profile.goal} 목표)</h2>
                <p>기초대사량(BMR): <strong>{bmr} kcal</strong></p>
                <p>체질량지수(BMI): <strong>{bmi}</strong></p>
                <p>오늘 섭취 칼로리: <strong>{total_calories_today} / {recommended_calories} kcal</strong></p>
                <button onClick={handleLogout}>로그아웃</button>
            </div>

            <div className="container">
                <h3>식단 기록하기</h3>
                <form onSubmit={handleMealSubmit}>
                    <div className="form-group">
                        <label>음식 이름:</label>
                        <input type="text" value={foodName} onChange={e => setFoodName(e.target.value)} required />
                    </div>
                    <div className="form-group">
                        <label>칼로리 (kcal):</label>
                        <input type="number" value={calories} onChange={e => setCalories(e.target.value)} required />
                    </div>
                    <button type="submit">기록하기</button>
                </form>
            </div>

              <div className="container">
                <h3>오늘의 식단 기록</h3>
                <ul>
                    {meals_today.map((meal) => (
                        <li key={meal.id}>
                            {editingMealId === meal.id ? (
                                // ----- 수정 모드일 때 UI -----
                                <div>
                                    <input type="text" value={editedFoodName} onChange={(e) => setEditedFoodName(e.target.value)} />
                                    <input type="number" value={editedCalories} onChange={(e) => setEditedCalories(e.target.value)} />
                                    <button onClick={() => handleUpdate(meal.id)}>저장</button>
                                    <button onClick={() => setEditingMealId(null)}>취소</button>
                                </div>
                            ) : (
                                // ----- 일반 모드일 때 UI -----
                                <div>
                                    {meal.food_name} - {meal.calories} kcal
                                    <button onClick={() => handleEdit(meal)}>수정</button>
                                    <button onClick={() => handleDelete(meal.id)}>삭제</button>
                                </div>
                            )}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
}
export default Dashboard;