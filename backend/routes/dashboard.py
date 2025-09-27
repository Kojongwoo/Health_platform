from flask import Blueprint, request, jsonify
from datetime import datetime
import jwt
from .. import get_db_connection, app # DB 커넥션과 app 설정 가져오기

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    target_date_str = request.args.get('date', datetime.utcnow().strftime('%Y-%m-%d'))
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': '토큰이 필요합니다'}), 403
    
    token = auth_header.split(' ')[1]
    conn = None
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
        conn = get_db_connection()
        dashboard_data = {}

        with conn.cursor() as cursor:
            # 1. 사용자 프로필 정보 조회
            sql = "SELECT name, gender, height, weight, goal, age FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            profile = cursor.fetchone()
            if not profile or not profile.get('height'):
                return jsonify({'error': '프로필이 완성되지 않았습니다.'}), 404
            dashboard_data['profile'] = profile

            # 2. BMR, TDEE, 총 권장 칼로리 계산
            age, weight, height = profile['age'], float(profile['weight']), float(profile['height'])
            
            if profile['gender'] == 'male':
                bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
            else:
                bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
            
            tdee = bmr * 1.375
            goal = profile['goal']

            if goal == '다이어트': recommended_calories = tdee - 500
            elif goal == '근성장': recommended_calories = tdee + 300
            else: recommended_calories = tdee
            
            dashboard_data['recommended_calories'] = round(recommended_calories)
            dashboard_data['bmr'] = round(bmr)

            # 3. 권장 칼로리를 기반으로 권장 영양소(g) 계산 (핵심 수정 사항)
            if goal == '근성장': protein_ratio, fat_ratio = 0.30, 0.25
            elif goal == '다이어트': protein_ratio, fat_ratio = 0.35, 0.30
            else: protein_ratio, fat_ratio = 0.20, 0.25
            
            dashboard_data['recommended_macros'] = {
                'protein': round((recommended_calories * protein_ratio) / 4),
                'carbs': round((recommended_calories * (1 - protein_ratio - fat_ratio)) / 4),
                'fat': round((recommended_calories * fat_ratio) / 9)
            }

            # 4. BMI 계산
            height_m = height / 100
            bmi = weight / (height_m ** 2)
            if bmi < 18.5: bmi_category = '저체중'
            elif 18.5 <= bmi < 25: bmi_category = '정상'
            elif 25 <= bmi < 30: bmi_category = '과체중'
            else: bmi_category = '비만'
            dashboard_data['bmi'] = round(bmi, 2)
            dashboard_data['bmi_category'] = bmi_category

            # 5. 해당 날짜의 식단 기록 및 총 섭취 칼로리 계산
            sql = "SELECT id, food_name, calories, meal_type, created_at FROM meals WHERE user_id = %s AND DATE(created_at) = %s"
            cursor.execute(sql, (user_id, target_date_str))
            meals_today = cursor.fetchall()
            
            dashboard_data['total_calories_today'] = sum(m.get('calories', 0) for m in meals_today)
            
            meals_by_type = { 'breakfast': [], 'lunch': [], 'dinner': [], 'snack': [] }
            for meal in meals_today:
                meal['created_at'] = meal['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                if meal.get('meal_type') in meals_by_type:
                    meals_by_type[meal['meal_type']].append(meal)
            dashboard_data['meals_by_type'] = meals_by_type

        return jsonify(dashboard_data), 200
    except Exception as e:
        print(f"Error in get_dashboard_data: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500
    finally:
        if conn:
            conn.close()