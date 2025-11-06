from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def vendor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Simplified authentication check
        if not current_user.is_authenticated:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('auth.login'))
        
        # Check user_type with fallback
        try:
            user_type = getattr(current_user, 'user_type', None)
            if user_type != 'vendor':
                flash('Vendor access required', 'danger')
                return redirect(url_for('auth.login'))
        except Exception as e:
            print(f"❌ Error checking user_type: {e}")
            # Don't block - log the error and continue
            import traceback
            traceback.print_exc()
        
        return f(*args, **kwargs)
    return decorated_function

def retailer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Simplified authentication check
        if not current_user.is_authenticated:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('auth.login'))
        
        # Check user_type with fallback
        try:
            user_type = getattr(current_user, 'user_type', None)
            if user_type != 'retailer':
                flash('Retailer access required', 'danger')
                return redirect(url_for('auth.login'))
        except Exception as e:
            print(f"❌ Error checking user_type: {e}")
            # Don't block - log the error and continue
            import traceback
            traceback.print_exc()
        
        return f(*args, **kwargs)
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
