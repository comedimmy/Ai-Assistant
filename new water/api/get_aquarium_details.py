from flask import Blueprint,request,jsonify
import jwt
import Database.db2 

api = Blueprint('api', __name__)

SECRET_KEY = 'very-secret-key'  # Secret key for signing JWT

# -------------------------------------------+
# 查詢水族箱資訊API input:token,aquarium_id
# -------------------------------------------+
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

'''
#------------------------------------------------------
# 以aquarium_id查詢該id的所有資訊 row 25
#------------------------------------------------------
def get_aquarium_by_id(aquarium_id: str) -> dict | None:
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True) 
        cursor.execute("""
            SELECT * FROM Aquarium where aquarium_id=%s
        """, (aquarium_id,))
        
        aquariums = cursor.fetchone()
        return aquariums
    except Exception as e:
        print("Database error:", str(e))
        return []
    finally:
        cursor.close()
        conn.close()
        
'''