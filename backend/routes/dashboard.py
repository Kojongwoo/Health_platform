# backend/routes/dashboard.py
from flask import Blueprint, request, jsonify, g
from datetime import datetime
from .. import get_db_connection
from ..decorators import token_required
# 우리가 만든 서비스 함수들을 가져옵니다.
from ..services import health_service 

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/api/dashboard', methods=['GET'])
@token_required
def get_dashboard_data():
    target_date_str = request.args.get('date', datetime.utcnow().strftime('%Y-%m-%d'))
    user_id = g.user_id

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 1. 사용자 프로필 정보 조회
            sql = "SELECT name, gender, height, weight, goal, age FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            profile = cursor.fetchone()

            if not profile or not profile.get('height'):
                return jsonify({'error': '프로필이 완성되지 않았습니다.'}), 404

            # 2. 서비스 함수를 사용하여 건강 지표 계산
            bmr = health_service.calculate_bmr(profile['gender'], float(profile['weight']), float(profile['height']), profile['age'])
            tdee = health_service.calculate_tdee(bmr)
            recommended_calories = health_service.calculate_recommended_calories(tdee, profile['goal'])
            bmi, bmi_category = health_service.calculate_bmi(float(profile['weight']), float(profile['height']))
            recommended_macros = health_service.calculate_recommended_macros(recommended_calories, profile['goal'])

            # 3. 해당 날짜의 식단 기록 조회
            sql = "SELECT id, food_name, calories, meal_type FROM meals WHERE user_id = %s AND DATE(created_at) = %s"
            cursor.execute(sql, (user_id, target_date_str))
            meals_today = cursor.fetchall()

            total_calories_today = sum(m.get('calories', 0) for m in meals_today)
            
            meals_by_type = { 'breakfast': [], 'lunch': [], 'dinner': [], 'snack': [] }
            for meal in meals_today:
                if meal.get('meal_type') in meals_by_type:
                    meals_by_type[meal['meal_type']].append(meal)

            # 4. 최종 대시보드 데이터 구성
            dashboard_data = {
                'profile': profile,
                'bmr': round(bmr),
                'recommended_calories': round(recommended_calories),
                'bmi': bmi,
                'bmi_category': bmi_category,
                'recommended_macros': recommended_macros,
                'total_calories_today': total_calories_today,
                'meals_by_type': meals_by_type
            }

        return jsonify(dashboard_data), 200
    except Exception as e:
        print(f"Error in get_dashboard_data: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500
    finally:
        if conn:
            conn.close()