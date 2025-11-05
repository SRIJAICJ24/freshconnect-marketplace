from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import current_user
from app import db
from app.models import User
import os

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

@bp.route('/health')
def health():
    """Health check endpoint for Railway deployment"""
    try:
        # Check database connection
        user_count = User.query.count()
        db_status = "connected"
    except Exception as e:
        user_count = 0
        db_status = f"error: {str(e)}"
    
    return jsonify({
        'status': 'running',
        'database': db_status,
        'users': user_count,
        'environment': os.environ.get('FLASK_ENV', 'unknown'),
        'has_secret_key': bool(os.environ.get('SECRET_KEY')),
        'has_database_url': bool(os.environ.get('DATABASE_URL'))
    })

@bp.route('/init-db')
def init_db():
    """Initialize database tables - use this once after deployment"""
    try:
        db.create_all()
        return jsonify({
            'status': 'success',
            'message': 'Database tables created successfully!',
            'users': User.query.count()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
