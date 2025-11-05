from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Order, Payment, Product, OrderStatusLog
from app.decorators import retailer_required
from app.payment_service import MockPaymentGateway
from app.driver_service import MockDriverService
from datetime import datetime

bp = Blueprint('payment', __name__, url_prefix='/payment')

@bp.route('/bill/<int:order_id>')
@retailer_required
def bill_summary(order_id):
    """Show detailed bill before payment"""
    order = Order.query.get_or_404(order_id)
    
    if order.buyer_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('retailer.orders'))
    
    # Calculate cart items with amounts
    cart_items = []
    product_total = 0
    total_weight = 0
    total_volume = 0
    
    for item in order.items:
        amount = item.price_at_purchase * item.quantity
        product_total += amount
        total_weight += item.quantity
        total_volume += item.quantity * 0.001  # Rough volume estimate: 1kg = 0.001m³
        
        cart_items.append({
            'product': item.product,
            'quantity': item.quantity,
            'amount': amount
        })
    
    # Calculate delivery costs
    volume_charge = total_volume * 100  # ₹100 per m³
    weight_charge = total_weight * 10   # ₹10 per kg
    detour_charge = 100  # Base distance charge (can be calculated from location)
    delivery_cost = volume_charge + weight_charge + detour_charge
    
    delivery_breakdown = {
        'volume': round(total_volume, 2),
        'volume_charge': volume_charge,
        'weight': round(total_weight, 1),
        'weight_charge': weight_charge,
        'distance': 2,  # km (can be calculated)
        'detour_charge': detour_charge
    }
    
    # Calculate tax
    tax = product_total * 0.05  # 5% tax
    
    # Grand total
    grand_total = product_total + delivery_cost + tax
    
    return render_template('payment/bill_summary.html',
                         order=order,
                         cart_items=cart_items,
                         product_total=product_total,
                         delivery_cost=delivery_cost,
                         delivery_breakdown=delivery_breakdown,
                         tax=tax,
                         grand_total=grand_total)

@bp.route('/checkout/<int:order_id>', methods=['GET', 'POST'])
@retailer_required
def checkout(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.buyer_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('retailer.orders'))
    
    if request.method == 'POST':
        card_number = request.form.get('card_number')
        expiry = request.form.get('expiry')
        cvv = request.form.get('cvv')
        
        result = MockPaymentGateway.process_payment(
            order_id,
            card_number,
            expiry,
            cvv,
            order.total_amount
        )
        
        if result['success']:
            # Update order status and timestamp
            old_status = order.order_status
            order.order_status = 'payment_confirmed'
            order.payment_confirmed_at = datetime.utcnow()
            order.payment_status = 'paid'
            
            # Log status change
            status_log = OrderStatusLog(
                order_id=order_id,
                status_from=old_status,
                status_to='payment_confirmed',
                changed_by_id=current_user.id,
                changed_at=datetime.utcnow()
            )
            db.session.add(status_log)
            
            # Assign driver
            MockDriverService.assign_driver_to_order(
                order_id,
                sum(item.quantity for item in order.items),
                order.delivery_address
            )
            
            db.session.commit()
            
            flash('Payment successful! Driver assigned. Track your order now.', 'success')
            return redirect(url_for('order_tracking.track_order', order_id=order_id))
        else:
            flash(f'Payment failed: {result["message"]}', 'danger')
            return redirect(url_for('payment.checkout', order_id=order_id))
    
    return render_template('payment/checkout.html', order=order)

@bp.route('/success/<int:order_id>')
@retailer_required
def success(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.buyer_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('retailer.orders'))
    
    return render_template('payment/success.html', order=order)
