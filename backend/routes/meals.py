from flask import Blueprint, request, jsonify
import jwt
from .. import get_db_connection, app # DB 커넥션과 app 설정 가져오기
from ..decorators import token_required
from flask import g

meals_bp = Blueprint('meals_bp', __name__)

@meals_bp.route('/api/meals', methods=['POST'])
@token_required
def handle_meals_post():
    user_id = g.user_id
    conn = None
    try:
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

@meals_bp.route('/api/meals/<int:meal_id>', methods=['PUT', 'DELETE'])
@token_required
def handle_meal_item(meal_id):
    user_id = g.user_id
    conn = None
    try:
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