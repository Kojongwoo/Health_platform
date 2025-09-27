# backend/__init__.py
from flask import Flask
from flask_cors import CORS
import pymysql

# Flask 앱 생성 및 설정
app = Flask(__name__)
app.config['SECRET_KEY'] = 'jongheohuhwoojong_0312'
CORS(app)

# --- 데이터베이스 연결 설정 ---
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'Gjwhddn9493!'
DB_NAME = 'health_db'

def get_db_connection():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                           db=DB_NAME, charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

# --- Blueprint 등록 ---
# 아래에서 생성할 Blueprint들을 임포트하고 등록합니다.
from .routes.auth import auth_bp
from .routes.dashboard import dashboard_bp
from .routes.meals import meals_bp
from .routes.profile import profile_bp
from .routes.exercises import exercises_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(meals_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(exercises_bp)