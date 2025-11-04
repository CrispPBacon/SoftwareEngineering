from functools import wraps
from flask import session, redirect, url_for, flash


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to log in first.', 'bg-red-300 text-red-700')
            return redirect(url_for('user.login'))
        if session.get('role') != 'admin':
            # flash('You do not have permission to access this page.', 'error')
            # Redirect to a default page (e.g., 'menu')
            return redirect(url_for('main.menu'))
        return f(*args, **kwargs)
    return decorated_function

# Modify user_required decorator


def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to log in first.', 'bg-red-300 text-red-700')
            return redirect(url_for('user.login'))
        if session.get('role') == 'admin':
            # flash('Admins cannot access user-only areas.', 'error')
            # Redirect to the admin dashboard or another relevant page
            return redirect(url_for('admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function
