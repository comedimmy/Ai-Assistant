from flask import Blueprint,request,jsonify
import jwt
import Database.db2 

api = Blueprint('api', __name__)

SECRET_KEY = 'very-secret-key'  # Secret key for signing JWT

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
            Database.db2.bind_user_to_aquarium(user_id, aquarium_id, aquarium_name)
            return jsonify({"status": "joined", "message": "此水族箱已被激活，已加入為共同管理者"}), 200
        
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

    


'''

#------------------------------------------------------
# 更新水族箱的所有設定(模擬新增) 在row 38中使用到
#------------------------------------------------------
def update_aquarium(
    aquarium_id: str,
    user_id: str,
    aquarium_name: str,
    fish_species: str,
    fish_amount: int,
    ai_model: str,
    min_temp: float,
    max_temp: float,
    feeding_frequency: str,
    feeding_amount: int
) -> bool:
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 更新 Aquarium 表並設為已激活
        cursor.execute("""
            UPDATE Aquarium
            SET fish_species = %s, fish_amount = %s, AI_model = %s,
                lowest_temperature = %s, highest_temperature = %s,
                feed_time = %s, feed_amount = %s, Last_update = NOW(),
                activated = TRUE
            WHERE aquarium_id = %s
        """, (
            fish_species, fish_amount, ai_model,
            min_temp, max_temp, feeding_frequency, feeding_amount,
            aquarium_id
        ))

        # 綁定使用者與名稱（如果未綁定再 insert）
        cursor.execute("""
            INSERT INTO aquriumName (user_id, aquarium_id, aquarium_name)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE aquarium_name = VALUES(aquarium_name)
        """, (user_id, aquarium_id, aquarium_name))

        conn.commit()
        return True
    except Exception as e:
        print("Database update error:", str(e))
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
#+----------------------------------------------------+
# 新增：檢查是否已激活 在row 24 中使用到
#+----------------------------------------------------+
def is_aquarium_activated(aquarium_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT activated FROM Aquarium WHERE aquarium_id = %s", (aquarium_id,))
        row = cursor.fetchone()
        return row and bool(row[0])
    except Exception as e:
        print("[Check activated Error]:", str(e))
        return False
    finally:
        cursor.close()
        conn.close()


#------------------------------------------------------
# 新增：只做綁定，不修改設定 在row25中使用到
#------------------------------------------------------
def bind_user_to_aquarium(user_id: str, aquarium_id: str, aquarium_name: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO aquriumName (user_id, aquarium_id, aquarium_name)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE aquarium_name = VALUES(aquarium_name)
        """, (user_id, aquarium_id, aquarium_name))
        conn.commit()
        return True
    except Exception as e:
        print("[Bind User Error]:", str(e))
        return False
    finally:
        cursor.close()
        conn.close()

'''