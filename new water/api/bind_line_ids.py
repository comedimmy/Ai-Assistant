from flask import Blueprint,request,jsonify
import jwt
import Database.update_line_bot_id,insert_user_with_ids

api = Blueprint('api', __name__)

SECRET_KEY = 'very-secret-key'  # Secret key for signing JWT

# -------------------------------------------------------+
# 綁定line的官方帳號/登入ID API 
# input:1.line_login_id 2.line_bot_id
# -------------------------------------------------------+
@api.route('/bind_line_ids', methods=['POST'])
def bind_line_ids():
    try:
        data = request.get_json()
        line_login_id = data.get('line_login_id')
        line_bot_id = data.get('line_bot_id')

        if not line_login_id or not line_bot_id:
            return jsonify({'error': '缺少 line_login_id 或 line_bot_id'}), 400

        # 查詢是否已有此 user_id 的資料
        existing_user = Database.db2.get_user_by_id(line_login_id)

        if existing_user:
            success = Database.update_line_bot_id.update_line_bot_id(line_login_id, line_bot_id)
            if success:
                return jsonify({'message': '綁定成功 (已更新)'}), 200
            else:
                return jsonify({'error': '更新失敗'}), 500
        else:
            success = Database.insert_user_with_ids.insert_user_with_ids(line_login_id, line_bot_id)
            if success:
                return jsonify({'message': '綁定成功 (已新增)'}), 201
            else:
                return jsonify({'error': '新增失敗'}), 500

    except Exception as e:
        print("API error:", e)
        return jsonify({'error': '伺服器內部錯誤'}), 500

# -------------------------------------------------------+
# 如果已存在使用者(前端登入過)使用該函式進行"更新"
# -------------------------------------------------------+
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

# -------------------------------------------------------+
# 如果資料庫無該使用者(前端未登入)使用該函式進行"新增"
# -------------------------------------------------------+
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
