import db

def get_user_by_id(user_id):
    """根據使用者id查詢使用者資料"""
    conn = db.get_connection()
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

def save_user_google(user_id,nickname, login_type="Google"):
    """將使用者資料儲存到資料庫，若使用者已存在則更新 Last_login"""
    conn = db.get_connection()
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


def update_user_name(user_id, new_name):
    """更新使用者名稱"""
    conn = db.get_connection()
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

