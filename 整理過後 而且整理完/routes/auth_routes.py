from flask import Blueprint, session, render_template, redirect, url_for
from dotenv import load_dotenv
import database.user_model
import requests
import os

load_dotenv()

def create_auth_blueprint(oauth):
    auth_bp = Blueprint('auth', __name__)

    google = oauth.register(
        name='google',
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        access_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
        client_kwargs={'scope': 'email profile'},
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
    )

    @auth_bp.route('/Google-Login')
    def google_login():
        if "user_name" in session:
            return render_template("error.html", message="您已經登入,請勿重複登入")
        google_client = oauth.create_client('google')
        redirect_uri = url_for('auth.authorize', _external=True)
        return google_client.authorize_redirect(redirect_uri)

    @auth_bp.route('/authorize')
    def authorize():
        google = oauth.create_client('google')

        token = google.authorize_access_token()
        if not token:
            return render_template("error.html", message="授權失敗，請重新登入")
        session['token'] = token

        response = google.get('userinfo')
        user_info = response.json()
        session['profile'] = user_info
        session.permanent = True  

        user_id = user_info['id']
        user_email = user_info['email']
        user_name = user_info['name']

        try:
            existing_user = database.user_model.get_user_by_id(user_id)
        except Exception as e:
            return render_template("error.html", message=f"資料庫存取錯誤: {e}，請稍後再試")

        try:
            if existing_user:
                session['user_id'] = existing_user['user_id']
                session['user_email'] = user_info['email']
                session['user_name'] = existing_user['nickname']

                response = requests.post(
                     "http://127.0.0.1:5000/api/save_user",
                    json={
                        "user_id": existing_user['user_id'], 
                        "nickname": existing_user['nickname'], 
                        "login_type": "Google"
                    },
                    timeout=5
                )
            else:
                response = requests.post(
                    "http://127.0.0.1:5000/api/save_user",
                    json={
                        "user_id": user_id, 
                        "nickname": user_name, 
                        "login_type": "Google"
                        },
                    timeout=5
                )

                if response.status_code == 200:
                    session['user_id'] = user_id
                    session['user_email'] = user_email
                    session['user_name'] = user_name
                else:
                    return render_template("error.html", message="無法儲存使用者資料，請稍後再試")
        except requests.RequestException as e:
            return render_template("error.html", message=f"API 請求錯誤: {e}")

        return redirect("user_console")

    @auth_bp.route('/logout')
    def logout():
        for key in list(session.keys()):
            session.pop(key)
        return redirect('/')

    return auth_bp