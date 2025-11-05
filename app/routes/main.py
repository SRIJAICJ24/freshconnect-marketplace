from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/dashboard')
def dashboard():
    if current_user.is_authenticated:
        if current_user.user_type == 'vendor':
            return redirect(url_for('vendor.dashboard'))
        elif current_user.user_type == 'retailer':
            return redirect(url_for('retailer.dashboard'))
        elif current_user.user_type == 'driver':
            return redirect(url_for('driver.dashboard'))
        elif current_user.user_type == 'admin':
            return redirect(url_for('admin.dashboard'))
    
    return render_template('index.html')

@bp.route('/responsive-demo')
def responsive_demo():
    """Demo page showing mobile-first responsive design"""
    return render_template('responsive_demo.html')
