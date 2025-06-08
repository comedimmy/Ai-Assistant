from mysql.connector import pooling, Error
# ----------------------------+
# row30
# ----------------------------+
def get_task_by_aquarium_id(aquarium_id: str) -> dict | None:
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ai_tasks WHERE aquarium_id = %s", (aquarium_id,))
        return cursor.fetchone()
    except Exception as e:
        print("Database error:", e)
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
        