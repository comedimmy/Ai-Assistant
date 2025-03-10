from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
from flask_cors import CORS  # 允許跨來源請求 (讓前端可以存取 Flask API)
from flask import Flask, request, jsonify
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import os
import random
import openai
import paho.mqtt.client as mqtt
from flask import Flask, redirect, url_for, session,render_template
from authlib.integrations.flask_client import OAuth
from datetime import timedelta

# dotenv setup
from dotenv import load_dotenv

load_dotenv()
# 設定路徑
os.chdir("f:/water")

# App config
app = Flask(__name__)
# Session config
app.secret_key = os.getenv("APP_SECRET_KEY")
app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
openai.api_key = os.getenv("OPENAI_API_KEY")
# oAuth Setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)





# 載入主模型和分詞器（用於判斷是否是餵魚）
main_model_path = "./my_model"  # 這是主模型的路徑
main_tokenizer = BertTokenizer.from_pretrained(main_model_path)
main_model = BertForSequenceClassification.from_pretrained(main_model_path)
main_model.eval()  # 設置為評估模式

# 載入副模型和分詞器（用於判斷餵魚的完整性）
feedjudge_model_path = "./feedjudgeAI_model"  # 這是副模型的路徑
feedjudge_tokenizer = BertTokenizer.from_pretrained(feedjudge_model_path)
feedjudge_model = BertForSequenceClassification.from_pretrained(feedjudge_model_path)
feedjudge_model.eval()  # 設置為評估模式

# 主模型的類別對應
main_labels = {
        0: "正在為您開燈...",
        1: "正在為您關燈...",
        2: "水溫查詢中...請稍後",
        3: "餵魚",
        4: "正在開啟水族箱風扇",
        5: "正在為您測得pH值...",
        6: "此功能未實裝",
        7: "魚類知識"
    }

# 副模型的類別對應
feedjudge_labels = {
    0: "無時間與數量",
    1: "缺少數量",
    2: "缺少時間",
    3: "完整訊息"
}

def call_chatgpt_api(input_text, filename="chatgpt_responses.txt"):
    try:
        # 在每次請求的句子後加上 "盡量簡短的說明就好"
        modified_input = input_text + " 盡量簡短的說明並以繁體中文回答"
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": modified_input}]
        )            
        # 將結果寫入文件
        answer = response["choices"][0]["message"]["content"]
        with open(filename, "a", encoding="utf-8") as file:
            file.write(f"問題: {input_text}\n回答: {answer}\n{'='*50}\n")
        return answer
    except Exception as e:
        print(f"OpenAI API Error: {str(e)}")  # 在伺服器端顯示錯誤
        return "抱歉，我暫時無法回答這個問題。"  # 確保不回傳 None

# 判斷是否是「餵魚」相關的動作
def classify_main_model(input_text):
    inputs = main_tokenizer(input_text, return_tensors="pt", padding=True, truncation=True, max_length=128)
    outputs = main_model(**inputs)
    predicted_class = torch.argmax(outputs.logits).item()
    return main_labels[predicted_class]

# 判斷餵魚是否包含完整的時間與數量
def classify_feed_info(input_text):
    inputs = feedjudge_tokenizer(input_text, return_tensors="pt", padding=True, truncation=True, max_length=128)
    outputs = feedjudge_model(**inputs)
    predicted_class = torch.argmax(outputs.logits).item()
    return feedjudge_labels[predicted_class]

# 讀取error_responses.txt的內容
def load_error_responses(filename="error_responses.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            responses = [line.strip() for line in file if line.strip()]  # 去除空行
        return responses
    except FileNotFoundError:
        return ["抱歉，這個功能還未實裝，你打錯字了嗎？"]  # 預設回應
    
error_responses = load_error_responses()

# 獲取隨機回應
def get_random_error_response():
    return random.choice(error_responses)

CORS(app)  # 避免 CORS 問題，允許前端存取

# MQTT 設定
MQTT_BROKER = "localhost"  # 如果 MQTT Broker 在本機，使用 localhost
MQTT_PORT = 1883
MQTT_TOPIC = "test/MQTT"

# 初始化 MQTT 客戶端
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

@app.route('/send-mqtt', methods=['POST'])
def send_mqtt():
    try:
        # 取得前端發送的 JSON 資料
        data = request.json  
        print("收到前端資料:", data)

        # 將 JSON 轉成 MQTT 訊息
        mqtt_payload = str(data)  # 轉換成字串格式
        mqtt_client.publish(MQTT_TOPIC, mqtt_payload)

        return jsonify({"message": "MQTT 訊息已發送", "sent_data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


MQTT_TOPIC_light ="aqar/light"
MQTT_TOPIC_fan ="aqar/fan"
MQTT_TOPIC_temperature ="aqar/sensor/water_temperature"
MQTT_TOPIC_feeder="aqar/fish_feeder"

# 定義接收 POST 請求的URL
@app.route('/receive', methods=['POST'])
def receive_data():
    # 獲取從 PHP 發送過來的資料
    input_text = request.json.get("message")

    # 判斷是否為「餵魚」相關的動作
    main_result = classify_main_model(input_text)

    # 如果是餵魚，則進一步判斷餵魚的時間與數量是否完整
    if main_result == "餵魚":
        feed_result = classify_feed_info(input_text)
        
        if feed_result == "缺少時間":
            return jsonify({"result": "請問您要設置餵食的時間嗎？"})
        elif feed_result == "缺少數量":
            return jsonify({"result": "請問您要餵食多少數量呢？"})
        elif feed_result == "無時間與數量":
            return jsonify({"result": "無時間與數量"})
        elif feed_result == "完整訊息":
            return jsonify({
                "result": "餵魚動作已完成，時間和數量都已設置",
            })
    
    if main_result == "此功能未實裝":
        return jsonify({
        "result": get_random_error_response(),
        })
    
    if main_result =="魚類知識":
         return jsonify({
        "result": call_chatgpt_api(input_text),
        })

    # 如果不是餵魚相關的動作，直接回應主模型的結果
    return jsonify({
        "result": main_result,
    })




@app.route('/')
def index():
    if 'profile' in session:
        # 使用者已登入，將資料傳給前端
        user_info = session['profile']
        return render_template('index.html', user_info=user_info)
    else:
        # 使用者未登入，顯示登入/註冊選項
        return render_template('index.html', user_info=None)

def hello_world():
    email = dict(session)['profile']['email']
    return f'Hello, you are logge in as {email}!'

@app.route("/login-page")
def login_page():
    return render_template("login.html")  # login.html

@app.route("/back")
def back():
    return render_template("index.html")  # index.html

@app.route('/login')
def login():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')  # create the google oauth client
    token = google.authorize_access_token()  # Access token from google (needed to get user info)
    resp = google.get('userinfo')  # userinfo contains stuff u specificed in the scrope
    user_info = resp.json()
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from google
    session['profile'] = user_info
    session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed
    return redirect('/')

@app.route('/profile')
def profile():
    if 'profile' in session:  # 如果 session 中有 'profile' 資料，代表使用者已登入
        user_info = session['profile']
        return jsonify(user_info)  # 返回使用者資料
    else:
        # 如果沒有登入，返回錯誤訊息
        return jsonify({"error": "User not logged in"}), 401

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
