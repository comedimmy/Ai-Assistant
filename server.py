from flask import Flask, render_template, jsonify, redirect
import json
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()
LINE_CLIENT_ID = os.getenv('LINE_CLIENT_ID')
LINE_CLIENT_SECRET = os.getenv('LINE_CLIENT_SECRET')

#config = dotenv_values(".env")
LINE_AUTH_URL = "https://access.line.me/oauth2/v2.1/authorize"
LINE_TOKEN_URL = "https://api.line.me/oauth2/v2.1/token"
LINE_PROFILE_URL = "https://api.line.me/v2/profile"
REDIRECT_URI = "http://127.0.0.1:5000/API/callback"

@app.route('/')
def main_page():
    return render_template('index.html')

@app.route('/Login')
def line_login():
    """ Redirect to LINE login page """
    login_url = f"{LINE_AUTH_URL}?response_type=code&client_id={LINE_CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=profile%20openid%20email&state=123456"

    return redirect(login_url)
@app.route('/API')
def test():
        return json.dumps({'title':'Testing','body':'This is a test.'})

@app.route('/API/webhook')
def webhook():
    pass

@app.route('/API/webhook')
def callback():
    pass
    
if __name__ == '__main__':
    app.run(debug=True)
