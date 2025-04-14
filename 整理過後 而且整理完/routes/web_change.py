from flask import Blueprint,render_template,session,redirect,request
import database.user_model
import database.aquarium_model
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


# 返回主頁
@web_bp.route("/back")
def back():
    return render_template("index.html")  # index.html
# 使用者介面
@web_bp.route('/user_console')
def user_console():

    if "user_name" not in session:
        return render_template("error.html", message="您尚未登入，請先登入。")
    
    if 'token' in session:    
        resp=session['profile']
        user_info = resp
        user_id = user_info['id']
        aquariums = database.aquarium_model.get_aquariums_by_user(user_id)  # 🔹 呼叫函式查詢水族箱資料
        return render_template("user_console.html",user_picture = user_info['picture'],name=user_info['name'], email=user_info['email'],aquariums=aquariums)

# 新增水族箱 
@web_bp.route('/add_aqur')
def add_aqur():
    if "user_name" not in session:
        return render_template("error.html", message="您尚未登入，請先登入。")
    return render_template('add_aqur.html')  #add_aqur.html

# 指定水族箱介面
@web_bp.route('/aqur_console')
def aqur_console():
    if "user_name" not in session:
        return render_template("error.html", message="您尚未登入，請先登入。")
    return render_template('aqur_console.html')  #aqur_console.html

#照片管理頁面
@web_bp.route('/picture_console')
def picture_console():
    if "user_name" not in session:
        return render_template("error.html", message="您尚未登入，請先登入。")
    aquarium_id = request.args.get('aquarium_id', 1)  # 預設顯示 aquarium_id=1
    photos = database.aquarium_model.get_photos_by_aquarium_id(aquarium_id)
    return render_template('picture_console.html', photos=photos)

@web_bp.route('/test')
def test():
    return render_template('test.html')  #test.html

@web_bp.route('/chat_website')
def chat_website():
    aquarium_id = request.args.get("aquarium_id")
    if not aquarium_id:
        return "缺少 aquarium_id", 400
    # 可以在這裡用 aquarium_id 查資料、渲染頁面
    return render_template("chat.html", aquarium_id=aquarium_id)
