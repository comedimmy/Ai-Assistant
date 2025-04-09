from db import get_connection

def save_photo_url(aquarium_id, photo_url):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # 將圖片URL儲存到資料庫
        cursor.execute("""
            INSERT INTO photos (aquarium_id, path)
            VALUES (%s, %s)
        """, (aquarium_id, photo_url))
        conn.commit()

        print(f"Photo URL for aquarium_id {aquarium_id} saved successfully.")
    except Exception as e:
        print("Database error:", str(e))
    finally:
        cursor.close()
        conn.close()

# 查詢特定水族箱的所有照片
def get_photos_by_aquarium_id(aquarium_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)  # 讓查詢結果返回字典格式

    try:
        cursor.execute("SELECT path FROM photos WHERE aquarium_id = %s", (aquarium_id,))
        photos = cursor.fetchall()  # 取得所有符合條件的照片資料
        return photos
    except Exception as e:
        print("Database error:", str(e))
        return []
    finally:
        cursor.close()
        conn.close()
# 刪除照片
def delete_photo(aquarium_id, photo_path):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = "DELETE FROM aquarium_photos WHERE aquarium_id = %s AND path = %s"
        cursor.execute(query, (aquarium_id, photo_path))
        conn.commit()
        return cursor.rowcount > 0  # 若成功刪除，回傳 True
    except Exception as e:
        print("Database error:", str(e))
        return False
    finally:
        cursor.close()
        conn.close()


def get_fish_by_name(name):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM fishes WHERE name = %s", (name,))
    fish = cursor.fetchone()
    cursor.close()
    conn.close()
    return fish

def get_aquariums_by_user(user_id):
    conn = get_connection()
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

def update_aquarium_name(aquarium_id, new_name):
    conn = get_connection()
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

def add_aquarium(user_id, aquarium_name, fish_species, fish_amount, ai_model,min_temp,max_temp,feeding_frequency,feeding_amount):
    conn = get_connection()
    cursor = conn.cursor()        
    feed_time = feeding_frequency     
    try:
        # 產生唯一的水族箱 ID
        cursor.execute("SELECT UUID()")
        aquarium_id = cursor.fetchone()[0]
        # 時間 = 次數

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

def get_aquarium_by_id(aquarium_id):
    conn = get_connection()
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

def delete_aquarium(aquarium_id):
    conn = get_connection()
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

def update_aquarium_fields(aquarium_id, fields):
    if not fields:
        return False

    try:
        conn = get_connection()
        cursor = conn.cursor()

        
        set_clause = ", ".join(f"{key} = %s" for key in fields.keys())
        sql = f"UPDATE aquarium SET {set_clause} WHERE aquarium_id = %s"
        values = list(fields.values()) + [aquarium_id]

        cursor.execute(sql, values)
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"[更新失敗] {e}")
        return False
    finally:
        cursor.close()
        conn.close()
