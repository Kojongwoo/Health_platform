from flask import Blueprint, request, jsonify
from .. import get_db_connection, app # DB 커넥션과 app 설정 가져오기
from ..decorators import token_required
from flask import g

profile_bp = Blueprint('profile_bp', __name__)

@profile_bp.route('/api/profile', methods=['GET', 'POST'])
@token_required
def handle_profile():

    user_id = g.user_id

    conn = None
    try:
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