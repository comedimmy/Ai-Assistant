from flask import Blueprint

messenge_bp = Blueprint('messenge',__name__)

@messenge_bp.route('/api/add_messenge')
def add_messenge(aqurium_id,content):
