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

@bp.route('/debug-session')
def debug_session():
    """Debug route to check session and authentication status"""
    from flask import session
    
    info = {
        'is_authenticated': current_user.is_authenticated,
        'user_id': current_user.id if current_user.is_authenticated else None,
        'has_user_type': hasattr(current_user, 'user_type') if current_user.is_authenticated else False,
        'user_type': getattr(current_user, 'user_type', None) if current_user.is_authenticated else None,
        'session_keys': list(session.keys()),
        'flask_login_id': session.get('_user_id', None)
    }
    
    if current_user.is_authenticated:
        try:
            info['user_name'] = current_user.name
            info['user_email'] = current_user.email
        except Exception as e:
            info['user_load_error'] = str(e)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Session Debug</title>
        <style>
            body {{ font-family: monospace; padding: 20px; background: #1e1e1e; color: #00ff00; }}
            .info {{ background: #2d2d2d; padding: 20px; border-radius: 8px; margin: 10px 0; }}
            .key {{ color: #00ffff; }}
            .value {{ color: #ffff00; }}
            .error {{ color: #ff0000; }}
            .success {{ color: #00ff00; }}
            a {{ color: #00ffff; margin: 10px; display: inline-block; }}
        </style>
    </head>
    <body>
        <h1>🔍 Session Debug Information</h1>
        <div class="info">
            <h3>Authentication Status:</h3>
            <p><span class="key">Is Authenticated:</span> <span class="{'success' if info['is_authenticated'] else 'error'}">{info['is_authenticated']}</span></p>
            <p><span class="key">User ID:</span> <span class="value">{info['user_id']}</span></p>
            <p><span class="key">Has user_type:</span> <span class="value">{info['has_user_type']}</span></p>
            <p><span class="key">User Type:</span> <span class="value">{info['user_type']}</span></p>
            <p><span class="key">Session User ID:</span> <span class="value">{info['flask_login_id']}</span></p>
        </div>
        <div class="info">
            <h3>Session Keys:</h3>
            <p><span class="value">{info['session_keys']}</span></p>
        </div>
        {'<div class="info"><h3>User Info:</h3><p>Name: ' + info.get('user_name', 'N/A') + '</p><p>Email: ' + info.get('user_email', 'N/A') + '</p></div>' if info['is_authenticated'] else ''}
        {'<div class="info error"><h3>User Load Error:</h3><p>' + info.get('user_load_error', '') + '</p></div>' if 'user_load_error' in info else ''}
        <div class="info">
            <h3>Quick Actions:</h3>
            <a href="/auth/logout">Logout & Clear Session</a>
            <a href="/auth/login">Go to Login</a>
            <a href="/">Home</a>
        </div>
    </body>
    </html>
    """
    return html

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
            {'product_name': 'Tomatoes', 'category': 'vegetable', 'price': 40, 'quantity': 100, 'minimum_quantity': 5},
            {'product_name': 'Onions', 'category': 'vegetable', 'price': 30, 'quantity': 150, 'minimum_quantity': 10},
            {'product_name': 'Potatoes', 'category': 'vegetable', 'price': 25, 'quantity': 200, 'minimum_quantity': 10},
            {'product_name': 'Carrots', 'category': 'vegetable', 'price': 35, 'quantity': 80, 'minimum_quantity': 5},
            {'product_name': 'Apples', 'category': 'fruit', 'price': 120, 'quantity': 60, 'minimum_quantity': 5},
            {'product_name': 'Bananas', 'category': 'fruit', 'price': 60, 'quantity': 100, 'minimum_quantity': 12},
        ]
        
        added = 0
        for data in products_data:
            existing = Product.query.filter_by(product_name=data['product_name'], vendor_id=vendor.id).first()
            if not existing:
                product = Product(
                    product_name=data['product_name'],
                    description=f'Fresh {data["product_name"]} from Koyambedu',
                    category=data['category'],
                    price=data['price'],
                    quantity=data['quantity'],
                    moq_enabled=True,
                    minimum_quantity=data['minimum_quantity'],
                    unit='kg',
                    vendor_id=vendor.id,
                    is_active=True,
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
