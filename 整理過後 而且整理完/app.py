from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from routes.auth_routes import create_auth_blueprint
from routes.user_routes import user_bp
from routes.aqur_routes import aqur_bp
from routes.dialogue_routes import dialogue_bp
from routes.web_change import web_bp
from authlib.integrations.flask_client import OAuth
from config import Config
from scheduler import task_scheduler  

app = Flask(__name__)
CORS(app)  # 允許跨來源請求
load_dotenv()  # 載入 .env 環境變數

# 註冊藍圖 (Blueprint)
app.register_blueprint(user_bp)
app.register_blueprint(aqur_bp)
app.register_blueprint(dialogue_bp)
app.register_blueprint(web_bp)
app.config.from_object(Config)

oauth = OAuth(app)

auth_bp = create_auth_blueprint(oauth)
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app.run(debug=True)