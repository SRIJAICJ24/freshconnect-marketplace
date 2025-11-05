"""
Order Tracking Routes
4-step tracking: Payment → Shipped → Ready → Delivered
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import Order, OrderStatusLog
from app.decorators import vendor_required, driver_required
from datetime import datetime

bp = Blueprint('order_tracking', __name__, url_prefix='/orders')


@bp.route('/<int:order_id>/track', methods=['GET'])
@login_required
def track_order(order_id):
    """View order tracking status (accessible by buyer, seller, driver)"""
    
    order = Order.query.get_or_404(order_id)
    
    # Check access permission
    if current_user.user_type == 'retailer' and order.buyer_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('retailer.dashboard'))
    
    if current_user.user_type == 'vendor' and order.seller_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('vendor.dashboard'))
    
    # Get status log
    status_logs = OrderStatusLog.query.filter_by(
        order_id=order_id
    ).order_by(OrderStatusLog.changed_at.desc()).all()
    
    # Calculate progress percentage
    progress = get_order_progress(order)
    
    return render_template('orders/track_order.html',
                         order=order,
                         status_logs=status_logs,
                         progress=progress)


@bp.route('/<int:order_id>/update-status', methods=['POST'])
@login_required
def update_order_status(order_id):
    """Update order status (vendor/driver only)"""
    
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('new_status')
    
    # Permission check
    if current_user.user_type == 'vendor' and order.seller_id != current_user.id:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('vendor.orders'))
    
    if current_user.user_type == 'driver' and order.assigned_driver_id != current_user.id:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('driver.assignments'))
    
    # Validate status transition
    if not is_valid_transition(order.order_status, new_status):
        flash(f'Invalid status transition from {order.order_status} to {new_status}', 'danger')
        return redirect(url_for('order_tracking.track_order', order_id=order_id))
    
    # Log status change
    log_entry = OrderStatusLog(
        order_id=order_id,
        status_from=order.order_status,
        status_to=new_status,
        changed_by_id=current_user.id,
        changed_at=datetime.utcnow()
    )
    db.session.add(log_entry)
    
    # Update order status
    old_status = order.order_status
    order.order_status = new_status
    
    # Update timestamp fields
    now = datetime.utcnow()
    if new_status == 'payment_confirmed':
        order.payment_confirmed_at = now
    elif new_status == 'shipped':
        order.shipped_in_truck_at = now
    elif new_status == 'out_for_delivery':
        order.ready_for_delivery_at = now
    elif new_status == 'delivered':
        order.delivered_at = now
        order.payment_status = 'paid'  # Mark payment as complete
    
    db.session.commit()
    
    flash(f'Order status updated from {old_status} to {new_status}', 'success')
    
    # Redirect based on user type
    if current_user.user_type == 'vendor':
        return redirect(url_for('vendor.orders'))
    elif current_user.user_type == 'driver':
        return redirect(url_for('driver.assignments'))
    else:
        return redirect(url_for('order_tracking.track_order', order_id=order_id))


@bp.route('/<int:order_id>/status', methods=['GET'])
@login_required
def get_order_status(order_id):
    """API endpoint to get current order status (for AJAX updates)"""
    
    order = Order.query.get_or_404(order_id)
    
    # Check access
    if (current_user.user_type == 'retailer' and order.buyer_id != current_user.id and
        current_user.user_type == 'vendor' and order.seller_id != current_user.id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    progress = get_order_progress(order)
    
    return jsonify({
        'order_id': order.id,
        'status': order.order_status,
        'progress': progress,
        'timestamps': {
            'payment_confirmed': order.payment_confirmed_at.isoformat() if order.payment_confirmed_at else None,
            'shipped': order.shipped_in_truck_at.isoformat() if order.shipped_in_truck_at else None,
            'ready': order.ready_for_delivery_at.isoformat() if order.ready_for_delivery_at else None,
            'delivered': order.delivered_at.isoformat() if order.delivered_at else None
        }
    })


def get_order_progress(order):
    """Calculate order progress percentage"""
    
    steps_completed = 0
    total_steps = 4
    
    if order.payment_confirmed_at:
        steps_completed += 1
    if order.shipped_in_truck_at:
        steps_completed += 1
    if order.ready_for_delivery_at:
        steps_completed += 1
    if order.delivered_at:
        steps_completed += 1
    
    return {
        'percentage': int((steps_completed / total_steps) * 100),
        'steps_completed': steps_completed,
        'total_steps': total_steps,
        'current_step': get_current_step_name(order)
    }


def get_current_step_name(order):
    """Get human-readable current step"""
    
    if order.delivered_at:
        return 'Delivered'
    elif order.ready_for_delivery_at:
        return 'Out for Delivery'
    elif order.shipped_in_truck_at:
        return 'Shipped'
    elif order.payment_confirmed_at:
        return 'Payment Confirmed'
    else:
        return 'Pending Payment'


def is_valid_transition(current_status, new_status):
    """Validate status transitions to prevent invalid jumps"""
    
    # Define valid transitions
    valid_transitions = {
        'pending': ['payment_confirmed', 'cancelled'],
        'payment_confirmed': ['shipped', 'cancelled'],
        'shipped': ['out_for_delivery', 'cancelled'],
        'out_for_delivery': ['delivered', 'failed'],
        'delivered': [],  # Final state
        'cancelled': [],  # Final state
        'failed': ['out_for_delivery']  # Can retry delivery
    }
    
    return new_status in valid_transitions.get(current_status, [])
