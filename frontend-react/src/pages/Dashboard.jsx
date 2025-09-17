// src/pages/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ProfileSetup from './ProfileSetup';
import apiFetch from '../apiClient';
import '../App.css';

// MealList, MealItem, EditForm 컴포넌트는 UI 렌더링만 담당하도록 분리
const MealList = ({ title, meals, ...props }) => (
    <div className="container">
        <h3>{title}</h3>
        <ul>
            {meals && meals.length > 0 ? (
                meals.map(meal => (
                    <li key={meal.id}>
                        {props.editingMealId === meal.id ? (
                            <EditForm meal={meal} {...props} />
                        ) : (
                            <MealItem meal={meal} {...props} />
                        )}
                    </li>
                ))
            ) : (
                <li>기록 없음</li>
            )}
        </ul>
    </div>
);

const MealItem = ({ meal, onEdit, onDelete }) => (
    <div>
        {meal.food_name} - {meal.calories} kcal
        <button onClick={() => onEdit(meal)}>수정</button>
        <button onClick={() => onDelete(meal.id)}>삭제</button>
    </div>
);

const EditForm = ({ meal, onUpdate, onCancelEdit, editedFoodName, setEditedFoodName, editedCalories, setEditedCalories }) => (
    <div>
        <input type="text" value={editedFoodName} onChange={(e) => setEditedFoodName(e.target.value)} />
        <input type="number" value={editedCalories} onChange={(e) => setEditedCalories(e.target.value)} />
        <button onClick={() => onUpdate(meal.id)}>저장</button>
        <button onClick={onCancelEdit}>취소</button>
    </div>
);


