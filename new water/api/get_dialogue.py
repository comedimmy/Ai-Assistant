from flask import Blueprint,request,jsonify
import jwt
import Database.db2 

api = Blueprint('api', __name__)

SECRET_KEY = 'very-secret-key'  # Secret key for signing JWT


#------------------------------------------------------
# 取得指定水族箱所有的對話紀錄 
#------------------------------------------------------

@api.route("/get_dialogue/<aquarium_id>", methods=["GET"])
def get_dialogue(aquarium_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '缺少或格式錯誤的 Authorization header'}), 402

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if not user_id:
            return jsonify({'error': 'Token 無效，缺少 user_id'}), 403

        # 新增分頁參數
        offset = int(request.args.get('offset', 0))   # 預設從第0筆開始
        limit = int(request.args.get('limit', 20))    # 預設一次抓20筆

        records = Database.db2.get_dialogue_by_aquarium(aquarium_id, offset, limit)

        if not records:
            return jsonify({"message": "沒有更多對話紀錄"}), 404
        return jsonify(records), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token 已過期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token 驗證失敗'}), 401
'''
#------------------------------------------------------
# 取得聊天紀錄
#------------------------------------------------------
def get_dialogue_by_aquarium(aquarium_id: str, offset: int = 0, limit: int = 20) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
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
'''