from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def format_datetime(dt):
    """Format datetime for display"""
    if dt:
        return dt.strftime('%B %d, %Y at %I:%M %p')
    return ''

def truncate_text(text, length=150):
    """Truncate text for summaries"""
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + '...'
