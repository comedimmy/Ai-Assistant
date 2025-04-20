import paho.mqtt.client as mqtt

mqtt_client = mqtt.Client()
mqtt_client.connect("localhost", 1883, 60)

def publish_command(aquarium_id):
    topic = f"aquarium/{aquarium_id}/feed"
    mqtt_client.publish(topic, "1")
