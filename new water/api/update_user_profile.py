from flask import Blueprint,request,jsonify
import jwt
import Database.db2 

api = Blueprint('api', __name__)

SECRET_KEY = 'very-secret-key'  # Secret key for signing JWT

@api.route('/update_user_profile', methods=['POST'])
def update_user_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '缺少或格式錯誤的 Authorization header'}), 401

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if not user_id:
            return jsonify({'error': 'Token 無效，缺少 user_id'}), 401

        data = request.json
        new_name = data.get("new_name")
        new_skin = data.get("ai_bot_skin")

        if not new_name and new_skin is None:
            return jsonify({'error': '請提供新的名稱或 AI 機器人種類'}), 400

        success = Database.db2.update_user_profile(user_id, new_name, new_skin)

        if success:
            return jsonify({'status': 'success', 'message': '使用者資料已更新'}), 200
        else:
            return jsonify({'status': 'error', 'message': '更新失敗'}), 500

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token 已過期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token 驗證失敗'}), 401