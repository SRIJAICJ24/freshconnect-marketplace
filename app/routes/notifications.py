"""
Notification Management Routes
Admin can manually trigger notifications
Vendors can view their notification history
"""

from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import current_user, login_required
from app import db
from app.models import Product
from app.decorators import admin_required, vendor_required
from app.notification_service import NotificationService
from datetime import datetime, timedelta

bp = Blueprint('notifications', __name__, url_prefix='/notifications')


@bp.route('/admin/trigger', methods=['GET', 'POST'])
@admin_required
def admin_trigger():
    """Admin can manually trigger notification check"""
    
    if request.method == 'POST':
        results = NotificationService.send_bulk_expiry_notifications()
        flash(f'Notifications sent! {results["notified"]} vendors notified, {results["hidden"]} products auto-hidden.', 'success')
        return redirect(url_for('notifications.admin_dashboard'))
    
    # Show preview of what will be notified
    vendors_products = NotificationService.check_expiring_products(days_threshold=7)
    
    return render_template('notifications/admin_trigger.html',
                         vendors_products=vendors_products)


@bp.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard for notification management"""
    
    # Get stats
    expiring_soon = Product.query.filter(
        Product.expiry_date <= datetime.now().date() + timedelta(days=7),
        Product.expiry_date >= datetime.now().date(),
        Product.is_active == True
    ).count()
    
    already_expired = Product.query.filter(
        Product.expiry_date < datetime.now().date(),
        Product.is_active == False
    ).count()
    
    in_emergency = Product.query.filter(
        Product.in_emergency_marketplace == True,
        Product.is_active == True
    ).count()
    
    stats = {
        'expiring_soon': expiring_soon,
        'already_expired': already_expired,
        'in_emergency': in_emergency
    }
    
    return render_template('notifications/admin_dashboard.html', stats=stats)


@bp.route('/vendor/expiring')
@vendor_required
def vendor_expiring():
    """Vendor view of their expiring products"""
    
    # Get vendor's products expiring in next 7 days
    expiring_products = Product.query.filter(
        Product.vendor_id == current_user.id,
        Product.expiry_date <= datetime.now().date() + timedelta(days=7),
        Product.expiry_date >= datetime.now().date(),
        Product.is_active == True
    ).all()
    
    # Calculate urgency for each
    for product in expiring_products:
        days_left = (product.expiry_date - datetime.now().date()).days
        if days_left <= 2:
            product.urgency = 'critical'
            product.urgency_color = 'danger'
        elif days_left <= 4:
            product.urgency = 'high'
            product.urgency_color = 'warning'
        else:
            product.urgency = 'moderate'
            product.urgency_color = 'info'
    
    return render_template('notifications/vendor_expiring.html',
                         products=expiring_products)


@bp.route('/api/check-expiring')
@login_required
def api_check_expiring():
    """API endpoint to get count of expiring products for current vendor"""
    
    if current_user.user_type != 'vendor':
        return jsonify({'count': 0})
    
    count = Product.query.filter(
        Product.vendor_id == current_user.id,
        Product.expiry_date <= datetime.now().date() + timedelta(days=7),
        Product.expiry_date >= datetime.now().date(),
        Product.is_active == True,
        Product.is_emergency == False
    ).count()
    
    return jsonify({'count': count})
