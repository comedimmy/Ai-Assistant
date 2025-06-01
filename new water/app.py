from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
'''
from routes.user_routes import user_bp
from routes.aqur_routes import aqur_bp
from routes.dialogue_routes import dialogue_bp


from config import Config 
'''
from api.auth import Line
from authlib.integrations.flask_client import OAuth
from api.web_change import web_bp
from api.api import api

app = Flask(__name__)
CORS(app)  # 允許跨來源請求
load_dotenv()  # 載入 .env 環境變數
'''
# 註冊藍圖 (Blueprint)
app.register_blueprint(user_bp)
app.register_blueprint(aqur_bp)
app.register_blueprint(dialogue_bp)

app.config.from_object(Config)
'''
app.register_blueprint(web_bp)
app.register_blueprint(api, url_prefix='/api')


oauth = OAuth(app)

app.register_blueprint(Line)
app.secret_key = 'very-secret-key'

if __name__ == '__main__':
    app.run(debug=True)

