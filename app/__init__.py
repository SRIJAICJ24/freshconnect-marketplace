from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from config import config_by_name
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    # Enable CORS for all routes
    CORS(app)
    
    db.init_app(app)
    
    # Configure login manager with better session handling
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in'
    login_manager.session_protection = 'strong'  # Protect against session hijacking
    login_manager.refresh_view = 'auth.login'
    
    # Make sessions permanent by default
    @app.before_request
    def make_session_permanent():
        from flask import session
        session.permanent = True
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    with app.app_context():
        from app.routes import main, auth, vendor, retailer, driver, admin, api, payment, barcode, emergency, vendor_barcode, admin_inventory, order_tracking, reviews, reports, notifications, vision, voice, admin_seed, comparison, emergency_migration
        
        app.register_blueprint(main.bp)
        app.register_blueprint(auth.bp)
        app.register_blueprint(vendor.bp)
        app.register_blueprint(retailer.bp)
        app.register_blueprint(driver.bp)
        app.register_blueprint(admin.bp)
        app.register_blueprint(api.bp)
        app.register_blueprint(payment.bp)
        app.register_blueprint(barcode.bp)  # FEATURE 2: Barcode tracking
        app.register_blueprint(emergency.bp)  # EMERGENCY MARKETPLACE: Sell expiring products
        app.register_blueprint(vendor_barcode.bp)  # FEATURE 3: Vendor barcode scanning
        app.register_blueprint(admin_inventory.bp)  # FEATURE 3: Admin inventory management
        app.register_blueprint(order_tracking.bp)  # FEATURE 5: Order tracking (4-step process)
        app.register_blueprint(reviews.bp)  # FEATURE 6: Reviews & Ratings
        app.register_blueprint(reports.bp)  # FEATURE 7: Report System
        app.register_blueprint(notifications.bp)  # FEATURE 8: Emergency Notifications
        app.register_blueprint(vision.bp)  # FEATURE 2: Camera & Image Recognition
        app.register_blueprint(voice.bp)  # FEATURE 1: Voice Assistant (Tamil + English)
        app.register_blueprint(comparison.bp)  # FEATURE 9: Vendor Comparison & Differentiation
        app.register_blueprint(emergency_migration.bp)  # EMERGENCY: Database migration from browser
        app.register_blueprint(admin_seed.bp)  # DATABASE SEEDING: Import local data to Railway
        
        try:
            db.create_all()
            print("✅ Database tables created successfully!")
        except Exception as e:
            print(f"⚠️ Database init warning: {e}")
            print("Database tables will be created on first request")
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', code=404, message='Page Not Found'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return render_template('error.html', code=500, message='Server Error'), 500
    
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception as e:
            print(f"❌ User loader error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    return app
