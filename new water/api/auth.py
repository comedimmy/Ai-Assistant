from flask import Flask, request, jsonify, redirect, render_template, Blueprint, url_for
from Database.db2 import save_user
import requests
import jwt #pip install pyjwt
import datetime

Line = Blueprint('Line', __name__)

@Line.route('/api/Line-Test')
def test():
    return 'Test'

@Line.route('/api/Line-info',methods=['POST'])
def line_info():
    CLIENT_ID = '2007340400'
    CLIENT_SECRET = 'eb8592a6d896f62008467143d4f6aa65'
    REDIRECT_URI = 'http://127.0.0.1:5000'
    SECRET_KEY = 'very-secret-key'  # Secret key for signing JWT
    
    data = request.json
    
    code = data.get('code')
    token_url = 'https://api.line.me/oauth2/v2.1/token'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    token_res = requests.post(token_url, data=data, headers=headers)

    token_data = token_res.json()

    access_token = token_data.get('access_token')
    
    if not access_token:
        return jsonify({'error': 'Failed to get access token'}), 400

    # Get user profile
    profile_res = requests.get(
        'https://api.line.me/v2/profile',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    profile = profile_res.json()

    # Extract relevant user data from the profile
    user_id = profile.get('userId')
    display_name = profile.get('displayName')
    picture_url = profile.get('pictureUrl')
    payload = {
        'user_id': user_id,
        'display_name': display_name,
        'picture_url': picture_url
    }
    print(payload)
    # Generate JWT token
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return jsonify({'token':token})

@Line.route('/api/Line-callback',methods=['GET'])
def callback():

    CLIENT_ID = '2007340400'

    CLIENT_SECRET = 'eb8592a6d896f62008467143d4f6aa65'

    REDIRECT_URI = 'http://127.0.0.1:5000/api/Line-callback'

    SECRET_KEY = 'very-secret-key'  # Secret key for signing JWT
    
    code = request.args.get('code')

    token_url = 'https://api.line.me/oauth2/v2.1/token'
    state = request.args.get('state')


    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }



    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    token_res = requests.post(token_url, data=data, headers=headers)

    token_data = token_res.json()
    print("Code: ",code," State: ",state)
    print("Token Data: ",token_data)
    #token_data.get('id_token')#Decode id_token can get user information
    
    access_token = token_data.get('access_token')

    if not access_token:

        return jsonify({'error': 'Failed to get access token'}), 400



    # Get user profile

    profile_res = requests.get(
        'https://api.line.me/v2/profile',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    profile = profile_res.json()
    
    # Extract relevant user data from the profile
    user_id = profile.get('userId')
    display_name = profile.get('displayName')
    picture_url = profile.get('pictureUrl')
    
    #查詢資料庫, 如果是新用戶則新增使用者, 舊用戶則更新登入時間
    login_type = "line"  # 自訂一個固定的登入類型
    save_user(user_id, display_name, login_type)


    # Create a payload with user data
    payload = {
        'user_id': user_id,
        'display_name': display_name,
        'picture_url': picture_url
    }

    # Generate JWT token
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    return redirect(f"http://127.0.0.1:5000/?token={token}")
    #return redirect(url_for('main.serve_index',token=token))
