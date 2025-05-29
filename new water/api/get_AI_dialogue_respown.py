from flask import Blueprint,request,jsonify
import jwt
import Database.db2 
from openai import OpenAI

api = Blueprint('api', __name__)

SECRET_KEY = 'very-secret-key'  # Secret key for signing JWT

client = OpenAI(api_key="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")


#----------------------------------------------------------------------------------------------+
# 該API作用為取得AI的即時回應 如果你要前端fetch的函式可以跟我說 我這邊都有測試過了 說不定可以不用重頭打
#----------------------------------------------------------------------------------------------+
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

'''
#------------------------------------------------------
# 為了讓AI理解上下文 必須存取該水族箱的部分聊天紀錄 row 36
#------------------------------------------------------
def get_recent_questions(aquarium_id: str, limit: int = 5) -> list[str]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT question
            FROM dialogue
            WHERE aquarium_id = %s
            ORDER BY transmit_time DESC
            LIMIT %s
        """, (aquarium_id, limit))
        rows = cursor.fetchall()
        return [row[0] for row in reversed(rows)] if rows else []
    except Exception as e:
        print("[Get recent_questions Error]:", str(e))
        return []
    finally:
        cursor.close()
        conn.close()


#------------------------------------------------------
# 新增與AI聊天的紀錄 row 63
#------------------------------------------------------
def insert_dialogue(aquarium_id: str, user_id: str, question: str, response: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO dialogue (aquarium_id, user_id, question, response, transmit_time)
            VALUES (%s, %s, %s, %s, NOW())
        """, (aquarium_id, user_id, question, response))
        conn.commit()
        return True
    except Exception as e:
        print("[Insert dialogue Error]:", str(e))
        return False
    finally:
        cursor.close()
        conn.close()

'''