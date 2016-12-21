from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission


def permission_required(permission):
    def decorator(f):
        # standard library helper function to update the wrapper function
        # preserves docstrings and names when the decorator is used
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    # Helper function as admin required is a common operation
    return permission_required(Permission.ADMINISTER)(f)
