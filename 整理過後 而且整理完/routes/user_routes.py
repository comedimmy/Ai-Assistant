from flask import Blueprint,session,jsonify,request
import database.user_model
user_bp = Blueprint('user',__name__)

@user_bp.route('/api/profile') #測試用
def profile():
    if 'profile' in session:  # 如果 session 中有 'profile' 資料，代表使用者已登入
        user_info = session['profile']
        return jsonify(user_info)  # 返回使用者資料
    else:
        # 如果沒有登入，返回錯誤訊息
        return jsonify({"error": "User not logged in"}), 401

# 新增使用者資料API
@user_bp.route("/api/save_user", methods=["POST"])
def save_user_api():
    data = request.json  
    if not data or "user_id" not in data or "nickname" not in data or "login_type" not in data:
        return jsonify({"message": "Invalid data", "status": "error"}), 400

    user_id = data["user_id"]
    nickname = data["nickname"]
    login_type = data["login_type"]

    if login_type == "Google":
        user_id = database.user_model.save_user_google(user_id, nickname, login_type)
    elif login_type == "Line":
        user_id = database.user_model.save_user_line(nickname, user_id, login_type) #還沒實作
    else:
        return jsonify({"message": "Invalid login type", "status": "error"}), 400

    return jsonify({"message": "User saved", "status": "success", "user_id": user_id})

# 查詢使用者資料 API
@user_bp.route('/api/get_user_data', methods=['GET'])
def get_user_data():
    # **直接從 session 取得 user_id**
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登入，請重新登入"}), 401  # 未登入時返回 401 錯誤

    user_data = database.user_model.get_user_by_id(user_id)

    if user_data:
        return jsonify(user_data)  # 回傳使用者資料
    else:
        return jsonify({"error": "找不到使用者"}), 404

# 修改使用者資料API
@user_bp.route('/api/update_user_name', methods=['POST'])
def update_user_name_api():
    if "user_name" not in session:
        return jsonify({"error": "未登入"}), 401

    data = request.json
    new_user_name = data.get("new_name")

    if not new_user_name:
        return jsonify({"error": "請輸入新的名稱"}), 400

    # 呼叫資料庫函數更新名稱
    success = database.user_model.update_user_name(session["user_id"], new_user_name)

    if success:
        session["user_name"] = new_user_name  # 更新 session 中的使用者名稱
        return jsonify({"message": "使用者名稱更新成功", "new_name": new_user_name})
    else:
        return jsonify({"error": "更新失敗，你沒有更改名稱"}), 500
