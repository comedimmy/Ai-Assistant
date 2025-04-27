from flask import Blueprint,render_template,redirect,request

web_bp = Blueprint('web',__name__)

@web_bp.route('/test')
def test():
    return render_template('test.html')  #test.html
