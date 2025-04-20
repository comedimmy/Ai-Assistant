from flask import Blueprint,request, jsonify
import openai
import os
import database.dialogue_model  
from dotenv import load_dotenv

load_dotenv()

dialogue_bp = Blueprint('messenge',__name__)

# 載入 OpenAI 金鑰
openai.api_key = os.getenv("OPENAI_API_KEY")

@dialogue_bp.route('/api/send_messenge/<aquarium_id>', methods=['POST'])
def send_messenge(aquarium_id):
    data = request.get_json()
    user_input = data.get("messenge")

    if not user_input:
        return jsonify({"error": "請提供訊息內容"}), 400

    try:
        # 儲存使用者的對話
        database.dialogue_model.insert_dialogue(aquarium_id, user_input, sender="使用者")

        # 使用 system prompt 限制主題
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是智慧水族箱的 AI 管家，"
                        "專門協助使用者了解魚類的飼養、水質調整、溫度控制、"
                        "餵食建議及疾病預防等資訊。請使用繁體中文、"
                        "語氣親切簡潔，並避免回答非魚類相關問題。"
                    )
                },
                {"role": "user", "content": user_input}
            ]
        )

        gpt_reply = response['choices'][0]['message']['content']

        # 儲存GPT回應
        database.dialogue_model.insert_dialogue(aquarium_id, gpt_reply, sender="AI")

        return jsonify({"GPT_messenge": gpt_reply})

    except Exception as e:
        return jsonify({"error": f"ChatGPT 發送失敗：{str(e)}"}), 500

@dialogue_bp.route("/api/get_dialogue/<aquarium_id>", methods=["GET"])
def get_dialogue(aquarium_id):
    records = database.dialogue_model.get_dialogue_by_aquarium(aquarium_id)
    if not records:
        return jsonify({"message": "沒有對話紀錄"}), 404
    return jsonify(records), 200