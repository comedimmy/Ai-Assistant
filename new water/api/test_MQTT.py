import paho.mqtt.client as mqtt
import json

# ====== MQTT 參數設定 ======
BROKER = "localhost"
PORT = 1883

# ====== 硬體傳給伺服器的 Topic（伺服器訂閱） ======
SUBSCRIBE_TOPICS = [
    "AITasks/request/+",
    "sensorsReport/+",
    "deviceStatus/+"
]

# ====== MQTT 訊息處理函式 ======
def on_message(client, userdata, msg):
    print(f"[收到訊息] Topic: {msg.topic}, Payload: {msg.payload.decode()}")

    aquarium_id = msg.topic.split("/")[-1]

    # AI 任務請求處理
    if msg.topic.startswith("AITasks/request/"):
        response_topic = f"AITasks/response/{aquarium_id}"
        reply = f"這是 {aquarium_id} 的 AI 任務回應。"
        client.publish(response_topic, reply)
        print(f"[已回應 AI 任務] → {response_topic} : {reply}")

    # 感測器數據處理
    elif msg.topic.startswith("sensorsReport/"):
        try:
            data = json.loads(msg.payload.decode())
            tds = data.get("TDS", "未知")
            temp = data.get("temperature", "未知")
            level = data.get("water_level", "未知")

            reply = f"TDS為{tds}，溫度{temp}攝氏度，水位為{level}公分"
            response_topic = f"sensorsReport/{aquarium_id}"
            client.publish(response_topic, reply)
            print(f"[已回應感測資訊] → {response_topic} : {reply}")
        except json.JSONDecodeError:
            print("❌ 感測器資料不是有效的 JSON")

    # 設備狀態處理
       # 設備狀態處理
    elif msg.topic.startswith("deviceStatus/"):
        try:
            data = json.loads(msg.payload.decode())
            tds = "開啟" if data.get("TDS") == "1" else "關閉"
            temp = "開啟" if data.get("temperature") == "1" else "關閉"
            level = "開啟" if data.get("water_level") == "1" else "關閉"
            light = "開啟" if data.get("light_status") == "1" else "關閉"

            reply = f"TDS感測器：{tds}，溫度感測器：{temp}，水位感測器：{level}，燈狀態：{light}"
            response_topic = f"deviceStatus/{aquarium_id}"
            client.publish(response_topic, reply)
            print(f"[已回應設備狀態] → {response_topic} : {reply}")
        except json.JSONDecodeError:
            print("❌ 設備狀態資料不是有效的 JSON")

# ====== MQTT 客戶端初始化與啟動 ======
client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT, 60)

# ====== 訂閱所有必要 topic ======
for topic in SUBSCRIBE_TOPICS:
    client.subscribe(topic)
    print(f"[訂閱中] {topic}")

print("✅ MQTT 測試伺服器已啟動，等待訊息中...")
client.loop_forever()
