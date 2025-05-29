from flask import Blueprint,request,jsonify
import jwt
import Database.db2 

api = Blueprint('api', __name__)

SECRET_KEY = 'very-secret-key'  # Secret key for signing JWT

# 查詢使用者資料 API
@api.route('/get_user_data', methods=['GET'])
def get_user_data():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '缺少或格式錯誤的 Authorization header'}), 401
    
    token = auth_header.split(' ')[1]


    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if not user_id:
            return jsonify({'error': 'Token 無效，缺少 user_id'}), 401

        # 查詢該 user 所擁有的水族箱
        user_data = Database.db2.get_user_by_id(user_id) #user_id

        return jsonify({
            'user_data': user_data  
        }), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token 已過期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token 驗證失敗'}), 401
    
'''
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
'''