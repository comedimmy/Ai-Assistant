import paho.mqtt.client as mqtt

# ====== MQTT 參數設定 ======
BROKER = "localhost"
PORT = 1883
TOPICS = [
    "aquarium/activated/request",
    "aquarium/init/request/+",
    "device/+/control/+",
    "sensors/+/report/+",
    "ai/tasks/request/+",
    "ai/evaluation/request/+",
    "alerts/environment/+",
    "alerts/device/+",
]

# ====== 接收訊息時觸發的處理邏輯 ======
def on_message(client, userdata, msg):
    print(f"[收到訊息] Topic: {msg.topic}, Payload: {msg.payload.decode()}")

    # 根據 topic 製作對應的 response topic
    if msg.topic.startswith("aquarium/activated/request"):
        response_topic = "aquarium/activated/response"
    elif msg.topic.startswith("aquarium/init/request/"):
        aquarium_id = msg.topic.split("/")[-1]
        response_topic = f"aquarium/init/response/{aquarium_id}"
    elif msg.topic.startswith("ai/tasks/request/"):
        aquarium_id = msg.topic.split("/")[-1]
        response_topic = f"ai/tasks/response/{aquarium_id}"
    elif msg.topic.startswith("ai/evaluation/request/"):
        aquarium_id = msg.topic.split("/")[-1]
        response_topic = f"ai/evaluation/response/{aquarium_id}"
    else:
        # 其他不屬於需要回傳的 topic 就略過
        return

    # 模擬一個通用的回應訊息
    reply = f"你好，你有連接上 {msg.topic} 了，該 topic 沒問題。"
    client.publish(response_topic, reply)
    print(f"[發送回應] → {response_topic} : {reply}")

# ====== 建立 MQTT 客戶端並連接 ======
client = mqtt.Client()
client.on_message = on_message

client.connect(BROKER, PORT, 60)

# ====== 訂閱所有測試主題 ======
for topic in TOPICS:
    client.subscribe(topic)
    print(f"[訂閱中] {topic}")

# ====== 進入監聽迴圈 ======
print("✅ MQTT 測試監聽啟動中...")
client.loop_forever()
