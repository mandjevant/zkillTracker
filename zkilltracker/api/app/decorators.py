from functools import wraps
from flask_login import current_user
from app.models import AdminCharacters
from app.helpers import is_admin
from flask import jsonify


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return "Forbidden", 403
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not is_admin(current_user):
            return jsonify({"redirect": "/login"}), 401
        return f(*args, **kwargs)

    return decorated_function
