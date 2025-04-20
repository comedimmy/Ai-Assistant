from flask import Blueprint,jsonify,request,session,redirect,render_template,url_for
import database.aquarium_model
from dotenv import load_dotenv
import openai
import os
import base64
from datetime import datetime, timedelta
from services.mqtt_service import publish_command
import database.task_model

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

aqur_bp = Blueprint('aqur',__name__)


@aqur_bp.route('/api/save_snapshot/<aquarium_id>', methods=['POST'])
def save_snapshot(aquarium_id):
    # 從請求中獲取圖片數據
    data = request.get_json()
    image_data = data.get('image')
    # 去除圖片數據中的 "data:image/png;base64," 部分
    image_data = image_data.split(',')[1]

    # 解碼 base64 圖片
    image_bytes = base64.b64decode(image_data)

    # 生成時間戳，讓每個圖片名稱都唯一
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # 格式: YYYYMMDD_HHMMSS
    image_filename = f'snapshot_{timestamp}.png'
    image_path = os.path.join('static', 'snapshots', image_filename)
    
    # 確保目錄存在
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    
    # 儲存圖片到伺服器
    with open(image_path, 'wb') as f:
        f.write(image_bytes)

    # 儲存圖片URL到資料庫
    photo_url = f"{image_path}"  # 生成圖片的URL
    database.aquarium_model.save_photo_url(aquarium_id, photo_url)  # 呼叫資料庫函式

    return jsonify({'message': '圖片儲存成功', 'image_path': image_path})

# 取得照片API
@aqur_bp.route('/api/get_photos/<aquarium_id>', methods=['GET'])
def get_photos(aquarium_id):
    if not aquarium_id:
        return jsonify({"error": "請提供 AquariumID"}), 400

    photos = database.aquarium_model.get_photos_by_aquarium_id(aquarium_id)
    if photos:
        return jsonify(photos)  # 以 JSON 格式回傳照片資訊
    else:
        return jsonify({"message": "找不到照片"}), 404

# 刪除照片的 API
@aqur_bp.route('/api/delete_photo', methods=['DELETE'])
def delete_photo():
    aquarium_id = request.args.get('aquarium_id')
    photo_path = request.args.get('photo_path')

    if not aquarium_id or not photo_path:
        return jsonify({"success": False, "message": "缺少參數"}), 400

    # 這裡需要確認資料庫中的 photo_path 是否屬於該 aquarium_id，避免刪除錯誤的照片
    success = database.aquarium_model.delete_photo(aquarium_id, photo_path)

    if success:
        # 如果刪除成功，也可以刪除伺服器上的圖片檔案
        try:
            os.remove(photo_path)
            return jsonify({"success": True, "message": "照片刪除成功"}), 200
        except FileNotFoundError:
            return jsonify({"success": False, "message": "圖片檔案不存在"}), 500
    else:
        return jsonify({"success": False, "message": "資料庫中找不到對應的照片"}), 404


# 向AI取得推薦的水族箱參數API
@aqur_bp.route('/api/recommend_aquarium_settings', methods=['POST'])
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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 使用 ChatGPT 模型
            messages=[{"role": "system", "content": "你是水族箱設置專家。"},
                      {"role": "user", "content": prompt}],
            max_tokens=100,  # 限制生成的最大字數
            temperature=0.7,  # 控制創意和隨機性的數值
        )
        
        # 解析回傳的結果，並返回需要的參數
        response_text = response['choices'][0]['message']['content'].strip()

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

# 新增水族箱API
@aqur_bp.route("/api/add_aquarium",methods=["POST"])
def add_aquarium_page():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        data = request.get_json()  # 解析 JSON 資料

        aquarium_name = data.get("aquarium_name")
        fish_species = data.get("fish_species")
        fish_amount = data.get("fish_amount")
        ai_model = data.get("AI_model")
        user_id = session['user_id']
        min_temp = data.get("min_temp")
        max_temp = data.get("max_temp")
        feeding_frequency = data.get("feeding_frequency")
        feeding_amount = data.get("feeding_amount")

        aquarium_id  = database.aquarium_model.add_aquarium(user_id, aquarium_name, fish_species, fish_amount, ai_model,min_temp,max_temp,feeding_frequency,feeding_amount)
        
        if not aquarium_id:
            return jsonify({"status": "error", "message": "新增水族箱失敗"}), 500

    # 計算 next_exe_time
    h, m, s = map(int, feeding_frequency.split(":"))
    interval_delta = timedelta(hours=h, minutes=m, seconds=s)
    last_update = datetime.now()
    next_exe_time = last_update + interval_delta

    # 新增餵食任務至 tasks 表
    database.task_model.insert_feeding_task(
        aquarium_id=aquarium_id,
        topic=f"aquarium/{aquarium_id}/feed",
        payload="1",
        name=f"{aquarium_name} 餵食",
        next_time=next_exe_time,
        interval_str=feeding_frequency
    )

    return jsonify({"status": "success", "message": "水族箱已新增並排程餵食！"}), 200

