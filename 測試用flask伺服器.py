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
from app import auth_bp  # 匯入處理 OAuth 的藍圖

# 設定路徑
os.chdir("f:/water")


app = Flask(__name__)
app.secret_key = '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'
app.register_blueprint(auth_bp, url_prefix='/auth')

openai.api_key = "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"

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



@app.route("/")
def index():
    return render_template("index.html")  # index.html

@app.route("/login-page")
def login_page():
    return render_template("login.html")  # login.html

@app.route("/back")
def back():
    return render_template("index.html")  # login.html


if __name__ == '__main__':
    app.run(debug=True)
