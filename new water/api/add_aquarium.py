from flask import Blueprint, request, jsonify
import jwt
import Database.add_aquarium.add_aquarium
import paho.mqtt.client as mqtt
import json

api = Blueprint('api', __name__)
SECRET_KEY = 'very-secret-key'  # Secret key for signing JWT

# MQTT broker 設定
MQTT_BROKER = "localhost"
MQTT_PORT = 1883


#----------------------------------------------------------------------------------------------+
# 新增水族箱api 更新內容:增加MQTT傳送邏輯,將資訊另外存入AI待管事項表中
#----------------------------------------------------------------------------------------------+
@api.route("/api/add_aquarium", methods=["POST"])
def add_aquarium_page():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '缺少或格式錯誤的 Authorization header'}), 401

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get("user_id")
        if not user_id:
            return jsonify({'error': 'Token 無效'}), 403

        data = request.get_json()
        aquarium_name = data.get("aquarium_name")
        fish_species = data.get("fish_species")
        fish_amount = data.get("fish_amount")
        ai_model = data.get("AI_model")
        min_temp = data.get("min_temp")
        max_temp = data.get("max_temp")
        feeding_frequency = data.get("feeding_frequency")
        feeding_amount = data.get("feeding_amount")

        # 新增至資料庫
        aquarium_id = Database.add_aquarium.add_aquarium(
            user_id, aquarium_name, fish_species, fish_amount, ai_model,
            min_temp, max_temp, feeding_frequency, feeding_amount
        )

        if not aquarium_id:
            return jsonify({"status": "error", "message": "新增水族箱失敗"}), 500

        # MQTT 發送
        mqtt_payload = {
            "aquarium_id": aquarium_id,
            "aquarium_name": aquarium_name,
            "fish_species": fish_species,
            "fish_amount": fish_amount,
            "AI_model": ai_model,
            "min_temp": min_temp,
            "max_temp": max_temp,
            "feeding_frequency": feeding_frequency,
            "feeding_amount": feeding_amount
        }
        publish_aquarium_details_to_mqtt(aquarium_id, mqtt_payload)

        return jsonify({"status": "success", "message": "水族箱已新增並排程餵食！"}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token 已過期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token 驗證失敗'}), 401

#----------------------------------------------------------------------------------------------+
# 新增至MQTT.MQTT資料夾當中 row62
#----------------------------------------------------------------------------------------------+
def publish_aquarium_details_to_mqtt(aquarium_id, payload):
    topic = f"aquariumDetails/{aquarium_id}"
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.publish(topic, json.dumps(payload))
    client.disconnect()
    print(f"[已發送MQTT] → {topic} : {payload}")


def add_aquarium(user_id, aquarium_name, fish_species, fish_amount, ai_model, min_temp, max_temp, feeding_frequency, feeding_amount):
    conn = get_connection()
    cursor = conn.cursor()
    feed_time = feeding_frequency

    try:
        # 產生唯一的水族箱 ID（使用 MySQL 的 UUID()）
        cursor.execute("SELECT UUID()")
        aquarium_id = cursor.fetchone()[0]

        # 插入到 Aquarium 表
        cursor.execute("""
            INSERT INTO Aquarium (aquarium_id, fish_species, fish_amount, AI_model,
                                  lowest_temperature, highest_temperature, feed_time, feed_amount, Last_update)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (
            aquarium_id, fish_species, fish_amount, ai_model,
            min_temp, max_temp, feed_time, feeding_amount
        ))

        # 插入到 aquriumName 表
        cursor.execute("""
            INSERT INTO aquriumName (user_id, aquarium_id, aquarium_name)
            VALUES (%s, %s, %s)
        """, (user_id, aquarium_id, aquarium_name))

        conn.commit()
        return aquarium_id  
    except Exception as e:
        print("Database error:", str(e))
        conn.rollback()
        return None  
    finally:
        cursor.close()
        conn.close()