# 查詢水族箱API
@aqur_bp.route('/api/get_aquarium_details/<aquarium_id>', methods=['GET'])
def aquarium_details(aquarium_id):
    # 根據 aquarium_id 查詢資料庫，並返回水族箱的詳細資料
    aquarium = database.aquarium_model.get_aquarium_by_id(aquarium_id)
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

# 刪除水族箱API
@aqur_bp.route('/api/delete_aquarium/<aquarium_id>', methods=['DELETE'])
def delete_aquarium(aquarium_id):
    # 呼叫 SQL 函式刪除水族箱
    success = database.aquarium_model.delete_aquarium(aquarium_id)
    if success:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Failed to delete aquarium"}), 500
    
# 更改水族箱資訊API
@aqur_bp.route('/api/update_aquarium/<aquarium_id>', methods=['POST'])
def update_aquarium_info(aquarium_id):
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "message": "未提供資料"}), 400

    # 定義允許更新的欄位
    allowed_fields = [
        "fish_species",  # 魚種
        "fish_amount",   # 魚隻數量
        "feed_amount",   # 每次餵食量
        "lowest_temperature",      # 最低溫
        "highest_temperature",      # 最高溫
        "light_status",  # 燈光狀態
        "water_level" # 水位
    ]

    # 從使用者傳入的資料中過濾出可更新的欄位
    update_fields = {key: data[key] for key in allowed_fields if key in data}

    if not update_fields:
        return jsonify({"success": False, "message": "沒有任何可更新的欄位"}), 400

    # 呼叫模型函式進行更新
    success = database.aquarium_model.update_aquarium_fields(aquarium_id, update_fields)

    if success:
        return jsonify({"success": True, "updated_fields": update_fields})
    else:
        return jsonify({"success": False, "message": "更新失敗"}), 500

# 更新水族箱名稱
@aqur_bp.route('/api/update_aquarium_name/<aquarium_id>', methods=['POST'])
def update_aquarium_name(aquarium_id):
    new_name = request.json.get('new_name')
    if not new_name:
        return jsonify({"success": False, "message": "Name is required"}), 400
    
    # 更新 aquariumname 表格中的名稱
    success = database.aquarium_model.update_aquarium_name(aquarium_id, new_name)
    if success:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Failed to update aquarium name"}), 500
    
# 查詢餵食資料    
@aqur_bp.route('/api/get_next_feed_time_and_amount', methods=['GET'])
def get_next_feed_time():
    aquarium_id = request.args.get('aquarium_id')
    if not aquarium_id:
        return jsonify({"error": "請提供 aquarium_id"}), 400

    aquarium = database.aquarium_model.get_aquarium_by_id(aquarium_id)
    if not aquarium:
        return jsonify({"error": "查無此水族箱"}), 404

    try:
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

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@aqur_bp.route('/api/update_feed_time', methods=['POST'])
def update_feed_time():
    data = request.get_json()
    aquarium_id = data.get("aquarium_id")

    if not aquarium_id:
        return jsonify({"error": "請提供 aquarium_id"}), 400

    success = database.aquarium_model.update_last_feed_time(aquarium_id, datetime.now())

    if success:
        return jsonify({"message": "Last_update 更新成功！"})
    else:
        return jsonify({"error": "更新失敗"}), 500

# 使用者手動餵食API
@aqur_bp.route('/api/manual_feed', methods=['POST'])
def manual_feed():
    data = request.get_json()
    aquarium_id = data.get("aquarium_id")

    if not aquarium_id:
        return jsonify({"error": "請提供 aquarium_id"}), 400

    now = datetime.now()

    # 發送 MQTT 餵食訊號
    publish_command(aquarium_id)

    # 更新 Last_update
    success = database.aquarium_model.update_last_feed_time(aquarium_id, now)

    if success:
        return jsonify({
            "message": "餵食成功並更新時間！",
            "updated_time": now.strftime("%Y-%m-%d %H:%M:%S")
        })
    else:
        return jsonify({"error": "餵食訊號已發送，但資料庫更新失敗"}), 500
    
@aqur_bp.route('/api/get_user_aquariums', methods=['GET'])
def get_user_aquariums():
    if 'user_id' not in session:
        return jsonify({"error": "未登入"}), 401

    user_id = session['user_id']
    try:
        aquariums = database.aquarium_model.get_aquariums_by_user(user_id)
        
        result = [{"aquarium_id": a["aquarium_id"], "aquarium_name": a["aquarium_name"]} for a in aquariums]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
