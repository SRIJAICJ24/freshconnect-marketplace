"""
FEATURE 2: Barcode-Based Inventory Management
Routes for barcode scanning and stock management
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import BarcodeTrack, Product, User
from app.decorators import vendor_required, retailer_required
from datetime import datetime
import random
import string

bp = Blueprint('barcode', __name__, url_prefix='/barcode')


def generate_barcode():
    """Generate mock barcode number"""
    return 'BC' + ''.join(random.choices(string.digits, k=12))


@bp.route('/scan', methods=['GET', 'POST'])
@login_required
def scan_barcode():
    """Vendor/Retailer scans barcode"""
    
    if request.method == 'POST':
        barcode = request.form.get('barcode_input', '').strip()
        
        if not barcode:
            flash('Please enter a barcode', 'warning')
            return redirect(url_for('barcode.scan_barcode'))
        
        # Find barcode
        barcode_track = BarcodeTrack.query.filter_by(barcode_number=barcode).first()
        
        if not barcode_track:
            flash('❌ Barcode not found', 'danger')
            return redirect(url_for('barcode.scan_barcode'))
        
        # Check if receiver is current user
        if barcode_track.receiver_id != current_user.id:
            flash('❌ This barcode is not for you', 'danger')
            return redirect(url_for('barcode.scan_barcode'))
        
        if barcode_track.status != 'in_transit':
            flash(f'⚠️ Barcode already processed (Status: {barcode_track.status})', 'warning')
            return redirect(url_for('barcode.scan_barcode'))
        
        # Mark as scanned
        barcode_track.status = 'scanned'
        barcode_track.scanned_at = datetime.utcnow()
        db.session.commit()
        
        # Show confirmation dialog (Tamil + English)
        return render_template('barcode/confirm_stock.html',
                             barcode=barcode_track,
                             product=barcode_track.product)
    
    # GET: Show scan form
    # Also show recent barcodes for this user
    recent_barcodes = BarcodeTrack.query.filter_by(
        receiver_id=current_user.id
    ).order_by(BarcodeTrack.created_at.desc()).limit(10).all()
    
    return render_template('barcode/scan.html', recent_barcodes=recent_barcodes)


@bp.route('/confirm/<int:barcode_id>', methods=['POST'])
@login_required
def confirm_add_to_stock(barcode_id):
    """User confirms adding to stock"""
    
    try:
        barcode_track = BarcodeTrack.query.get_or_404(barcode_id)
        
        # Verify ownership
        if barcode_track.receiver_id != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Add to product inventory
        product = barcode_track.product
        old_quantity = product.quantity
        product.quantity += barcode_track.quantity
        
        # Update barcode status
        barcode_track.status = 'added_to_stock'
        barcode_track.added_to_stock_at = datetime.utcnow()
        
        db.session.commit()
        
        print(f"[BARCODE] {current_user.name} scanned and added {barcode_track.quantity} {barcode_track.unit} of {product.product_name}")
        print(f"[INVENTORY] {product.product_name}: {old_quantity} → {product.quantity} {product.unit}")
        
        return jsonify({
            'success': True,
            'message': f'✅ {barcode_track.quantity} {barcode_track.unit} added to {product.product_name} stock',
            'product_name': product.product_name,
            'quantity': barcode_track.quantity,
            'old_total': old_quantity,
            'new_total': product.quantity
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"[BARCODE ERROR] {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/reject/<int:barcode_id>', methods=['POST'])
@login_required
def reject_barcode(barcode_id):
    """User rejects/returns items"""
    
    try:
        barcode_track = BarcodeTrack.query.get_or_404(barcode_id)
        
        if barcode_track.receiver_id != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        barcode_track.status = 'rejected'
        db.session.commit()
        
        print(f"[BARCODE] {current_user.name} rejected barcode {barcode_track.barcode_number}")
        
        return jsonify({
            'success': True,
            'message': '⚠️ Item rejected. Return process initiated.'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/generate/<int:order_id>')
@login_required
def generate_for_order(order_id):
    """Generate barcode for an order (vendor uses this)"""
    from app.models import Order
    
    try:
        order = Order.query.get_or_404(order_id)
        
        # Verify user is the seller
        if order.seller_id != current_user.id:
            flash('Unauthorized', 'danger')
            return redirect(url_for('vendor.orders'))
        
        # Check if barcode already exists
        existing_barcode = BarcodeTrack.query.filter_by(order_id=order_id).first()
        if existing_barcode:
            flash(f'Barcode already exists: {existing_barcode.barcode_number}', 'info')
            return redirect(url_for('vendor.orders'))
        
        # Generate new barcode
        barcode = BarcodeTrack(
            barcode_number=generate_barcode(),
            order_id=order_id,
            product_id=order.items[0].product_id if order.items else None,
            sender_id=current_user.id,
            receiver_id=order.buyer_id,
            status='in_transit',
            quantity=sum(item.quantity for item in order.items),
            unit=order.items[0].product.unit if order.items else 'kg'
        )
        
        db.session.add(barcode)
        db.session.commit()
        
        flash(f'✅ Barcode generated: {barcode.barcode_number}', 'success')
        return redirect(url_for('vendor.orders'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('vendor.orders'))


@bp.route('/list')
@login_required
def list_barcodes():
    """List all barcodes for current user"""
    
    # Barcodes user will receive
    incoming = BarcodeTrack.query.filter_by(receiver_id=current_user.id).order_by(
        BarcodeTrack.created_at.desc()
    ).all()
    
    # Barcodes user sent
    outgoing = BarcodeTrack.query.filter_by(sender_id=current_user.id).order_by(
        BarcodeTrack.created_at.desc()
    ).all()
    
    return render_template('barcode/list.html', 
                          incoming=incoming, 
                          outgoing=outgoing)
