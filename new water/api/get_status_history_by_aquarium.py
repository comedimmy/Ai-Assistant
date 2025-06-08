from flask import Blueprint,request,jsonify
import jwt
import Database.get_status_history_by_aquarium_id

api = Blueprint('api', __name__)

SECRET_KEY = 'very-secret-key'  # Secret key for signing JWT

# -------------------------------------------------------+
# 取得歷史紀錄API 
# input:1.jwt token 2.aquarium_id
# -------------------------------------------------------+
@api.route('/get_status_history_by_aquarium', methods=['POST'])
def get_status_history_by_aquarium():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '缺少或格式錯誤的 Authorization header'}), 401

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        if not payload.get("user_id"):
            return jsonify({'error': 'Token 無效'}), 403

        data = request.get_json()
        aquarium_id = data.get('aquarium_id')
        if not aquarium_id:
            return jsonify({'error': '缺少 aquarium_id'}), 400

        records = Database.get_status_history_by_aquarium_id.get_status_history_by_aquarium_id(aquarium_id)
        if records:
            return jsonify(records), 200
        else:
            return jsonify([]), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token 已過期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token 驗證失敗'}), 401
    

# ------------+
# row30
# ------------+

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

