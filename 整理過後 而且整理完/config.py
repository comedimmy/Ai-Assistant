import os

class Config:
    # Flask 設定
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-key")

    # Google OAuth 設定
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

    # MQTT 設定
    MQTT_BROKER_URL = os.environ.get("MQTT_BROKER_URL", "localhost")
    MQTT_BROKER_PORT = int(os.environ.get("MQTT_BROKER_PORT", 1883))
