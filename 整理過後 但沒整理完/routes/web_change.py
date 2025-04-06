from flask import Blueprint,render_template,session,redirect
import database.user_model
web_bp = Blueprint('web',__name__)

@web_bp.route('/')
def index():
    if 'profile' in session:
        # 使用者已登入，將資料傳給前端
        user_info = session['profile']
        if 'user_id' not in session:
            return redirect("logout")
        user_id = session['user_id']
        user_data=database.user_model.get_user_by_id(user_id)
        return render_template('index.html', user_info=user_info,user_data=user_data)
    else:
        # 使用者未登入，顯示登入/註冊選項
        return render_template('index.html', user_info=None)
