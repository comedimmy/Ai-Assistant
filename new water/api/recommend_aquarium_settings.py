from flask import Blueprint,request,jsonify
import jwt
import Database.db2 
from openai import OpenAI

api = Blueprint('api', __name__)

SECRET_KEY = 'very-secret-key'  # Secret key for signing JWT

client = OpenAI(api_key="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")

#---------------------------------------------------------------------------------------+
# 向AI取得推薦的水族箱參數API 通常不會讓使用者接觸到 但我為了以防萬一 額外開了一個entry point
#---------------------------------------------------------------------------------------+
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