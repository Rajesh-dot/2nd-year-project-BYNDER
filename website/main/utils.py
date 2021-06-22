from functools import wraps
from flask_login import current_user
from flask import flash, redirect


def require_role(role):
    """make sure user has this role"""
    def decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            if not current_user.user_type == role:
                flash("No Permission", category="error")
                return redirect("/")
            else:
                return func(*args, **kwargs)
        return wrapped_function
    return decorator
