# db_tool.py
import os
import mysql.connector
from mysql.connector import pooling, Error
from typing import Optional

# -----------------------------------------------------------------------------
# 1) Configuration via environment variables (with sensible defaults)
# -----------------------------------------------------------------------------
DB_CONFIG = {
    'host':     '210.240.202.120', #os.getenv('DB_HOST',     'localhost'),
    'port':     3306, #int(os.getenv('DB_PORT',  '3306')),
    'user':     'comedimmy', #os.getenv('DB_USER',     'root'),
    'password': '11124235', #'os.getenv('DB_PASSWORD', ''),
    'database': 'ai_assistant', #os.getenv('DB_NAME',     'mydatabase'),
}

# -----------------------------------------------------------------------------
# 2) Initialize a connection pool so connections are reused under load
# -----------------------------------------------------------------------------
POOL = mysql.connector.pooling.MySQLConnectionPool(
    pool_name     = "mypool",
    pool_size     = 5, #int(os.getenv('DB_POOL_SIZE', '5')),
    **DB_CONFIG
)

def get_connection():
    """
    Grab a connection from the pool.
    Remember to .close() the connection when you’re done!
    """
    return POOL.get_connection()

# -----------------------------------------------------------------------------
# 3) Your helper function: get all aquariums for a given user_id
# -----------------------------------------------------------------------------
def get_aquariums_by_user(user_id: str) -> list[dict]:
    """
    Returns a list of dicts like [{'aquarium_id': ..., 'aquarium_name': ...}, ...].
    If there’s any error, logs it and returns an empty list.
    """
    conn = None
    cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT aquarium_id,
                   aquarium_name
            FROM aquriumName
            WHERE user_id = %s
        """, (user_id,))
        return cursor.fetchall()
    except Error as e:
        # You might prefer logging to a file or monitoring system
        print(f"[db_tool] MySQL error: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



def get_user_by_id(user_id: str) -> list[dict]:
    """根據使用者id查詢使用者資料，回傳 dict 或 None。"""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True) 
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()
        return user_data
    except Error as e:
        print(f"[db_tool] MySQL error: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def save_user(user_id,display_name, login_type="Line"):
    """將使用者資料儲存到資料庫，若使用者已存在則更新 Last_login"""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)  # 使用 dictionary 模式返回資料
        # 1. 先檢查使用者是否存在
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if user:
            # 2. 若使用者存在，則更新 Last_login
            cursor.execute("""
                UPDATE users 
                SET Last_login = NOW() 
                WHERE user_id = %s
            """, (user_id,))
            print(f"User {display_name} already exists, updated Last_login.")
        else:
            # 3. 若使用者不存在，則插入新資料
            cursor.execute("""
                INSERT INTO users (user_id,nickname, Login_type, Last_login)
                VALUES (%s,%s, %s,NOW())
            """, (user_id,display_name,  login_type))
            print(f"Inserted new user {display_name}.")

        conn.commit()
        return cursor.lastrowid  # 返回新插入或更新的使用者 ID
    except Exception as e:
        print("Database error:", str(e))
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def update_aquarium(
    aquarium_id: str,
    user_id: str,
    aquarium_name: str,
    fish_species: str,
    fish_amount: int,
    ai_model: str,
    min_temp: float,
    max_temp: float,
    feeding_frequency: str,
    feeding_amount: int
) -> bool:
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 更新 Aquarium 表
        cursor.execute("""
            UPDATE Aquarium
            SET fish_species = %s, fish_amount = %s, AI_model = %s,
                lowest_temperature = %s, highest_temperature = %s,
                feed_time = %s, feed_amount = %s, Last_update = NOW()
            WHERE aquarium_id = %s
        """, (
            fish_species, fish_amount, ai_model,
            min_temp, max_temp, feeding_frequency, feeding_amount,
            aquarium_id
        ))

        # 綁定使用者與名稱（如果未綁定再 insert）
        cursor.execute("""
            INSERT INTO aquriumName (user_id, aquarium_id, aquarium_name)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE aquarium_name = VALUES(aquarium_name)
        """, (user_id, aquarium_id, aquarium_name))

        conn.commit()
        return True
    except Exception as e:
        print("Database update error:", str(e))
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def unbind_user_from_aquarium(user_id: str, aquarium_id: str) -> bool:
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 僅刪除該使用者對此水族箱的綁定
        cursor.execute("""
            DELETE FROM aquriumName
            WHERE user_id = %s AND aquarium_id = %s
        """, (user_id, aquarium_id))

        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print("Database error:", str(e))
        return False
    finally:
        cursor.close()
        conn.close()