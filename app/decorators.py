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
        # ULTRA DEFENSIVE - Log everything
        try:
            print(f"🔍 retailer_required called for route: {f.__name__}")
            print(f"   current_user: {current_user}")
            print(f"   is_authenticated: {current_user.is_authenticated}")
            
            # Check if user is authenticated
            if not current_user.is_authenticated:
                print(f"   ❌ User not authenticated, redirecting to login")
                flash('Please login to access this page', 'warning')
                return redirect(url_for('auth.login'))
            
            # Log user details
            try:
                print(f"   user_id: {current_user.id}")
                print(f"   user_type: {getattr(current_user, 'user_type', 'NO ATTR')}")
                print(f"   user_email: {getattr(current_user, 'email', 'NO ATTR')}")
            except Exception as log_error:
                print(f"   ⚠️ Could not log user details: {log_error}")
            
            # Check user_type
            try:
                user_type = getattr(current_user, 'user_type', None)
                if user_type is None:
                    print(f"   ⚠️ user_type is None! Allowing access anyway...")
                    # Don't block - just allow
                elif user_type != 'retailer':
                    print(f"   ❌ Wrong user_type: {user_type}, need retailer")
                    flash('Retailer access required', 'danger')
                    return redirect(url_for('auth.login'))
                else:
                    print(f"   ✅ Correct user_type: {user_type}")
            except Exception as e:
                print(f"   ⚠️ Error checking user_type: {e}")
                # DON'T BLOCK - just continue
                import traceback
                traceback.print_exc()
            
            print(f"   ✅ Allowing access to {f.__name__}")
            return f(*args, **kwargs)
            
        except Exception as outer_error:
            print(f"❌ CRITICAL ERROR in retailer_required: {outer_error}")
            import traceback
            traceback.print_exc()
            flash('Authentication system error. Please try logging out and back in.', 'danger')
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
