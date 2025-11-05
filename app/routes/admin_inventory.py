"""
Admin Inventory Management Routes
Admin creates inventory with barcodes for vendors to claim
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app import db
from app.models import AdminGeneratedStock
from app.decorators import admin_required
from datetime import datetime
import random
import string

bp = Blueprint('admin_inventory', __name__, url_prefix='/admin/inventory')


def generate_unique_code():
    """Generate unique barcode like FC20251104001"""
    timestamp = datetime.now().strftime('%Y%m%d')
    random_suffix = ''.join(random.choices(string.digits, k=3))
    return f"FC{timestamp}{random_suffix}"


@bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create_stock():
    """Admin creates new inventory with barcode"""
    
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        category = request.form.get('category')
        weight = float(request.form.get('weight'))
        unit = request.form.get('unit', 'kg')
        price = float(request.form.get('price'))
        expiry_date_str = request.form.get('expiry_date')
        
        # Generate unique barcode
        barcode = generate_unique_code()
        
        # Ensure uniqueness
        while AdminGeneratedStock.query.filter_by(admin_generated_code=barcode).first():
            barcode = generate_unique_code()
        
        # Parse expiry date
        expiry_date = None
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
            except:
                pass
        
        # Create stock
        stock = AdminGeneratedStock(
            admin_generated_code=barcode,
            product_name=product_name,
            category=category,
            weight=weight,
            unit=unit,
            price=price,
            expiry_date=expiry_date,
            created_by_admin_id=current_user.id
        )
        
        db.session.add(stock)
        db.session.commit()
        
        flash(f'Stock created successfully! Barcode: {barcode}', 'success')
        return redirect(url_for('admin_inventory.view_stocks'))
    
    return render_template('admin/create_inventory.html')


@bp.route('/stocks', methods=['GET'])
@admin_required
def view_stocks():
    """View all admin-generated stocks"""
    
    # Get filter
    filter_type = request.args.get('filter', 'all')
    
    query = AdminGeneratedStock.query
    
    if filter_type == 'unclaimed':
        query = query.filter_by(is_claimed_by_vendor=False)
    elif filter_type == 'claimed':
        query = query.filter_by(is_claimed_by_vendor=True)
    
    stocks = query.order_by(AdminGeneratedStock.created_at.desc()).all()
    
    # Stats
    total_stocks = AdminGeneratedStock.query.count()
    unclaimed = AdminGeneratedStock.query.filter_by(is_claimed_by_vendor=False).count()
    claimed = AdminGeneratedStock.query.filter_by(is_claimed_by_vendor=True).count()
    
    return render_template('admin/view_inventory.html',
                         stocks=stocks,
                         filter_type=filter_type,
                         total_stocks=total_stocks,
                         unclaimed=unclaimed,
                         claimed=claimed)


@bp.route('/delete/<int:stock_id>', methods=['POST'])
@admin_required
def delete_stock(stock_id):
    """Delete an unclaimed stock"""
    
    stock = AdminGeneratedStock.query.get_or_404(stock_id)
    
    if stock.is_claimed_by_vendor:
        flash('Cannot delete claimed stock!', 'danger')
        return redirect(url_for('admin_inventory.view_stocks'))
    
    db.session.delete(stock)
    db.session.commit()
    
    flash('Stock deleted successfully!', 'success')
    return redirect(url_for('admin_inventory.view_stocks'))
