from flask import Blueprint,request,jsonify
import jwt
import Database.db2 

api = Blueprint('api', __name__)

SECRET_KEY = 'very-secret-key'  # Secret key for signing JWT

#------------------------------------------------------
# 更新餵食設定 API 並記錄事件紀錄
#------------------------------------------------------

@api.route("/update_feeding_schedule", methods=["POST"])
def update_feeding_schedule():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '缺少或格式錯誤的 Authorization header'}), 401

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get("user_id")
        if not user_id:
            return jsonify({'error': 'Token 無效'}), 403

        data = request.get_json()
        aquarium_id = data.get("aquarium_id")
        feed_amount = data.get("feed_amount")
        feed_time = data.get("feed_time")

        if not aquarium_id or feed_amount is None or not feed_time:
            return jsonify({'error': '缺少必要參數'}), 400

        success = Database.db2.update_feeding_settings(aquarium_id, feed_amount, feed_time)

        # 新增事件紀錄
        event_status = True if success else False
        Database.db2.insert_event_record(
            user_id=user_id,
            aquarium_id=aquarium_id,
            status=event_status,
            category="餵食",
            action="更改餵食數量"
        )

        if success:
            return jsonify({'status': 'success', 'message': '餵食設定已更新'}), 200
        else:
            return jsonify({'status': 'error', 'message': '更新失敗'}), 500

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token 已過期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token 驗證失敗'}), 401

'''
#------------------------------------------------------
# 更新餵食時間紀錄 row 34
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

#------------------------------------------------------
# 新增事件紀錄函式 row 38
#------------------------------------------------------

def insert_event_record(user_id: str, aquarium_id: str, status: bool, category: str, action: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
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
'''