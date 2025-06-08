# db_tool.py
import os
import mysql.connector
from mysql.connector import pooling, Error
from typing import Optional
from datetime import datetime
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

def get_aquarium_by_id(aquarium_id: str) -> dict | None:
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT a.*, an.aquarium_name
            FROM Aquarium a
            LEFT JOIN aquriumname an
            ON a.aquarium_id = an.aquarium_id
            WHERE a.aquarium_id = %s
        """, (aquarium_id,))
        
        aquarium = cursor.fetchone()
        return aquarium
    except Exception as e:
        print("Database error:", str(e))
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

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


def update_user_profile(user_id, new_name=None, new_skin=None):
    """更新使用者名稱與 AI 機器人皮膚"""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        updates = []
        params = []

        if new_name:
            updates.append("nickname = %s")
            params.append(new_name)
        if new_skin is not None:
            updates.append("ai_bot_skin = %s")
            params.append(new_skin)

        if not updates:
            return False

        params.append(user_id)

        query = f"""
            UPDATE users
            SET {', '.join(updates)}
            WHERE user_id = %s
        """

        cursor.execute(query, tuple(params))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print("Database error:", str(e))
        return False
    finally:
        cursor.close()
        conn.close()


#------------------------------------------------------
# 儲存使用者
#------------------------------------------------------
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

# Database/db2.py

def update_line_bot_id(user_id: str, line_bot_id: str) -> bool:
    """更新已存在的使用者的 line_bot_id"""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET line_bot_id = %s WHERE user_id = %s",
            (line_bot_id, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print("[DB ERROR] 更新 line_bot_id 發生錯誤:", e)
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def insert_user_with_ids(user_id: str, line_bot_id: str) -> bool:
    """新增使用者資料"""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (user_id, line_bot_id, Login_type, Last_login)
            VALUES (%s, %s, 'Line', NOW())
            """,
            (user_id, line_bot_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print("[DB ERROR] 新增使用者失敗:", e)
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


#------------------------------------------------------
# 更新水族箱的所有設定(模擬新增)
#------------------------------------------------------
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

        # 更新 Aquarium 表並設為已激活
        cursor.execute("""
            UPDATE Aquarium
            SET fish_species = %s, fish_amount = %s, AI_model = %s,
                lowest_temperature = %s, highest_temperature = %s,
                feed_time = %s, feed_amount = %s, Last_update = NOW(),
                activated = TRUE
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

# 新增：檢查是否已激活

def is_aquarium_activated(aquarium_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT activated FROM Aquarium WHERE aquarium_id = %s", (aquarium_id,))
        row = cursor.fetchone()
        return row and bool(row[0])
    except Exception as e:
        print("[Check activated Error]:", str(e))
        return False
    finally:
        cursor.close()
        conn.close()

#------------------------------------------------------
# 以user_id為主與某個水族箱取消綁定
#------------------------------------------------------
def unbind_user_from_aquarium(user_id: str, aquarium_id: str) -> bool:
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

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

#------------------------------------------------------
# 新增：只做綁定，不修改設定
#------------------------------------------------------
def bind_user_to_aquarium(user_id: str, aquarium_id: str, aquarium_name: str) -> bool:
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO aquriumName (user_id, aquarium_id, aquarium_name)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE aquarium_name = VALUES(aquarium_name)
        """, (user_id, aquarium_id, aquarium_name))
        conn.commit()
        return True
    except Exception as e:
        print("[Bind User Error]:", str(e))
        return False
    finally:
        cursor.close()
        conn.close()



#------------------------------------------------------
# 若此aquarium_id綁定人數為0，則取消激活狀態
#------------------------------------------------------
def deactivate_aquarium_if_unbound(aquarium_id: str):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM aquriumName
            WHERE aquarium_id = %s
        """, (aquarium_id,))
        result = cursor.fetchone()

        if result and result[0] == 0:
            cursor.execute("""
                UPDATE Aquarium
                SET activated = FALSE
                WHERE aquarium_id = %s
            """, (aquarium_id,))
            conn.commit()
            return 1
    except Exception as e:
        print("[Deactivate aquarium error]:", str(e))
    finally:
        cursor.close()
        conn.close()


#------------------------------------------------------
# 取得聊天紀錄
#------------------------------------------------------
def get_dialogue_by_aquarium(aquarium_id: str, offset: int = 0, limit: int = 10) -> list[dict]:
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT question, response, transmit_time
            FROM dialogue
            WHERE aquarium_id = %s
            ORDER BY transmit_time ASC
            LIMIT %s OFFSET %s
        """, (aquarium_id, limit, offset))
        return cursor.fetchall()
    except Exception as e:
        print("[Get dialogue Error]:", str(e))
        return []
    finally:
        cursor.close()
        conn.close()

