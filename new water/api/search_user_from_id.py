# +--------------------------------------------------------------------------+
#  蘇佑婷要的 檢查在資料庫當中是否有使用者的資料 有的話回傳true 沒有則回傳false
# +--------------------------------------------------------------------------+

from flask import Blueprint,request,jsonify
import jwt
import Database.db2 

api = Blueprint('api', __name__)

SECRET_KEY = 'very-secret-key'  # Secret key for signing JWT

@api.route('search_user_from_id', methods=['POST'])
def search_user_from_id():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '缺少或格式錯誤的 Authorization header'}), 401
    
    token = auth_header.split(' ')[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if not user_id:
            return jsonify({'exists': False}), 200

        # 查詢 user_id 是否存在
        user = Database.db2.get_user_by_id(user_id)

        if user:
            return jsonify({'exists': True}), 200
        else:
            return jsonify({'exists': False}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token 已過期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token 驗證失敗'}), 401
