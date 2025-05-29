from flask import Blueprint,request,jsonify
import jwt
import Database.db2 

api = Blueprint('api', __name__)

SECRET_KEY = 'very-secret-key'  # Secret key for signing JWT



# +--------------------------------------------------------------------------+
# | 解除綁定 API 
# | input為 token,aquarium_id
# +--------------------------------------------------------------------------+
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
            Database.db2.deactivate_aquarium_if_unbound(aquarium_id)
            return jsonify({'status': 'success', 'message': '已解除綁定'}), 200
        else:
            return jsonify({'status': 'error', 'message': '找不到綁定關係'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


'''
# +--------------------------------------------------------------------------+
# | unbind_user_from_aquarium 資料庫函式 row 28
# +--------------------------------------------------------------------------+

def unbind_user_from_aquarium(user_id: str, aquarium_id: str) -> bool:
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM aquriumName
            WHERE user_id = %s AND aquarium_id = %s
        """, (user_id, aquarium_id))

        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print("Database error:", str(e))
        return False
    finally:
        cursor.close()
        conn.close()

# +--------------------------------------------------------------------------+
# | deactivate_aquarium_if_unbound 資料庫函式 row 32
# +--------------------------------------------------------------------------+

def deactivate_aquarium_if_unbound(aquarium_id: str):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM aquriumName
            WHERE aquarium_id = %s
        """, (aquarium_id,))
        result = cursor.fetchone()

        if result and result[0] == 0:
            cursor.execute("""
                UPDATE Aquarium
                SET activated = FALSE
                WHERE aquarium_id = %s
            """, (aquarium_id,))
            conn.commit()
    except Exception as e:
        print("[Deactivate aquarium error]:", str(e))
    finally:
        cursor.close()
        conn.close()
'''