function Dashboard() {
    const navigate = useNavigate();
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);
    // 날짜 관리를 위한 state 추가
    const [selectedDate, setSelectedDate] = useState(new Date());
    // 식단 관리를 위한 useState
    const [foodName, setFoodName] = useState('');
    const [calories, setCalories] = useState('');
    const [mealType, setMealType] = useState('lunch');
    const [editingMealId, setEditingMealId] = useState(null);
    const [editedFoodName, setEditedFoodName] = useState('');
    const [editedCalories, setEditedCalories] = useState('');

    const fetchDashboardData = async (date) => {
        setLoading(true);
        // Date 객체를 'YYYY-MM-DD' 형식의 문자열로 변환
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const dateString = `${year}-${month}-${day}`;

        try {
            const response = await apiFetch(`/api/dashboard?date=${dateString}`);
            if (response.ok) {
                setDashboardData(await response.json());
            } else {
                setDashboardData(null);
            }
        } catch (error) {
            console.error("Dashboard data fetch error:", error);
            setDashboardData(null);
        }
        setLoading(false);
    };

    useEffect(() => { 
        fetchDashboardData(selectedDate); 
    }, [selectedDate]);

    const handlePrevDay = () => {
        const newDate = new Date(selectedDate);
        newDate.setDate(selectedDate.getDate() - 1);
        setSelectedDate(newDate);
    };

    const handleNextDay = () => {
        const newDate = new Date(selectedDate);
        newDate.setDate(selectedDate.getDate() + 1);
        setSelectedDate(newDate);
    };    

    const handleLogout = () => { localStorage.removeItem('token'); navigate('/login'); };

    const handleMealSubmit = async (event) => {
        event.preventDefault();
        try {
            await apiFetch('/api/meals', {
                method: 'POST',
                body: JSON.stringify({ food_name: foodName, calories: parseInt(calories), meal_type: mealType })
            });
            setFoodName(''); setCalories('');
            fetchDashboardData();
        } catch (error) { console.error("Meal submit error:", error); alert('식단 기록에 실패했습니다.'); }
    };

    const handleDelete = async (mealId) => {
        if (window.confirm('정말로 이 항목을 삭제하시겠습니까?')) {
            try {
                await apiFetch(`/api/meals/${mealId}`, { method: 'DELETE' });
                fetchDashboardData();
            } catch (error) { console.error("Delete error:", error); alert('삭제에 실패했습니다.');}
        }
    };

    const handleEdit = (meal) => {
        setEditingMealId(meal.id);
        setEditedFoodName(meal.food_name);
        setEditedCalories(meal.calories);
    };
    
    const handleUpdate = async (mealId) => {
        try {
            await apiFetch(`/api/meals/${mealId}`, {
                method: 'PUT',
                body: JSON.stringify({ food_name: editedFoodName, calories: parseInt(editedCalories) })
            });
            setEditingMealId(null);
            fetchDashboardData();
        } catch (error) { console.error("Update error:", error); alert('수정에 실패했습니다.'); }
    };

    if (loading) return <div>로딩 중...</div>;
    if (!dashboardData) return <ProfileSetup onProfileUpdate={() => fetchDashboardData(selectedDate)} />;

    // ----- 여기가 핵심 수정 사항입니다 -----
    // dashboardData에서 값을 추출할 때, 혹시 값이 없을 경우를 대비해 기본값을 설정합니다.
    const { profile, recommended_calories, total_calories_today, bmr, bmi, meals_by_type = {} } = dashboardData;
    const { breakfast = [], lunch = [], dinner = [], snack = [] } = meals_by_type;
    const dateString = selectedDate.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' });

    return (
        // --- 여기가 수정되었습니다 ---
        <div className="dashboard-layout">
            {/* 왼쪽 컬럼 */}
            <div className="grid-column">
                <div className="container">
                    <div className="dashboard-header">
                        <button onClick={handlePrevDay}>&lt;</button>
                        <h1>{dateString}</h1>
                        <button onClick={handleNextDay}>&gt;</button>
                    </div>
                    <h2>{profile.name}님의 대시보드 ({profile.goal} 목표)</h2>
                    <p>기초대사량(BMR): <strong>{bmr} kcal</strong> </p>
                    <p>체질량지수(BMI): <strong>{bmi} ({dashboardData.bmi_category})</strong></p>
                    <p>섭취 칼로리: <strong>{total_calories_today} / {recommended_calories} kcal</strong></p>
                    <button onClick={handleLogout} className="logout-btn">로그아웃</button>
                </div>

                <div className="container">
                    <h3>식단 기록하기</h3>
                    <form onSubmit={handleMealSubmit}>
                        <div className="form-group"><label>식사 유형:</label><select value={mealType} onChange={e => setMealType(e.target.value)}><option value="breakfast">아침</option><option value="lunch">점심</option><option value="dinner">저녁</option><option value="snack">간식</option></select></div>
                        <div className="form-group"><label>음식 이름:</label><input type="text" value={foodName} onChange={e => setFoodName(e.target.value)} required /></div>
                        <div className="form-group"><label>칼로리 (kcal):</label><input type="number" value={calories} onChange={e => setCalories(e.target.value)} required /></div>
                        <button type="submit">기록하기</button>
                    </form>
                </div>
            </div>

            {/* 오른쪽 컬럼 */}
            <div className="meal-grid">
                <MealList title="아침 식사" meals={breakfast} onEdit={handleEdit} onDelete={handleDelete} onUpdate={handleUpdate} onCancelEdit={() => setEditingMealId(null)} editingMealId={editingMealId} editedFoodName={editedFoodName} setEditedFoodName={setEditedFoodName} editedCalories={editedCalories} setEditedCalories={setEditedCalories} />
                <MealList title="점심 식사" meals={lunch} onEdit={handleEdit} onDelete={handleDelete} onUpdate={handleUpdate} onCancelEdit={() => setEditingMealId(null)} editingMealId={editingMealId} editedFoodName={editedFoodName} setEditedFoodName={setEditedFoodName} editedCalories={editedCalories} setEditedCalories={setEditedCalories} />
                <MealList title="저녁 식사" meals={dinner} onEdit={handleEdit} onDelete={handleDelete} onUpdate={handleUpdate} onCancelEdit={() => setEditingMealId(null)} editingMealId={editingMealId} editedFoodName={editedFoodName} setEditedFoodName={setEditedFoodName} editedCalories={editedCalories} setEditedCalories={setEditedCalories} />
                <MealList title="간식" meals={snack} onEdit={handleEdit} onDelete={handleDelete} onUpdate={handleUpdate} onCancelEdit={() => setEditingMealId(null)} editingMealId={editingMealId} editedFoodName={editedFoodName} setEditedFoodName={setEditedFoodName} editedCalories={editedCalories} setEditedCalories={setEditedCalories} />
            </div>
        </div>
    );
}

export default Dashboard;