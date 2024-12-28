from functools import wraps
from flask import session


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            return "Forbidden", 403
        return f(*args, **kwargs)

    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return "Forbidden", 403
        return f(*args, **kwargs)

    return decorated_function
