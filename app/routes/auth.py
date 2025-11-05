from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app import db
from app.models import User, RetailerCredit

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        user_type = request.form.get('user_type')
        phone = request.form.get('phone')
        city = request.form.get('city')
        
        if not all([name, email, password, user_type]):
            flash('All fields required', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('auth.register'))
        
        user = User(
            name=name,
            email=email,
            user_type=user_type,
            phone=phone,
            city=city,
            is_active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.flush()
        
        if user_type == 'retailer':
            credit = RetailerCredit(retailer_id=user.id)
            db.session.add(credit)
        
        db.session.commit()
        
        flash(f'Account created! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            print(f"✅ User {user.id} ({user.user_type}) logged in successfully")
            flash('Logged in successfully!', 'success')
            
            try:
                return redirect(url_for('main.dashboard'))
            except Exception as e:
                print(f"❌ Redirect error: {e}")
                # Direct redirect based on user type
                if user.user_type == 'retailer':
                    return redirect(url_for('retailer.dashboard'))
                elif user.user_type == 'vendor':
                    return redirect(url_for('vendor.dashboard'))
                elif user.user_type == 'driver':
                    return redirect(url_for('driver.dashboard'))
                elif user.user_type == 'admin':
                    return redirect(url_for('admin.dashboard'))
                else:
                    return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('main.index'))
