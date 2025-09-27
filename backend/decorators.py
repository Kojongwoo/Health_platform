# backend/decorators.py
from functools import wraps
from flask import request, jsonify, g
import jwt
from . import app # __init__.py의 app 객체를 가져옵니다.

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': '토큰이 필요합니다'}), 403

        try:
            # 'Bearer ' 부분을 제거하고 실제 토큰만 추출합니다.
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            
            # g 객체에 user_id를 저장하여 라우트 함수에서 사용할 수 있게 합니다.
            g.user_id = payload['user_id']

        except jwt.ExpiredSignatureError:
            return jsonify({'error': '토큰이 만료되었습니다.'}), 401
        except (jwt.InvalidTokenError, IndexError):
            return jsonify({'error': '유효하지 않은 토큰입니다.'}), 401

        return f(*args, **kwargs)
    return decorated_function