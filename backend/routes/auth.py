from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import jwt
import bcrypt
from .. import get_db_connection, app # DB 커넥션과 app 설정 가져오기

# 'auth_bp' 라는 이름의 Blueprint 객체 생성
auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/api/register', methods=['POST'])
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

@auth_bp.route('/api/login', methods=['POST'])
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
