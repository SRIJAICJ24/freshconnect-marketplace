from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def vendor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if not current_user.is_authenticated:
                flash('Please login to access this page', 'warning')
                return redirect(url_for('auth.login'))
            
            if current_user.user_type != 'vendor':
                flash('Vendor access required', 'danger')
                return redirect(url_for('auth.login'))
            
            return f(*args, **kwargs)
        except Exception as e:
            print(f"❌ Decorator error in vendor_required: {e}")
            import traceback
            traceback.print_exc()
            flash('Authentication error. Please login again.', 'danger')
            return redirect(url_for('auth.login'))
    return decorated_function

def retailer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if not current_user.is_authenticated:
                flash('Please login to access this page', 'warning')
                return redirect(url_for('auth.login'))
            
            # More defensive check with better error message
            if not hasattr(current_user, 'user_type'):
                flash('Session expired. Please login again.', 'warning')
                return redirect(url_for('auth.logout'))
            
            if current_user.user_type != 'retailer':
                flash('Retailer access required', 'danger')
                return redirect(url_for('auth.login'))
            
            return f(*args, **kwargs)
        except AttributeError as e:
            print(f"❌ AttributeError in retailer_required: {e}")
            print(f"   Current user: {current_user}")
            print(f"   Is authenticated: {current_user.is_authenticated}")
            flash('Session expired. Please logout and login again.', 'warning')
            return redirect(url_for('auth.logout'))
        except Exception as e:
            print(f"❌ Decorator error in retailer_required: {e}")
            import traceback
            traceback.print_exc()
            flash('Authentication error. Please logout and login again.', 'danger')
            return redirect(url_for('auth.logout'))
    return decorated_function

def driver_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'driver':
            flash('Driver access required', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
