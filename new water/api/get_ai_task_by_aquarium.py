from flask import Blueprint,request,jsonify
import jwt
import Database.get_task_by_aquarium_id

api = Blueprint('api', __name__)

SECRET_KEY = 'very-secret-key'  # Secret key for signing JWT

# -------------------------------------------------------+
# 取得AI待辦事項API 
# input:1.jwt token 2.aquarium_id
# -------------------------------------------------------+
@api.route('/get_ai_task_by_aquarium', methods=['POST'])
def get_ai_task_by_aquarium():
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
        aquarium_id = data.get('aquarium_id')
        if not aquarium_id:
            return jsonify({'error': '缺少 aquarium_id'}), 400

        task = Database.get_task_by_aquarium_id.get_task_by_aquarium_id(aquarium_id)
        if task:
                task_result = {
                    "task_id": task["task_id"],
                    "user_id": task["user_id"],
                    "aquarium_id": task["aquarium_id"],
                    "feed_amount": task["feed_amount"],
                    "feed_time": str(task["feed_time"]),
                    "highest_temperature": task["highest_temperature"],
                    "lowest_temperature": task["lowest_temperature"],
                    "light_on_time": str(task["light_on_time"]),
                    "light_off_time": str(task["light_off_time"]),
                    "water_level_threshold": task["water_level_threshold"],
                }

                return jsonify(task_result), 200
        else:
            return jsonify({'error': '查無此水族箱任務'}), 404

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token 已過期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token 驗證失敗'}), 401

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
        