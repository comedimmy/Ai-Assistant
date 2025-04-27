from flask import Blueprint, send_from_directory, current_app, request, jsonify
import jwt
from Database.db2 import get_aquariums_by_user,get_user_by_id,save_user

api = Blueprint('api', __name__)

SECRET_KEY = 'very-fucking-secret-key'  # Secret key for signing JWT


# 查詢使用者資料 API
@api.route('/api/get_user_data', methods=['GET'])
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
        user_data = get_user_by_id(user_id) #user_id

        return jsonify({
            'user_data': user_data  
        }), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token 已過期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token 驗證失敗'}), 401

@api.route('/api/get_aquariums', methods=['POST'])
def get_aquariums():
    data = request.json
    #Json of Input
    #{
    #    user_id:"abc123"
    #}
    print('user id: ', data.get('user_id'))
    #接收參數為使用者ID, 根據使用者ID查詢並回傳水族箱名稱
    fake_data = {
        'aquariums':[
            {'name':'我的第一個水族箱','image_url':'/images/logo.png'},
            {'name':'海底世界','image_url':'/images/logo.png'}
        ]
    }
    return jsonify(fake_data)
    
@api.route('/api/get_aquariums_from_user', methods=['POST'])
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
        aquariums = get_aquariums_by_user('106706436733147855255') #user_id

        return jsonify({
            'aquariums': aquariums  
        }), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token 已過期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token 驗證失敗'}), 401


# 新增使用者資料API
@api.route("/api/save_user", methods=["POST"])
def save_user_api():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "缺少請求資料"}), 400

        user_id = data.get('user_id')
        nickname = data.get('nickname')
        login_type = data.get('login_type')

        if not user_id or not nickname or not login_type:
            return jsonify({"status": "error", "message": "缺少必要欄位"}), 400

        # 呼叫資料庫新增使用者
        save_user(user_id, nickname, login_type)

        return jsonify({
            "status": "success",
            "message": "User saved",
            "user_id": user_id
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"伺服器錯誤: {str(e)}"
        }), 500
    
@api.route('/api/test_database',methods=['GET'])
def api_test():
    return 'test_database'