#------------------------------------------------------
# 新增與AI聊天的紀錄
#------------------------------------------------------
def insert_dialogue(aquarium_id: str, user_id: str, question: str, response: str) -> bool:
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dialogue (aquarium_id, user_id, question, response, transmit_time)
            VALUES (%s, %s, %s, %s, NOW())
        """, (aquarium_id, user_id, question, response))
        conn.commit()
        return True
    except Exception as e:
        print("[Insert dialogue Error]:", str(e))
        return False
    finally:
        cursor.close()
        conn.close()

#------------------------------------------------------
# 為了讓AI理解上下文 必須存取該水族箱的部分聊天紀錄
#------------------------------------------------------
def get_recent_questions(aquarium_id: str, limit: int = 5) -> list[str]:
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT question
            FROM dialogue
            WHERE aquarium_id = %s
            ORDER BY transmit_time DESC
            LIMIT %s
        """, (aquarium_id, limit))
        rows = cursor.fetchall()
        return [row[0] for row in reversed(rows)] if rows else []
    except Exception as e:
        print("[Get recent_questions Error]:", str(e))
        return []
    finally:
        cursor.close()
        conn.close()

#------------------------------------------------------
# 更新餵食時間紀錄
#------------------------------------------------------

def update_feeding_settings(aquarium_id: str, feed_amount: int, feed_time: str) -> bool:
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Aquarium
            SET feed_amount = %s,
                feed_time = %s,
                Last_update = NOW()
            WHERE aquarium_id = %s
        """, (feed_amount, feed_time, aquarium_id))

        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print("[Feeding Update Error]:", str(e))
        return False
    finally:
        cursor.close()
        conn.close()

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
        
# 新增事件紀錄函式

def insert_event_record(user_id: str, aquarium_id: str, status: bool, category: str, action: str) -> bool:
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO event_log (user_id, aquarium_id, status, category, action, timestamp)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (user_id, aquarium_id, status, category, action))
        conn.commit()
        return True
    except Exception as e:
        print("[Insert Event Error]:", str(e))
        return False
    finally:
        cursor.close()
        conn.close()


def get_activated_aquariums():
    conn = None
    cursor = None
    try:    
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT aquarium_id, highest_temperature, lowest_temperature, 
                   feed_amount, feed_time, activated
            FROM aquariums
            WHERE activated = 1
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def get_status_history_by_aquarium_id(aquarium_id: str) -> list[dict]:
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT record_id, aquarium_id, TDS, temperature, water_level, record_time
            FROM statushistory
            WHERE aquarium_id = %s
            ORDER BY record_time ASC
        """, (aquarium_id,))
        records = cursor.fetchall()
        return records
    except Exception as e:
        print("Database error:", e)
        return []
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_user_all_aquariums_recent_dialogues(user_id: str, limit: int = 3) -> list[str]:
    conn = None
    cursor = None
    try:    
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            WITH RankedDialogue AS (
                SELECT 
                    d.question,
                    d.aquarium_id,
                    aqn.aquarium_name,
                    ROW_NUMBER() OVER (
                        PARTITION BY d.aquarium_id 
                        ORDER BY d.transmit_time DESC
                    ) AS rn
                FROM dialogue d
                JOIN aquriumname aqn 
                    ON d.aquarium_id = aqn.aquarium_id 
                   AND d.user_id = aqn.user_id
                WHERE aqn.user_id = %s
            )
            SELECT question, aquarium_id, aquarium_name
            FROM RankedDialogue
            WHERE rn <= %s
            ORDER BY aquarium_id, rn
        """, (user_id, limit))

        rows = cursor.fetchall()

        if not rows:
            return []

        # 把每筆資料轉換成 "水族箱名稱：對話內容"
        result = [f"{row[2]}：{row[0]}" for row in rows]
        return result

    except Exception as e:
        print("[get_user_all_aquariums_recent_dialogues ERROR]", str(e))
        return []
    finally:
        cursor.close()
        conn.close()
        
def add_aquarium(user_id, aquarium_name, fish_species, fish_amount, ai_model, min_temp, max_temp, feeding_frequency, feeding_amount):
    conn = get_connection()
    cursor = conn.cursor()
    feed_time = feeding_frequency

    try:
        # 產生唯一的水族箱 ID（使用 MySQL 的 UUID()）
        cursor.execute("SELECT UUID()")
        aquarium_id = cursor.fetchone()[0]

        # 插入到 Aquarium 表
        cursor.execute("""
            INSERT INTO Aquarium (aquarium_id, fish_species, fish_amount, AI_model,
                                  lowest_temperature, highest_temperature, feed_time, feed_amount, Last_update)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (
            aquarium_id, fish_species, fish_amount, ai_model,
            min_temp, max_temp, feed_time, feeding_amount
        ))

        # 插入到 aquriumName 表
        cursor.execute("""
            INSERT INTO aquriumName (user_id, aquarium_id, aquarium_name)
            VALUES (%s, %s, %s)
        """, (user_id, aquarium_id, aquarium_name))

        conn.commit()
        return aquarium_id  
    except Exception as e:
        print("Database error:", str(e))
        conn.rollback()
        return None  
    finally:
        cursor.close()
        conn.close()