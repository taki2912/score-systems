from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, redirect, url_for, flash
from models import User


def hash_password(password):
    return generate_password_hash(password)


def verify_password(password_hash, password):
    return check_password_hash(password_hash, password)


def login_user(user):
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role


def logout_user():
    session.clear()


def get_current_user():
    user_id = session.get('user_id')
    if user_id is None:
        return None
    return User.query.get(user_id)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_id') is None:
            flash('请先登录', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_id') is None:
            flash('请先登录', 'warning')
            return redirect(url_for('login'))
        if session.get('role') not in ('admin', 'super_admin'):
            flash('需要管理员权限', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


def super_admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_id') is None:
            flash('请先登录', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'super_admin':
            flash('需要超级管理员权限', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated
