"""
Vendor Barcode Scanning Routes
Vendors scan admin-generated barcodes to claim inventory
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app import db
from app.models import AdminGeneratedStock, Product
from app.decorators import vendor_required
from datetime import datetime

bp = Blueprint('vendor_barcode', __name__, url_prefix='/vendor/barcode')


@bp.route('/scan', methods=['GET'])
@vendor_required
def scan_page():
    """Barcode scanning page for vendors"""
    
    # Get vendor's claimed stocks
    claimed_stocks = AdminGeneratedStock.query.filter_by(
        claimed_by_vendor_id=current_user.id,
        is_claimed_by_vendor=True
    ).order_by(AdminGeneratedStock.claimed_at.desc()).all()
    
    # Get available (unclaimed) stocks for vendors to see
    available_stocks = AdminGeneratedStock.query.filter_by(
        is_claimed_by_vendor=False
    ).order_by(AdminGeneratedStock.created_at.desc()).all()
    
    return render_template('vendor/scan_barcode.html',
                         claimed_stocks=claimed_stocks,
                         available_stocks=available_stocks)


@bp.route('/claim', methods=['POST'])
@vendor_required
def claim_stock():
    """Vendor claims a stock by scanning barcode"""
    
    try:
        data = request.get_json()
        barcode = data.get('barcode', '').strip()
        
        if not barcode:
            return jsonify({
                'success': False,
                'message': 'Please enter or scan a barcode'
            }), 400
        
        # Find the admin-generated stock
        stock = AdminGeneratedStock.query.filter_by(
            admin_generated_code=barcode
        ).first()
        
        if not stock:
            return jsonify({
                'success': False,
                'message': f'Barcode "{barcode}" not found in system'
            }), 404
        
        # Check if already claimed
        if stock.is_claimed_by_vendor:
            claimed_by_name = stock.claimed_by_vendor.business_name or stock.claimed_by_vendor.name
            return jsonify({
                'success': False,
                'message': f'This stock was already claimed by {claimed_by_name}'
            }), 400
        
        # Create product in vendor's inventory
        product = Product(
            vendor_id=current_user.id,
            product_name=stock.product_name,
            category=stock.category,
            price=stock.price,
            quantity=stock.weight,
            unit=stock.unit,
            expiry_date=stock.expiry_date,
            is_active=True
        )
        
        db.session.add(product)
        db.session.flush()  # Get product ID
        
        # Mark stock as claimed
        stock.is_claimed_by_vendor = True
        stock.claimed_by_vendor_id = current_user.id
        stock.claimed_at = datetime.utcnow()
        stock.product_id = product.id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully added {stock.product_name} to your inventory!',
            'product': {
                'id': product.id,
                'name': product.product_name,
                'category': product.category,
                'quantity': product.quantity,
                'unit': product.unit,
                'price': product.price
            }
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error claiming stock: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error adding product: {str(e)}'
        }), 500


@bp.route('/history', methods=['GET'])
@vendor_required
def claim_history():
    """View vendor's claim history"""
    
    claimed_stocks = AdminGeneratedStock.query.filter_by(
        claimed_by_vendor_id=current_user.id,
        is_claimed_by_vendor=True
    ).order_by(AdminGeneratedStock.claimed_at.desc()).all()
    
    return render_template('vendor/barcode_history.html',
                         claimed_stocks=claimed_stocks)


@bp.route('/check/<barcode>', methods=['GET'])
@vendor_required
def check_barcode(barcode):
    """Check if a barcode exists and is available"""
    
    stock = AdminGeneratedStock.query.filter_by(
        admin_generated_code=barcode
    ).first()
    
    if not stock:
        return jsonify({
            'exists': False,
            'message': 'Barcode not found'
        })
    
    if stock.is_claimed_by_vendor:
        return jsonify({
            'exists': True,
            'available': False,
            'message': f'Already claimed by {stock.claimed_by_vendor.business_name or stock.claimed_by_vendor.name}',
            'claimed_at': stock.claimed_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return jsonify({
        'exists': True,
        'available': True,
        'product': {
            'name': stock.product_name,
            'category': stock.category,
            'weight': stock.weight,
            'unit': stock.unit,
            'price': stock.price,
            'expiry_date': stock.expiry_date.strftime('%Y-%m-%d') if stock.expiry_date else None
        }
    })
