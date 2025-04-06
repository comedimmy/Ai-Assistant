import mysql.connector
from config import Config

def get_connection():
    return mysql.connector.connect(**Config.DB_CONFIG)