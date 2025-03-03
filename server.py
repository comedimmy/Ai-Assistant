from flask import Flask, render_template, jsonify, redirect, request, session, url_for
import requests
import json
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session handling

load_dotenv()
LINE_CLIENT_ID = os.getenv('LINE_CLIENT_ID')
LINE_CLIENT_SECRET = os.getenv('LINE_CLIENT_SECRET')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

#config = dotenv_values(".env")
LINE_AUTH_URL = "https://access.line.me/oauth2/v2.1/authorize"
LINE_TOKEN_URL = "https://api.line.me/oauth2/v2.1/token"
LINE_PROFILE_URL = "https://api.line.me/v2/profile"
REDIRECT_URI = "http://127.0.0.1:5000/API/callback"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_PROFILE_URL = "https://www.googleapis.com/oauth2/v1/userinfo"


@app.route('/')
def main_page():
    return render_template('index.html')
    
@app.route("/Google-Login")
def google_login():
    """ Redirect user to Google OAuth page """
    #redirect_uri = 'http://127.0.0.1:5000/API/callback'
    login_url = (
        f"{GOOGLE_AUTH_URL}?response_type=code&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={'http://127.0.0.1:5000/login'}&scope=email%20profile&state=123456"
    )
    return redirect(login_url)
@app.route('/Line-Login')
def line_login():
    """ Redirect to LINE login page """
    login_url = f"{LINE_AUTH_URL}?response_type=code&client_id={LINE_CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=profile%20openid%20email&state=123456"

    return redirect(login_url)
@app.route('/API')
def test():
        return json.dumps({'title':'Testing','body':'This is a test.'})

@app.route('/API/callback')
def login_info():
    """ Handle the OAuth2 callback from LINE """
    
    code = request.args.get('code')
    if not code:
        return "Error: No code received", 400

    # Exchange code for access token
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': LINE_CLIENT_ID,
        'client_secret': LINE_CLIENT_SECRET
    }
    token_response = requests.post(LINE_TOKEN_URL, data=token_data)
    token_json = token_response.json()

    if 'access_token' not in token_json:
        return "Error retrieving access token", 400

    access_token = token_json['access_token']

    # Get user profile data
    headers = {'Authorization': f'Bearer {access_token}'}
    profile_response = requests.get(LINE_PROFILE_URL, headers=headers)
    profile_json = profile_response.json()
    # Extract unique user ID
    user_id = profile_json.get('userId', 'Unknown ID')
    display_name = profile_json.get('displayName', 'Unknown User')
    picture_url = profile_json.get('pictureUrl', '')
   
    # Store user info in session
    #session['user'] = profile_json
    # Store user info in session
    session['user'] = {
        'userId': user_id,  # Unique LINE user ID
        'displayName': display_name,
        'pictureUrl': picture_url
    }
    return redirect(url_for('home'))
    
@app.route('/API/webhook')
def webhook():
    pass

    
if __name__ == '__main__':
    app.run(debug=True)
