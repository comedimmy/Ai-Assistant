from flask import Blueprint,request,jsonify
import jwt
import Database.get_user_all_aquariums_recent_dialogues 
from openai import OpenAI

api = Blueprint('api', __name__)

SECRET_KEY = 'very-secret-key'  # Secret key for signing JWT

client = OpenAI(api_key="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")

#----------------------------------------------------------------------------------------------+
# 該API作用為取得使用者層AI的即時回應 
# input: 
# 1.token 
# 2.messenge(使用者詢問或輸入的內容) 
#----------------------------------------------------------------------------------------------+
@api.route('/get_user_AI_response', methods=['POST'])
def user_bot_response():
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

        recent_questions = Database.get_user_all_aquariums_recent_dialogues.get_user_all_aquariums_recent_dialogues(user_id, limit=3)

        messages = [
            {"role": "system", "content": (
                "你是智慧水族管家，專門幫助使用者統整所有水族箱的問題與建議，語氣親切簡潔，用繁體中文純文字回答。"
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
        return jsonify({"GPT_messenge": gpt_reply})

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token 已過期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token 驗證失敗'}), 401
    
#------------------------------------------------------------+
# 在使用者對AI的情況下 需要讓AI知道所有水族箱的最後三個對話 row 37
#------------------------------------------------------------+
def get_user_all_aquariums_recent_dialogues(user_id: str, limit: int = 3) -> list[str]:
    conn = None
    cursor = None
    try:    
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            WITH RankedDialogue AS (
                SELECT 
                    d.question,
                    d.aquarium_id,
                    aqn.aquarium_name,
                    ROW_NUMBER() OVER (
                        PARTITION BY d.aquarium_id 
                        ORDER BY d.transmit_time DESC
                    ) AS rn
                FROM dialogue d
                JOIN aquriumname aqn 
                    ON d.aquarium_id = aqn.aquarium_id 
                   AND d.user_id = aqn.user_id
                WHERE aqn.user_id = %s
            )
            SELECT question, aquarium_id, aquarium_name
            FROM RankedDialogue
            WHERE rn <= %s
            ORDER BY aquarium_id, rn
        """, (user_id, limit))

        rows = cursor.fetchall()

        if not rows:
            return []

        # 把每筆資料轉換成 "水族箱名稱：對話內容"
        result = [f"{row[2]}：{row[0]}" for row in rows]
        return result

    except Exception as e:
        print("[get_user_all_aquariums_recent_dialogues ERROR]", str(e))
        return []
    finally:
        cursor.close()
        conn.close()
