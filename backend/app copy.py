from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import jwt
from flask_cors import CORS
import pymysql
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jongheohuhwoojong_0312' # 실제 배포 시에는 더 복잡한 키로 변경하세요.
CORS(app)

# --- 데이터베이스 연결 설정 ---
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'Gjwhddn9493!' # 본인의 MySQL 비밀번호로 수정하세요.
DB_NAME = 'health_db'

def get_db_connection():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                           db=DB_NAME, charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

# --- API 엔드포인트 ---

@app.route('/api/dashboard', methods=['GET'])
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

# --- 이하 다른 함수들은 수정 없이 그대로 유지됩니다 ---

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    if not email or not password or not name:
        return jsonify({'error': '모든 필드를 입력해주세요'}), 400
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql_check = "SELECT * FROM users WHERE email = %s"
            cursor.execute(sql_check, (email,))
            if cursor.fetchone():
                return jsonify({'error': '이미 존재하는 이메일입니다.'}), 409
            sql_insert = "INSERT INTO users (email, password, name) VALUES (%s, %s, %s)"
            cursor.execute(sql_insert, (email, hashed_password, name))
        conn.commit()
    finally:
        conn.close()
    return jsonify({'message': '회원가입이 성공적으로 완료되었습니다.'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': '이메일과 비밀번호를 모두 입력해주세요'}), 400
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()
            if not user:
                return jsonify({'error': '존재하지 않는 이메일입니다.'}), 404
            if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                token = jwt.encode({
                    'user_id': user['id'],
                    'exp': datetime.utcnow() + timedelta(hours=1)
                }, app.config['SECRET_KEY'], algorithm='HS256')
                return jsonify({'message': '로그인 성공!', 'token': token}), 200
            else:
                return jsonify({'error': '비밀번호가 일치하지 않습니다.'}), 401
    finally:
        conn.close()

@app.route('/api/profile', methods=['GET', 'POST'])
def handle_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': '토큰이 필요합니다'}), 403
    token = auth_header.split(' ')[1]
    conn = None
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
        conn = get_db_connection()
        if request.method == 'GET':
            with conn.cursor() as cursor:
                sql = "SELECT gender, height, weight, goal, age, level FROM users WHERE id = %s"
                cursor.execute(sql, (user_id,))
                profile = cursor.fetchone()
            return jsonify(profile), 200
        elif request.method == 'POST':
            data = request.get_json()
            with conn.cursor() as cursor:
                sql = """
                    UPDATE users 
                    SET gender = %s, height = %s, weight = %s, goal = %s, age = %s, level = %s
                    WHERE id = %s
                """
                cursor.execute(sql, (data.get('gender'), data.get('height'), data.get('weight'), data.get('goal'), data.get('age'), data.get('level'), user_id))
            conn.commit()
            return jsonify({'message': '프로필이 성공적으로 업데이트되었습니다.'}), 200
    except Exception as e:
        print(f"Error in handle_profile: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/meals', methods=['POST'])
def handle_meals_post():
    auth_header = request.headers.get('Authorization')
    if not auth_header: return jsonify({'error': '토큰이 필요합니다'}), 403
    token = auth_header.split(' ')[1]
    conn = None
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
        conn = get_db_connection()
        data = request.get_json()
        sql = """
            INSERT INTO meals (user_id, food_name, calories, meal_type, created_at) 
            VALUES (%s, %s, %s, %s, %s)
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, (user_id, data.get('food_name'), data.get('calories'), 
                                data.get('meal_type'), data.get('date')))
        conn.commit()
        return jsonify({'message': '식단이 성공적으로 기록되었습니다.'}), 201
    except Exception as e:
        print(f"Error in handle_meals_post: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/meals/<int:meal_id>', methods=['PUT', 'DELETE'])
def handle_meal_item(meal_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header: return jsonify({'error': '토큰이 필요합니다'}), 403
    token = auth_header.split(' ')[1]
    conn = None
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT user_id FROM meals WHERE id = %s"
            cursor.execute(sql, (meal_id,))
            meal = cursor.fetchone()
            if not meal or meal['user_id'] != user_id:
                return jsonify({'error': '권한이 없습니다.'}), 403
            if request.method == 'PUT':
                data = request.get_json()
                sql = "UPDATE meals SET food_name = %s, calories = %s WHERE id = %s"
                cursor.execute(sql, (data.get('food_name'), data.get('calories'), meal_id))
                conn.commit()
                return jsonify({'message': '항목이 성공적으로 수정되었습니다.'}), 200
            elif request.method == 'DELETE':
                sql = "DELETE FROM meals WHERE id = %s"
                cursor.execute(sql, (meal_id,))
                conn.commit()
                return jsonify({'message': '항목이 성공적으로 삭제되었습니다.'}), 200
    except Exception as e:
        print(f"Error in handle_meal_item: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/exercises', methods=['GET'])
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

if __name__ == '__main__':
    app.run(debug=True)
