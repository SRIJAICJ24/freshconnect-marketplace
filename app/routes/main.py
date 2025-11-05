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
    try:
        if current_user.is_authenticated:
            print(f"🔍 Dashboard redirect for user {current_user.id}, type: {current_user.user_type}")
            
            if current_user.user_type == 'vendor':
                return redirect(url_for('vendor.dashboard'))
            elif current_user.user_type == 'retailer':
                return redirect(url_for('retailer.dashboard'))
            elif current_user.user_type == 'driver':
                return redirect(url_for('driver.dashboard'))
            elif current_user.user_type == 'admin':
                return redirect(url_for('admin.dashboard'))
        
        return render_template('index.html')
    except Exception as e:
        print(f"❌ Dashboard redirect error: {e}")
        import traceback
        traceback.print_exc()
        return f"<h1>Redirect Error</h1><p>{str(e)}</p><p>User: {current_user.id if current_user.is_authenticated else 'Not logged in'}</p>", 500

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

@bp.route('/test-dashboard')
def test_dashboard():
    """Test route to diagnose dashboard issues"""
    if not current_user.is_authenticated:
        return "<h1>NOT LOGGED IN</h1><p>Please login first</p>"
    
    html = f"""
    <h1>✅ TEST DASHBOARD - WORKING!</h1>
    <p><strong>User ID:</strong> {current_user.id}</p>
    <p><strong>Name:</strong> {current_user.name}</p>
    <p><strong>Email:</strong> {current_user.email}</p>
    <p><strong>User Type:</strong> {current_user.user_type}</p>
    <hr>
    <p>If you see this, your login works!</p>
    <p>The error is in the template or dashboard logic.</p>
    <hr>
    <a href="/retailer/dashboard">Try Retailer Dashboard</a> |
    <a href="/vendor/dashboard">Try Vendor Dashboard</a> |
    <a href="/auth/logout">Logout</a>
    """
    return html

@bp.route('/seed-data')
def seed_data():
    """Add sample data for testing - Railway production"""
    try:
        from werkzeug.security import generate_password_hash
        from app.models import Product
        from datetime import datetime
        
        # Create sample vendor
        vendor = User.query.filter_by(email='vendor@test.com').first()
        if not vendor:
            vendor = User(
                name='Sample Vendor',
                email='vendor@test.com',
                password_hash=generate_password_hash('password123'),
                user_type='vendor',
                phone='9876543210',
                address='Koyambedu Market',
                city='Chennai'
            )
            db.session.add(vendor)
            db.session.commit()
        
        # Create sample products
        products_data = [
            {'name': 'Tomatoes', 'category': 'vegetable', 'price': 40, 'stock': 100, 'moq': 5},
            {'name': 'Onions', 'category': 'vegetable', 'price': 30, 'stock': 150, 'moq': 10},
            {'name': 'Potatoes', 'category': 'vegetable', 'price': 25, 'stock': 200, 'moq': 10},
            {'name': 'Carrots', 'category': 'vegetable', 'price': 35, 'stock': 80, 'moq': 5},
            {'name': 'Apples', 'category': 'fruit', 'price': 120, 'stock': 60, 'moq': 5},
            {'name': 'Bananas', 'category': 'fruit', 'price': 60, 'stock': 100, 'moq': 12},
        ]
        
        added = 0
        for data in products_data:
            existing = Product.query.filter_by(name=data['name'], vendor_id=vendor.id).first()
            if not existing:
                product = Product(
                    name=data['name'],
                    description=f'Fresh {data["name"]} from Koyambedu',
                    category=data['category'],
                    price=data['price'],
                    stock_quantity=data['stock'],
                    moq=data['moq'],
                    unit='kg',
                    vendor_id=vendor.id,
                    created_at=datetime.utcnow()
                )
                db.session.add(product)
                added += 1
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Sample data added!',
            'products_added': added,
            'total_products': Product.query.count(),
            'total_users': User.query.count()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
