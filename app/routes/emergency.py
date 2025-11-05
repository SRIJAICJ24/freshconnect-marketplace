from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Product, EmergencyMarketplaceMetrics
from app.decorators import vendor_required, retailer_required, admin_required
from app.emergency_marketplace_service import EmergencyMarketplaceService
from datetime import datetime

bp = Blueprint('emergency', __name__, url_prefix='/emergency')

# ============================================================================
# VENDOR ROUTES - Mark & Manage Emergency Sales
# ============================================================================

@bp.route('/vendor/dashboard')
@vendor_required
def vendor_dashboard():
    """Vendor dashboard for managing emergency sales"""
    
    # Get vendor's emergency products
    emergency_products = Product.query.filter_by(
        vendor_id=current_user.id,
        is_emergency=True
    ).all()
    
    # Get vendor's eligible products (expiring soon)
    eligible_products = Product.query.filter_by(
        vendor_id=current_user.id,
        is_active=True,
        is_emergency=False
    ).all()
    
    # Calculate metrics for this vendor
    total_original_value = sum(
        (p.original_price_backup or p.price) * p.quantity 
        for p in emergency_products
    )
    
    total_current_value = sum(p.price * p.quantity for p in emergency_products)
    total_discount = total_original_value - total_current_value
    
    return render_template('emergency/vendor_dashboard.html',
                         emergency_products=emergency_products,
                         eligible_products=eligible_products,
                         total_emergency=len(emergency_products),
                         total_original_value=total_original_value,
                         total_discount=total_discount,
                         total_current_value=total_current_value)


@bp.route('/vendor/mark/<int:product_id>', methods=['GET', 'POST'])
@vendor_required
def mark_emergency(product_id):
    """Mark product as emergency sale"""
    
    product = Product.query.get_or_404(product_id)
    
    if product.vendor_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('emergency.vendor_dashboard'))
    
    if request.method == 'POST':
        discount = float(request.form.get('discount', 30))
        
        success, message = EmergencyMarketplaceService.mark_vendor_product_emergency(
            product_id, discount, current_user.id
        )
        
        if success:
            flash(f"✓ {message['product_name']} marked as emergency! New price: ₹{message['new_price']:.2f}", 'success')
            return redirect(url_for('emergency.vendor_dashboard'))
        else:
            flash(f"Error: {message}", 'danger')
    
    return render_template('emergency/mark_emergency.html', product=product)


@bp.route('/vendor/remove/<int:product_id>', methods=['POST'])
@vendor_required
def remove_emergency(product_id):
    """Remove product from emergency sale"""
    
    success, message = EmergencyMarketplaceService.remove_emergency_status(product_id, current_user.id)
    
    if success:
        flash(f"✓ {message}", 'success')
    else:
        flash(f"Error: {message}", 'danger')
    
    return redirect(url_for('emergency.vendor_dashboard'))


# ============================================================================
# RETAILER ROUTES - Browse & Buy Emergency Products
# ============================================================================

@bp.route('/marketplace')
@retailer_required
def marketplace():
    """Emergency marketplace for retailers"""
    
    # Get parameters
    category = request.args.get('category', None)
    min_discount = int(request.args.get('min_discount', 0))
    sort_by = request.args.get('sort', 'urgency')
    
    # Get emergency products
    products = EmergencyMarketplaceService.get_emergency_marketplace_products(
        category=category,
        min_discount=min_discount,
        sort_by=sort_by
    )
    
    # Get categories
    categories = EmergencyMarketplaceService.get_emergency_categories()
    
    # Statistics
    total_products = len(products)
    total_savings = sum(
        ((p.original_price_backup or p.price) - p.price) * p.quantity 
        for p in products
    )
    
    return render_template('emergency/marketplace.html',
                         products=products,
                         categories=categories,
                         total_products=total_products,
                         total_savings=total_savings,
                         selected_category=category,
                         selected_discount=min_discount,
                         sort_by=sort_by)


@bp.route('/product/<int:product_id>')
@retailer_required
def product_detail(product_id):
    """Emergency product detail page"""
    
    product = Product.query.get_or_404(product_id)
    
    if not product.is_emergency:
        flash('Product not in emergency marketplace', 'danger')
        return redirect(url_for('emergency.marketplace'))
    
    # Calculate savings
    original_price = product.original_price_backup or product.price
    savings = (original_price - product.price) * product.quantity
    
    return render_template('emergency/product_detail.html',
                         product=product,
                         original_price=original_price,
                         savings=savings,
                         urgency=product.get_emergency_status())


# ============================================================================
# ADMIN ROUTES - Analytics & Metrics
# ============================================================================

@bp.route('/admin/analytics')
@admin_required
def analytics():
    """Emergency marketplace analytics"""
    
    # Get metrics for last 30 days
    metrics_summary = EmergencyMarketplaceService.get_metrics_summary(days=30)
    
    # Auto-flag expiring products
    auto_flag_result = EmergencyMarketplaceService.auto_flag_expiring_products()
    
    # Get current emergency products
    emergency_count = Product.query.filter_by(is_emergency=True).count()
    
    return render_template('emergency/admin_analytics.html',
                         metrics=metrics_summary,
                         emergency_count=emergency_count,
                         auto_flag_result=auto_flag_result)


# ============================================================================
# API ROUTES - AJAX Endpoints
# ============================================================================

@bp.route('/api/update-metrics', methods=['POST'])
@admin_required
def api_update_metrics():
    """Update metrics (can be called by scheduler)"""
    
    metrics = EmergencyMarketplaceService.calculate_and_update_metrics()
    
    if metrics:
        return jsonify({'success': True, 'message': 'Metrics updated'})
    else:
        return jsonify({'success': False, 'message': 'Error updating metrics'}), 500


@bp.route('/api/auto-flag', methods=['POST'])
@admin_required
def api_auto_flag():
    """Auto-flag expiring products"""
    
    result = EmergencyMarketplaceService.auto_flag_expiring_products()
    
    return jsonify(result)


@bp.route('/api/emergency-count')
def api_emergency_count():
    """Get count of emergency products"""
    
    count = Product.query.filter_by(is_emergency=True).count()
    
    return jsonify({'count': count})


@bp.route('/api/marketplace-stats')
@retailer_required
def api_marketplace_stats():
    """Get quick stats for marketplace"""
    
    products = EmergencyMarketplaceService.get_emergency_marketplace_products()
    
    total_savings = sum(
        ((p.original_price_backup or p.price) - p.price) * p.quantity 
        for p in products
    )
    
    stats = {
        'total_products': len(products),
        'categories': EmergencyMarketplaceService.get_emergency_categories(),
        'total_savings': total_savings,
        'avg_discount': round(sum(p.emergency_discount for p in products) / max(len(products), 1), 1)
    }
    
    return jsonify(stats)
