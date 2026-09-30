from flask import Blueprint


bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return "Irish Property Price Explorer is running"

@bp.route("/health")
def health():
    return{"status": "ok"}