// src/App.jsx
import { Routes, Route, Link } from 'react-router-dom';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import LandingPage from './pages/LandingPage'; // LandingPage import
import ProtectedRoute from './components/ProtectedRoute';
import ExercisePage from './pages/ExercisePage'; // ExercisePage import

function App() {
  const token = localStorage.getItem('token');

  return (
    <div>
      <nav>
        {token ? (
          // --- 여기가 수정되었습니다 ---
          <>
            <Link to="/dashboard">대시보드</Link> | <Link to="/exercises">운동 추천</Link>
          </>
        ) : (
          <>
            <Link to="/login">로그인</Link> | <Link to="/signup">회원가입</Link>
          </>
        )}
      </nav>
      <Routes>
        {/* 이제 메인 경로는 누구나 접근 가능한 LandingPage 입니다 */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/exercises" element={<ProtectedRoute><ExercisePage /></ProtectedRoute>} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* Dashboard는 /dashboard 경로에서만 접근 가능하며, 보호됩니다 */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  );
}

export default App;