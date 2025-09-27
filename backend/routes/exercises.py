from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import jwt
import bcrypt
from .. import get_db_connection, app # DB 커넥션과 app 설정 가져오기

exercises_bp = Blueprint('exercises_bp', __name__)

@exercises_bp.route('/api/exercises', methods=['GET'])
def recommend_exercises():
    auth_header = request.headers.get('Authorization')
    if not auth_header: return jsonify({'error': '토큰이 필요합니다'}), 403
    token = auth_header.split(' ')[1]
    conn = None
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT name, height, weight, goal, level FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            user = cursor.fetchone()
            if not user or not user['level']:
                return jsonify({'error': '프로필 정보(운동 수준)가 필요합니다.'}), 404
            
            height_m = float(user['height']) / 100
            bmi = float(user['weight']) / (height_m ** 2)
            goal = user['goal']
            level = user['level']
            
            params = [level]
            query = "SELECT id, name, description FROM exercises WHERE level = %s"
            reason = f"{user['name']}님은 '{level}' 수준에 맞춰 운동을 추천합니다."

            if goal == '다이어트':
                query += " AND type = 'cardio'"
                if bmi >= 25:
                    query += " AND impact = 'low'"
                    reason = f"현재 BMI({round(bmi,1)})를 고려하여, 관절에 부담이 적은 유산소 운동을 추천합니다."
            else:
                query += " AND type = 'strength'"
                reason = f"'{goal}' 목표 달성을 위해 근력 운동을 추천합니다."
            
            cursor.execute(query, tuple(params))
            exercises = cursor.fetchall()
        return jsonify({'recommendations': exercises, 'reason': reason}), 200
    except Exception as e:
        print(f"Error in recommend_exercises: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500
    finally:
        if conn:
            conn.close()