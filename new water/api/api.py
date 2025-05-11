from flask import Blueprint, send_from_directory, current_app, request, jsonify
import jwt
import Database.db2 
from openai import OpenAI

api = Blueprint('api', __name__)

SECRET_KEY = 'very-fucking-secret-key'  # Secret key for signing JWT

client = OpenAI(api_key="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")

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
        user_data = Database.db2.get_user_by_id(user_id) #user_id

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
        aquariums = Database.db2.get_aquariums_by_user(user_id) #user_id

        return jsonify({
            'aquariums': aquariums  
        }), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token 已過期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token 驗證失敗'}), 401

'''
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
'''
# 向AI取得推薦的水族箱參數API
@api.route('/api/recommend_aquarium_settings', methods=['POST'])
def recommend_aquarium_settings():
    # 取得用戶傳來的資料
    data = request.get_json()
    fish_species = data.get('fish_species')
    fish_amount = data.get('fish_amount')
    
    # 確保有傳遞必要的參數
    if not fish_species or not fish_amount:
        return jsonify({"error": "缺少必要的參數"}), 400

    # 修改 prompt，使其要求返回簡潔的格式
    prompt = f"根據魚種「{fish_species}」和魚隻數量「{fish_amount}」，僅返回以下水族箱的設置參數，且不需要單位，格式為：\n" \
             "最低溫: XX\n" \
             "最高溫: XX\n" \
             "餵食間隔時間: XX:XX:XX\n" \
             "每次餵食的數量: X 克"

    try:

        # 向 OpenAI API 發送請求
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是水族箱設置專家。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7,
        )
        
        # 解析回傳的結果，並返回需要的參數
        response_text = response.choices[0].message.content.strip()

        # 打印回應結果，查看格式
        print(f"API 回應: {response_text}")

        # 解析簡潔的格式
        parameters = {}
        feeding_per_fish = None  # 每隻魚的餵食量

        for line in response_text.split("\n"):
            if "最低溫" in line:
                parameters["min_temp"] = line.split(":")[1].strip()
            elif "最高溫" in line:
                parameters["max_temp"] = line.split(":")[1].strip()
            elif "餵食間隔時間" in line:
                parameters["feeding_frequency"] = line.split(":")[1] + ":" + line.split(":")[2] + ":" + line.split(":")[3]
            elif "每次餵食的數量" in line:
                # 提取餵食量並移除單位
                feeding_amount_str = line.split(":")[1].strip()
                feeding_per_fish = float(''.join(filter(str.isdigit, feeding_amount_str)))  # 去除單位後轉換為浮點數
                parameters["feeding_amount"] = feeding_per_fish  # 設定每隻魚的餵食量

        # 根據魚隻數量計算總餵食量
        if feeding_per_fish is not None and fish_amount > 0:
            total_feeding_amount = feeding_per_fish * fish_amount
            parameters["feeding_amount"] = total_feeding_amount

        # 返回結果
        return jsonify(parameters)

    except Exception as e:
        # 回傳錯誤訊息
        return jsonify({"error": str(e)}), 500

# "激活"水族箱API
@api.route("/api/activate_aquarium/<aquarium_id>", methods=["POST"])
def activate_aquarium(aquarium_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '缺少或格式錯誤的 Authorization header'}), 402

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if not user_id:
            return jsonify({'error': 'Token 無效，缺少 user_id'}), 403

        data = request.get_json()
        aquarium_name = data.get("aquarium_name")
        fish_species = data.get("fish_species")
        fish_amount = data.get("fish_amount")
        ai_model = data.get("AI_model")
        min_temp = data.get("min_temp")
        max_temp = data.get("max_temp")
        feeding_frequency = data.get("feeding_frequency")
        feeding_amount = data.get("feeding_amount")

        success = Database.db2.update_aquarium(
            aquarium_id, user_id, aquarium_name, fish_species, fish_amount,
            ai_model, min_temp, max_temp, feeding_frequency, feeding_amount
        )

        if not success:
            return jsonify({"status": "error", "message": "激活失敗或資料無效"}), 500

        return jsonify({"status": "success", "message": "水族箱已成功激活"}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token 已過期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token 驗證失敗'}), 401

    
#解除綁定API
@api.route('/api/unbind_aquarium/<aquarium_id>', methods=['DELETE'])
def unbind_aquarium(aquarium_id):
	auth_header = request.headers.get('Authorization')
	if not auth_header or not auth_header.startswith('Bearer '):
		return jsonify({'error': '未授權'}), 401
	token = auth_header.split(" ")[1]

	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
		user_id = payload.get("user_id")
		if not user_id:
			return jsonify({'error': 'Token 無效'}), 403

		success = Database.db2.unbind_user_from_aquarium(user_id, aquarium_id)

		if success:
			return jsonify({'status': 'success', 'message': '已解除綁定'}), 200
		else:
			return jsonify({'status': 'error', 'message': '找不到綁定關係'}), 404
	except Exception as e:
		return jsonify({'error': str(e)}), 500

@api.route('/api/test_database',methods=['GET'])
def api_test():
    return 'test_database'