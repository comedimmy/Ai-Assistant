import paho.mqtt.publish as publish
import json
from datetime import  timedelta

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_lights = "aquarium/lights/control"
MQTT_TOPIC_feed = "aquarium/feed/control"

def publish_light_command(state: str):
    if state not in ["on", "off"]:
        raise ValueError("狀態只能是 'on' 或 'off'")
    
    payload = json.dumps({"state": state})
    publish.single(MQTT_TOPIC_lights, payload=payload, hostname=MQTT_BROKER, port=MQTT_PORT, qos=2)

def publish_activated_aquarium_ids(aquariums):
    activated_ids = [aq['aquarium_id'] for aq in aquariums if aq['activated'] == 1]

    payload = json.dumps({"activated_ids": activated_ids})
    publish.single(MQTT_TOPIC_feed, payload=payload, hostname=MQTT_BROKER, port=MQTT_PORT, qos=2)

def publish_aquarium_settings(aquarium):
    def format_timedelta(value):
        if isinstance(value, timedelta):
            return str(value)  # 或 value.strftime('%H:%M:%S') 如果你要更格式化
        return value

    payload = json.dumps({
        "aquarium_id": aquarium["aquarium_id"],
        "highest_temperature": aquarium["highest_temperature"],
        "lowest_temperature": aquarium["lowest_temperature"],
        "feed_amount": aquarium["feed_amount"],
        "feed_time": format_timedelta(aquarium["feed_time"]),
        "activated": aquarium["activated"]
    })

    topic = f"aquarium/settings/response/{aquarium['aquarium_id']}"
    publish.single(topic, payload=payload, hostname=MQTT_BROKER, port=MQTT_PORT, qos=2)

def publish_aquarium_deactivated(aquarium_id):
    topic = f"aquarium/deactivated/{aquarium_id}"
    payload = json.dumps({
        "aquarium_id": aquarium_id,
        "deactivated": True
    })
    publish.single(topic, payload=payload, hostname=MQTT_BROKER, port=MQTT_PORT, qos=2)