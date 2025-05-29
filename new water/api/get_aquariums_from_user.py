from flask import Blueprint,request,jsonify
import jwt
import Database.db2 

api = Blueprint('api', __name__)

SECRET_KEY = 'very-secret-key'  # Secret key for signing JWT


#------------------------------------------------------
# 取得指定使用者綁定的所有水族箱
#------------------------------------------------------
@api.route('/get_aquariums_from_user', methods=['POST'])
def get_aquariums_from_user():
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
        aquariums = Database.db2.get_aquariums_by_user(user_id) #user_id

        return jsonify({
            'aquariums': aquariums  
        }), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token 已過期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token 驗證失敗'}), 401
    

'''
#------------------------------------------------------
# 所使用的函式 row 28
#------------------------------------------------------

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
'''