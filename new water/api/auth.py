from flask import Blueprint, render_template, redirect, url_for,jsonify
from Database.db2 import get_user_by_id
import requests
import os
import jwt

SECRET_KEY = 'very-fucking-secret-key'  # Secret key for signing JWT

def create_auth_blueprint(oauth):
    auth_bp = Blueprint('auth', __name__)

    google = oauth.register(
        name='google',
        client_id='335965473255-klcvtsdd0hf7ah8b4pmc442t5q141jg3.apps.googleusercontent.com',
        client_secret='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',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
        client_kwargs={'scope': 'email profile'},
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
    )

    @auth_bp.route('/Google-Login')
    def google_login():
        google_client = oauth.create_client('google')
        redirect_uri = url_for('auth.authorize', _external=True)
        return google_client.authorize_redirect(redirect_uri)

    @auth_bp.route('/authorize')
    def authorize():
        google = oauth.create_client('google')
        token = google.authorize_access_token()
        if not token:
            return render_template("error.html", message="授權失敗，請重新登入")

        response = google.get('userinfo')
        user_info = response.json()

        user_id = user_info['id']
        user_email = user_info['email']
        user_name = user_info['name']
        user_picture = user_info.get('picture')

        try:
            existing_user = get_user_by_id(user_id)
        except Exception as e:
            return render_template("error.html", message=f"資料庫存取錯誤: {e}，請稍後再試")

        try:
            if existing_user:
                nickname = existing_user['nickname']
            else:
                nickname = user_name

            save_response = requests.post(
                "http://127.0.0.1:5000/api/save_user",
                json={
                    "user_id": user_id,
                    "nickname": nickname,
                    "login_type": "Line"
                },
                timeout=5
            )
            if save_response.status_code != 200:
                return render_template("error.html", message="無法儲存使用者資料，請稍後再試")
        except requests.RequestException as e:
            return render_template("error.html", message=f"API 請求錯誤: {e}")
        
        payload = {
            "user_id": user_id,
            "nickname": nickname,
            "email": user_email,
            "picture": user_picture,
        }
        jwt_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        
        return redirect(url_for('web.test',jwt_token=jwt_token))

    @auth_bp.route('/logout')
    def logout():
        return redirect('/')

    return auth_bp

