from db import get_connection

def get_fish_by_name(name):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM fishes WHERE name = %s", (name,))
    fish = cursor.fetchone()
    cursor.close()
    conn.close()
    return fish