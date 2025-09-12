from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import jwt
from flask_cors import CORS
import pymysql
import bcrypt # 비밀번호 암호화를 위해 추가

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jongheohuhwoojong_0312'
CORS(app) # 모든 경로에 대해 CORS 허용

# --- 데이터베이스 연결 설정 ---
# 본인의 MySQL 설정에 맞게 수정하세요.
DB_HOST = 'localhost'
DB_USER = 'root' # 본인 DB의 user
DB_PASSWORD = 'Gjwhddn9493!' # 본인 DB의 password
DB_NAME = 'health_db'

def get_db_connection():
    """데이터베이스 커넥션을 생성하고 반환하는 함수"""
    return pymysql.connect(host=DB_HOST,
                           user=DB_USER,
                           password=DB_PASSWORD,
                           db=DB_NAME,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

# --- API 엔드포인트 정의 ---
@app.route('/')
def home():
    return "AI 맞춤형 건강 관리 플랫폼 백엔드 서버"

@app.route('/api/register', methods=['POST'])
def register():
    """회원가입 API"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not email or not password or not name:
        return jsonify({'error': '모든 필드를 입력해주세요'}), 400

    # 비밀번호 암호화
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 이메일 중복 체크
            sql_check = "SELECT * FROM users WHERE email = %s"
            cursor.execute(sql_check, (email,))
            if cursor.fetchone():
                return jsonify({'error': '이미 존재하는 이메일입니다.'}), 409
            
            # 사용자 정보 삽입
            sql_insert = "INSERT INTO users (email, password, name) VALUES (%s, %s, %s)"
            cursor.execute(sql_insert, (email, hashed_password, name))
        conn.commit()
    finally:
        conn.close()

    return jsonify({'message': '회원가입이 성공적으로 완료되었습니다.'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    """로그인 API"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': '이메일과 비밀번호를 모두 입력해주세요'}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 사용자가 존재하는지 확인
            sql = "SELECT * FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()

            if not user:
                return jsonify({'error': '존재하지 않는 이메일입니다.'}), 404

            # 비밀번호가 일치하는지 확인
            if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                # 비밀번호 일치 -> JWT 생성
                token = jwt.encode({
                    'user_id': user['id'],
                    'exp': datetime.utcnow() + timedelta(hours=1) # 토큰 유효기간 1시간
                }, app.config['SECRET_KEY'], algorithm='HS256')

                return jsonify({'message': '로그인 성공!', 'token': token}), 200
            else:
                return jsonify({'error': '비밀번호가 일치하지 않습니다.'}), 401
    finally:
        conn.close()

# backend/app.py

# backend/app.py

@app.route('/api/meals', methods=['GET', 'POST'])
def handle_meals():
    # 요청 헤더에서 토큰 가져오기
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': '토큰이 필요합니다'}), 403

    token = auth_header.split(' ')[1]

    try:
        # 토큰을 디코딩하여 사용자 정보 확인
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']

        conn = get_db_connection()

        # GET 요청 처리 (식단 목록 조회)
        if request.method == 'GET':
            with conn.cursor() as cursor:
                sql = "SELECT food_name, calories, created_at FROM meals WHERE user_id = %s ORDER BY created_at DESC"
                cursor.execute(sql, (user_id,))
                meals = cursor.fetchall()
                # 날짜/시간 객체를 문자열로 변환 (JSON 호환)
                for meal in meals:
                    meal['created_at'] = meal['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            return jsonify(meals), 200

        # POST 요청 처리 (식단 기록 추가)
        elif request.method == 'POST':
            data = request.get_json()
            food_name = data.get('food_name')
            calories = data.get('calories')

            with conn.cursor() as cursor:
                sql = "INSERT INTO meals (user_id, food_name, calories) VALUES (%s, %s, %s)"
                cursor.execute(sql, (user_id, food_name, calories))
            conn.commit()
            return jsonify({'message': '식단이 성공적으로 기록되었습니다.'}), 201

    except jwt.ExpiredSignatureError:
        return jsonify({'error': '토큰이 만료되었습니다.'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': '유효하지 않은 토큰입니다.'}), 401
    finally:
        if conn:
            conn.close()

@app.route('/api/profile', methods=['GET', 'POST'])
def handle_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': '토큰이 필요합니다'}), 403

    token = auth_header.split(' ')[1]

    conn = None # <-- conn 변수를 여기서 None으로 미리 초기화합니다.
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
        conn = get_db_connection() # <-- 여기서 실제 DB 연결 객체가 할당됩니다.

        # GET 요청: 현재 프로필 정보 조회
        if request.method == 'GET':
            # (기존 코드와 동일)
            with conn.cursor() as cursor:
                sql = "SELECT gender, height, weight, goal FROM users WHERE id = %s"
                cursor.execute(sql, (user_id,))
                profile = cursor.fetchone()
            return jsonify(profile), 200

        # POST 요청: 프로필 정보 업데이트
        elif request.method == 'POST':
            # (기존 코드와 동일)
            data = request.get_json()
            gender = data.get('gender')
            height = data.get('height')
            weight = data.get('weight')
            goal = data.get('goal')
            age = data.get('age')

            with conn.cursor() as cursor:
                sql = """
                    UPDATE users 
                    SET gender = %s, height = %s, weight = %s, goal = %s, age = %s
                    WHERE id = %s
                """
                cursor.execute(sql, (gender, height, weight, goal, age, user_id))
            conn.commit()
            return jsonify({'message': '프로필이 성공적으로 업데이트되었습니다.'}), 200

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        return jsonify({'error': str(e)}), 401
    finally:
        # conn이 성공적으로 연결되었을 때만 close()를 호출합니다.
        if conn:
            conn.close()

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
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
            # 1. 사용자 프로필 정보 가져오기
            sql = "SELECT name, gender, height, weight, goal, age FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            profile = cursor.fetchone()
            if not profile or not profile['height']:
                return jsonify({'error': '프로필이 완성되지 않았습니다.'}), 404
            dashboard_data['profile'] = profile

            # 2. 일일 권장 칼로리 계산
            # BMR 계산 
            age = profile['age']
            weight = float(profile['weight'])
            height = float(profile['height'])

            if profile['gender'] == 'male':
                bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
            else: # female
                bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

            # TDEE (활동대사량) 계산, 활동 수준은 1.375(가벼운 활동)으로 고정
            # tdee = bmr * 1.375

            # --- BMI 계산 추가 ---
            height_in_meters = height / 100
            bmi = weight / (height_in_meters ** 2)

            # --- 응답 데이터에 bmr, bmi 추가 ---
            dashboard_data['bmr'] = round(bmr)
            dashboard_data['bmi'] = round(bmi, 2)

            goal = profile['goal']
            if goal == '다이어트':
                recommended_calories = bmr - 300 # 유지 칼로리에서 500kcal 감량
            elif goal == '근성장':
                recommended_calories = bmr + 300 # 유지 칼로리에서 300kcal 증량
            else: # 건강유지
                recommended_calories = bmr
            dashboard_data['recommended_calories'] = round(recommended_calories)

            # 3. 오늘 섭취한 총 칼로리 및 식단 목록 가져오기
            sql = "SELECT id, food_name, calories, created_at FROM meals WHERE user_id = %s AND DATE(created_at) = CURDATE() ORDER BY created_at DESC"
            cursor.execute(sql, (user_id,))
            meals_today = cursor.fetchall()

            total_calories_today = sum(meal['calories'] for meal in meals_today)

            for meal in meals_today:
                meal['created_at'] = meal['created_at'].strftime('%Y-%m-%d %H:%M:%S')

            dashboard_data['meals_today'] = meals_today
            dashboard_data['total_calories_today'] = total_calories_today

        return jsonify(dashboard_data), 200

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        return jsonify({'error': str(e)}), 401
    finally:
        if conn:
            conn.close()

@app.route('/api/meals/<int:meal_id>', methods=['PUT', 'DELETE'])
def handle_meal_item(meal_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': '토큰이 필요합니다'}), 403

    token = auth_header.split(' ')[1]
    conn = None
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
        conn = get_db_connection()

        with conn.cursor() as cursor:
            # 중요: 수정/삭제하려는 항목이 현재 로그인한 사용자의 것인지 확인 (보안)
            sql = "SELECT user_id FROM meals WHERE id = %s"
            cursor.execute(sql, (meal_id,))
            meal = cursor.fetchone()
            if not meal or meal['user_id'] != user_id:
                return jsonify({'error': '권한이 없습니다.'}), 403

            # PUT 요청 처리 (수정)
            if request.method == 'PUT':
                data = request.get_json()
                food_name = data.get('food_name')
                calories = data.get('calories')
                sql = "UPDATE meals SET food_name = %s, calories = %s WHERE id = %s"
                cursor.execute(sql, (food_name, calories, meal_id))
                conn.commit()
                return jsonify({'message': '항목이 성공적으로 수정되었습니다.'}), 200

            # DELETE 요청 처리 (삭제)
            elif request.method == 'DELETE':
                sql = "DELETE FROM meals WHERE id = %s"
                cursor.execute(sql, (meal_id,))
                conn.commit()
                return jsonify({'message': '항목이 성공적으로 삭제되었습니다.'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# --- 서버 실행 ---
if __name__ == '__main__':
    app.run(debug=True)