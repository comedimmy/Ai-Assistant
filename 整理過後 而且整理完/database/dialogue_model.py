from db import get_connection
from datetime import datetime

def insert_dialogue(aquarium_id, content, sender):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO dialogue (aquarium_id, content, transmit_time, sender)
            VALUES (%s, %s, %s, %s)
        """, (aquarium_id, content, datetime.now(), sender))
        conn.commit()
        return True
    except Exception as e:
        print("[Dialogue Insert Error]:", str(e))
        return False
    finally:
        cursor.close()
        conn.close()

def get_dialogue_by_aquarium(aquarium_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT content, sender, transmit_time
            FROM dialogue
            WHERE aquarium_id = %s
            ORDER BY transmit_time DESC
        """, (aquarium_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()