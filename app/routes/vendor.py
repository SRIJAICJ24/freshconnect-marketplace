from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Product, Order, OrderItem
from app.decorators import vendor_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta

bp = Blueprint('vendor', __name__, url_prefix='/vendor')

@bp.route('/dashboard')
@vendor_required
def dashboard():
    total_products = Product.query.filter_by(vendor_id=current_user.id).count()
    total_orders = Order.query.filter_by(seller_id=current_user.id).count()
    
    recent_orders = Order.query.filter_by(
        seller_id=current_user.id
    ).order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('vendor/dashboard.html',
                         total_products=total_products,
                         total_orders=total_orders,
                         recent_orders=recent_orders)

@bp.route('/add-product', methods=['GET', 'POST'])
@vendor_required
def add_product():
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        category = request.form.get('category')
        price = request.form.get('price')
        quantity = request.form.get('quantity')
        unit = request.form.get('unit', 'kg')
        expiry_date = request.form.get('expiry_date')
        
        moq_enabled = request.form.get('moq_enabled') == 'on'
        moq_type = request.form.get('moq_type') if moq_enabled else None
        minimum_quantity = request.form.get('minimum_quantity') if moq_enabled else None
        
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(f"{current_user.id}_{datetime.now().timestamp()}_{file.filename}")
                file.save(os.path.join('app/static/images/products', filename))
                image_filename = filename
        
        product = Product(
            vendor_id=current_user.id,
            product_name=product_name,
            category=category,
            price=float(price),
            quantity=float(quantity),
            unit=unit,
            expiry_date=datetime.strptime(expiry_date, '%Y-%m-%d').date() if expiry_date else None,
            image_filename=image_filename,
            moq_enabled=moq_enabled,
            moq_type=moq_type,
            minimum_quantity=float(minimum_quantity) if minimum_quantity else None
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('vendor.products'))
    
    return render_template('vendor/add_product.html')

@bp.route('/products')
@vendor_required
def products():
    vendor_products = Product.query.filter_by(
        vendor_id=current_user.id
    ).order_by(Product.created_at.desc()).all()
    
    return render_template('vendor/products.html', products=vendor_products)

@bp.route('/orders')
@vendor_required
def orders():
    vendor_orders = Order.query.filter_by(
        seller_id=current_user.id
    ).order_by(Order.created_at.desc()).all()
    
    return render_template('vendor/orders.html', orders=vendor_orders)
