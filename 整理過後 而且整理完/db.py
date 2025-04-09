import mysql.connector
from config import Config

def get_connection():
    db_config = {
        "host": "210.240.202.120",
        "user": "comedimmy",
        "password": "11124235",
        "database": "ai_assistant"
    }
    return mysql.connector.connect(**db_config)
