from flask import Blueprint, send_from_directory, current_app, request, jsonify
import jwt
import Database.db2 
from openai import OpenAI
from datetime import datetime, timedelta
import MQTT.MQTT

api = Blueprint('api', __name__)

SECRET_KEY = 'very-secret-key'  # Secret key for signing JWT

client = OpenAI(api_key="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")

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

@api.route('/get_aquariums', methods=['POST'])
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

# ----------------------------------
# 你們要的查詢水族箱資訊API (蘇佑庭也要)
# ----------------------------------
@api.route('/get_aquarium_details/<aquarium_id>', methods=['GET'])
def aquarium_details(aquarium_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '缺少或格式錯誤的 Authorization header'}), 401

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if not user_id:
            return jsonify({'error': 'Token 無效，缺少 user_id'}), 401

        aquarium = Database.db2.get_aquarium_by_id(aquarium_id)
        if aquarium:
            return jsonify({
                'aquarium_id': aquarium['aquarium_id'],
                'fish_species': aquarium['fish_species'],
                'fish_amount': aquarium['fish_amount'],
                'feed_amount': aquarium['feed_amount'],
                'min_temp': aquarium['lowest_temperature'],
                'max_temp': aquarium['highest_temperature'],
                'last_update': aquarium['Last_update'],
                'light_status': aquarium['light_status'],
                'temperature': aquarium['temperature'],
                'water_level': aquarium['water_level'],
                'AI_model': aquarium['AI_model'],
                'QR_code': aquarium['QR_code'],
                'TDS': aquarium['TDS'],
            })
        else:
            return jsonify({'error': '水族箱資料未找到'}), 404

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token 已過期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token 驗證失敗'}), 401

# 向AI取得推薦的水族箱參數API
@api.route('/recommend_aquarium_settings', methods=['POST'])
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


# ------------------------------------------------------
# 以下兩個有根據老師說明做修改 需要改變使用者操作流程
# ------------------------------------------------------

# "激活"水族箱API 前身為add_aquarium
@api.route("/activate_aquarium/<aquarium_id>", methods=["POST"])
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

        # 如果已激活，只允許綁定使用者，不允許修改參數
        if Database.db2.is_aquarium_activated(aquarium_id):
            data = request.get_json()
            aquarium_name = data.get("aquarium_name")
            Database.db2.bind_user_to_aquarium(user_id, aquarium_id, aquarium_name)
            return jsonify({"status": "joined", "message": "此水族箱已被激活，已加入為共同管理者"}), 200

        # 取得設定資訊
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

        # 取得該水族箱的完整資料以便傳送給硬體
        aquarium = Database.db2.get_aquarium_by_id(aquarium_id)
        if aquarium:
            MQTT.MQTT.publish_aquarium_settings(aquarium)

        return jsonify({"status": "success", "message": "水族箱已成功激活並已通知硬體"}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token 已過期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token 驗證失敗'}), 401
    
    
# 解除綁定 API
@api.route('/unbind_aquarium/<aquarium_id>', methods=['DELETE'])
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
            # 若此 aquarium 綁定人數為 0，則取消激活狀態
            deactivated = Database.db2.deactivate_aquarium_if_unbound(aquarium_id)
            
            # 若成功取消激活，通知硬體
            if deactivated:
                MQTT.MQTT.publish_aquarium_deactivated(aquarium_id)

            return jsonify({'status': 'success', 'message': '已解除綁定'}), 200
        else:
            return jsonify({'status': 'error', 'message': '找不到綁定關係'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500



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
        limit = int(request.args.get('limit', 10))    # 預設一次抓10筆

        records = Database.db2.get_dialogue_by_aquarium(aquarium_id, offset, limit)

        if not records:
            return jsonify({"message": "沒有更多對話紀錄"}), 404
        return jsonify(records), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token 已過期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token 驗證失敗'}), 401


@api.route('/get_AI_dialogue_respown/<aquarium_id>', methods=['POST'])
def get_AI_dialogue_respown(aquarium_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '缺少或格式錯誤的 Authorization header'}), 402

    token = auth_header.split(' ')[1]
    data = request.get_json()
    user_input = data.get("messenge")

    if not user_input:
        return jsonify({"error": "請提供訊息內容"}), 400

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if not user_id:
            return jsonify({'error': 'Token 無效，缺少 user_id'}), 403

        # 取得該水族箱最近幾筆的使用者問題
        recent_questions = Database.db2.get_recent_questions(aquarium_id, limit=5)

        messages = [
            {"role": "system", "content": (
                "你是智慧水族箱的 AI 管家，"
                "專門協助使用者了解魚類的飼養、水質調整、溫度控制、"
                "餵食建議及疾病預防等資訊。請使用繁體中文、並盡量用簡短的幾句話說明，"
                "語氣親切簡潔，避免回答非魚類相關問題。"
                "請不要使用任何 Markdown 標記語法（例如 ** 粗體、_ 斜體、` 代碼等），僅使用純文字回答。"
            )}
        ]

        for q in recent_questions:
            messages.append({"role": "user", "content": q})

        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
        )

        gpt_reply = response.choices[0].message.content.strip()

        # 儲存進 dialogue_pairs
        Database.db2.insert_dialogue(aquarium_id, user_id, user_input, gpt_reply)

        return jsonify({"GPT_messenge": gpt_reply})

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token 已過期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token 驗證失敗'}), 401

# +--------------------------------------------------------------------------+
#  蘇佑婷要的 檢查在資料庫當中是否有使用者的資料 有的話回傳true 沒有則回傳false
# +--------------------------------------------------------------------------+
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
    

# 查詢餵食資料    
@api.route('/get_next_feeding_schedule/<aquarium_id>', methods=['GET'])
def get_next_feed_time(aquarium_id):

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '缺少或格式錯誤的 Authorization header'}), 402

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if not user_id:
            return jsonify({'error': 'Token 無效，缺少 user_id'}), 403
        
        aquarium = Database.db2.get_aquarium_by_id(aquarium_id)
        if not aquarium:
            return jsonify({"error": "查無此水族箱"}), 404
        
        feed_interval = aquarium['feed_time'] 
        last_update = aquarium['Last_update'] 
        feed_amount = aquarium['feed_amount']
        current_time = datetime.now()

        # 安全處理空值
        if not feed_interval or not last_update:
            return jsonify({"error": "feed_time 或 Last_update 為空"}), 400

        next_feed_time = last_update + feed_interval
        time_remaining = next_feed_time - current_time

        return jsonify({
            "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "last_update": last_update.strftime("%Y-%m-%d %H:%M:%S"),
            "feed_interval": str(feed_interval),
            "next_feed_time": next_feed_time.strftime("%Y-%m-%d %H:%M:%S"),
            "time_remaining": str(time_remaining).split('.')[0],
            "feed_amount": feed_amount,
            "should_feed_now": current_time >= next_feed_time
        })
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token 已過期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token 驗證失敗'}), 401

# 更新餵食設定 API 並記錄事件紀錄
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


@api.route('/aquarium/lights', methods=['POST'])
def control_light():
    data = request.get_json()
    state = data.get("state")

    if state not in ["on", "off"]:
        return jsonify({"error": "參數錯誤，需提供 'state': 'on' 或 'off'"}), 400

    try:
        MQTT.MQTT.publish_light_command(state)
        return jsonify({"message": f"已發送燈光控制指令：{state}"}), 200
    except Exception as e:
        return jsonify({"error": f"MQTT 發送失敗: {str(e)}"}), 500



@api.route('/test_database',methods=['GET'])
def api_test():
    return 'test_database'