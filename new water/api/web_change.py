from flask import Blueprint,render_template,redirect,request

web_bp = Blueprint('web',__name__)

@web_bp.route('/test')
def test():
    return render_template('test.html')  #test.html

@web_bp.route('/Line-test')
def Line():
    return render_template('Line.html')  #test.html

@web_bp.route('/')
def index():
    return render_template('index.html')  #test.html

@web_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')  #test.html

@web_bp.route('/add_aqur')
def add_aqur():
    return render_template('add_aqur.html')  #test.html

