import mysql.connector
from datetime import datetime, timedelta


def get_db_connection():
    db_config = {
        "host": "210.240.202.120",
        "user": "comedimmy",
        "password": "11124235",
        "database": "ai_assistant"
    }
    return mysql.connector.connect(**db_config)

def save_user_google(user_id,nickname, login_type="Google"):
    """將使用者資料儲存到資料庫，若使用者已存在則更新 Last_login"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
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
            print(f"User {nickname} already exists, updated Last_login.")
        else:
            # 3. 若使用者不存在，則插入新資料
            cursor.execute("""
                INSERT INTO users (user_id,nickname, Login_type, Last_login)
                VALUES (%s,%s, %s,NOW())
            """, (user_id,nickname,  login_type))
            print(f"Inserted new user {nickname}.")

        conn.commit()
        return cursor.lastrowid  # 返回新插入或更新的使用者 ID
    except Exception as e:
        print("Database error:", str(e))
        return None
    finally:
        cursor.close()
        conn.close()

def get_user_by_id(user_id):
    """根據使用者id查詢使用者資料"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # 使用 dictionary 模式返回資料

    try:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()
        return user_data
    except Exception as e:
        print("Database error:", str(e))
        return None
    finally:
        cursor.close()
        conn.close()

def update_user_name(user_id, new_name):
    """更新使用者名稱"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 更新名稱
        cursor.execute("""
            UPDATE users 
            SET nickname = %s 
            WHERE user_id = %s
        """, (new_name, user_id))
        
        conn.commit()
        return cursor.rowcount > 0  # 若更新成功則回傳 True
    except Exception as e:
        print("Database error:", str(e))
        return False
    finally:
        cursor.close()
        conn.close()

def save_photo_url(aquarium_id, photo_url):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 將圖片URL儲存到資料庫
        cursor.execute("""
            INSERT INTO photo (AquariumID, URL)
            VALUES (%s, %s)
        """, (aquarium_id, photo_url))
        conn.commit()

        print(f"Photo URL for AquariumID {aquarium_id} saved successfully.")
    except Exception as e:
        print("Database error:", str(e))
    finally:
        cursor.close()
        conn.close()

# 查詢特定水族箱的所有照片
def get_photos_by_aquarium_id(aquarium_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # 讓查詢結果返回字典格式

    try:
        cursor.execute("SELECT PhotoID, URL, LogTime FROM photo WHERE AquariumID = %s", (aquarium_id,))
        photos = cursor.fetchall()  # 取得所有符合條件的照片資料
        return photos
    except Exception as e:
        print("Database error:", str(e))
        return []
    finally:
        cursor.close()
        conn.close()

# 刪除照片
def delete_photo(photo_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM photo WHERE PhotoID = %s", (photo_id,))
        conn.commit()
        return cursor.rowcount > 0  # 若成功刪除，回傳 True
    except Exception as e:
        print("Database error:", str(e))
        return False
    finally:
        cursor.close()
        conn.close()

def add_aquarium(user_id, aquarium_name, fish_species, fish_amount, ai_model,min_temp,max_temp,feeding_frequency,feeding_amount):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 獲取當前的日期和時間
    current_time = datetime.now()
    # 取得當前時間
    current_time = datetime.now()

    # 計算每次餵食的時間間隔
    feeding_frequency = int(feeding_frequency)  # 確保是整數
    hours_between_feedings = 24 / feeding_frequency  # 餵食的間隔時間（小時）

    # 取得下一次餵食時間
    next_feed_time = current_time + timedelta(hours=hours_between_feedings)

    # 確保只保留時、分、秒（忽略日期）
    feed_time = next_feed_time.time().strftime("%H:%M:%S")

    print("最終存入資料庫的餵食時間:", feed_time)       
    try:
        # 產生唯一的水族箱 ID
        cursor.execute("SELECT UUID()")
        aquarium_id = cursor.fetchone()[0]
        # 時間 = 次數
        feed_time = feeding_frequency 
        # 插入到 Aquarium 表
        cursor.execute("""
            INSERT INTO Aquarium (aquarium_id, fish_species, fish_amount, AI_model,lowest_temperature,highest_temperature,feed_time,feed_amount, Last_update)
            VALUES (%s, %s, %s, %s,%s, %s, %s, %s, NOW())
        """, (aquarium_id, fish_species, fish_amount, ai_model,min_temp,max_temp, feed_time,feeding_amount))
        
        # 插入到 aquriumName 表
        cursor.execute("""
            INSERT INTO aquriumName (user_id, aquarium_id, aquarium_name)
            VALUES (%s, %s, %s)
        """, (user_id, aquarium_id, aquarium_name))
        
        conn.commit()
        return True
    except Exception as e:
        print("Database error:", str(e))
        return False
    finally:
        cursor.close()
        conn.close()

def update_aquarium_name(aquarium_id, new_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE aquriumName
            SET aquarium_name = %s
            WHERE aquarium_id = %s
        """, (new_name, aquarium_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print("Database error:", str(e))
        return False
    finally:
        cursor.close()
        conn.close()

def delete_aquarium(aquarium_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 刪除水族箱名稱
        cursor.execute("DELETE FROM aquriumName WHERE aquarium_id = %s", (aquarium_id,))
        # 刪除水族箱的資料
        cursor.execute("DELETE FROM Aquarium WHERE aquarium_id = %s", (aquarium_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print("Database error:", str(e))
        return False
    finally:
        cursor.close()
        conn.close()

def get_aquariums_by_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # 使用字典方式返回結果，方便 JSON 化

    try:
        cursor.execute("""
            SELECT a.aquarium_id, a.highest_temperature, a.lowest_temperature, a.fish_species, a.fish_amount,
                   a.feed_amount, a.feed_time, a.water_level, a.AI_model, a.light_status, a.TDS, a.temperature,
                   a.QR_code, a.Last_update, n.aquarium_name
            FROM Aquarium a
            JOIN aquriumName n ON a.aquarium_id = n.aquarium_id
            WHERE n.user_id = %s
        """, (user_id,))
        
        aquariums = cursor.fetchall()
        return aquariums
    except Exception as e:
        print("Database error:", str(e))
        return []
    finally:
        cursor.close()
        conn.close()

def get_aquarium_by_id(aquarium_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # 使用字典方式返回結果，方便 JSON 化
    try:
        cursor.execute("""
            SELECT * FROM Aquarium where aquarium_id=%s
        """, (aquarium_id,))
        
        aquariums = cursor.fetchone()
        return aquariums
    except Exception as e:
        print("Database error:", str(e))
        return []
    finally:
        cursor.close()
        conn.close()
