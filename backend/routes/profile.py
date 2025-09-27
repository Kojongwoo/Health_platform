from flask import Blueprint, request, jsonify
import jwt
from .. import get_db_connection, app # DB 커넥션과 app 설정 가져오기

profile_bp = Blueprint('profile_bp', __name__)

@profile_bp.route('/api/profile', methods=['GET', 'POST'])
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