from db import get_connection
from datetime import datetime

def get_all_active_tasks():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM tasks WHERE status = 'execution'")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def update_task_next_time(task_id, new_time):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE tasks SET next_exe_time = %s, last_update = %s WHERE task_id = %s",
            (new_time.strftime('%Y-%m-%d %H:%M:%S'), new_time.strftime('%Y-%m-%d %H:%M:%S'), task_id)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def insert_feeding_task(aquarium_id, topic, payload, name, next_time, interval_str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO tasks (
                task_name, mqtt_topic, instructions,
                daily, frequency, next_exe_time, status,
                create_time, last_update
            )
            VALUES (%s, %s, %s, %s, 'day', %s, 'execution', %s, %s)
        """, (
            name,
            topic,
            payload,
            interval_str,
            next_time.strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            None
        ))
        conn.commit()
        return True
    except Exception as e:
        print("[Task Insert Error]:", str(e))
        return False
    finally:
        cursor.close()
        conn.close()