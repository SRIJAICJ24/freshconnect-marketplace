from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Product, Order, OrderItem, Payment, Driver, DriverAssignment, RetailerCredit
from app.decorators import retailer_required
from app.driver_service import MockDriverService
from app.credit_system import CreditSystem
from datetime import datetime, timedelta

bp = Blueprint('retailer', __name__, url_prefix='/retailer')

@bp.route('/dashboard')
@retailer_required
def dashboard():
    # SIMPLIFIED VERSION - No complex calculations
    print(f"✅ Retailer dashboard accessed by user {current_user.id}")
    
    # Simple default credit - no database queries
    credit_info = {
        'score': 500,
        'tier': 'silver',
        'tier_name': 'Silver',
        'limit': 50000,
        'available': 50000,
        'utilized': 0
    }
    
    try:
        return render_template('retailer/dashboard.html', credit=credit_info)
    except Exception as e:
        print(f"❌ Template error: {e}")
        import traceback
        traceback.print_exc()
        return f"<h1>Dashboard Loading Error</h1><p>Error: {str(e)}</p><p>User ID: {current_user.id}</p><p>User Type: {current_user.user_type}</p>", 500

@bp.route('/browse')
@retailer_required
def browse():
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = Product.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(Product.product_name.ilike(f'%{search}%'))
    
    products = query.all()
    categories = db.session.query(Product.category).distinct().all()
    
    return render_template('retailer/browse.html',
                         products=products,
                         categories=[c[0] for c in categories])

@bp.route('/product/<int:product_id>')
@retailer_required
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('retailer/product_detail.html', product=product)

@bp.route('/cart')
@retailer_required
def cart():
    cart = session.get('cart', {})
    
    cart_items = []
    total_amount = 0
    
    for product_id, quantity in cart.items():
        product = Product.query.get(product_id)
        if product:
            amount = product.price * quantity
            total_amount += amount
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'amount': amount
            })
    
    return render_template('retailer/cart.html',
                         cart_items=cart_items,
                         total_amount=total_amount)

@bp.route('/add-to-cart', methods=['POST'])
@retailer_required
def add_to_cart():
    # Support both JSON (AJAX) and form data (regular form submission)
    is_json = request.is_json
    
    if is_json:
        product_id = request.json.get('product_id')
        quantity = request.json.get('quantity', 1)
    else:
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity', 1)
    
    if not product_id:
        if is_json:
            return jsonify({
                'success': False,
                'message': 'Product ID is required'
            }), 400
        else:
            flash('Product ID is required', 'danger')
            return redirect(url_for('retailer.browse'))
    
    # Convert quantity to float (for kg, etc.)
    try:
        quantity = float(quantity)
    except (ValueError, TypeError):
        if is_json:
            return jsonify({
                'success': False,
                'message': 'Invalid quantity'
            }), 400
        else:
            flash('Invalid quantity', 'danger')
            return redirect(url_for('retailer.browse'))
    
    if quantity <= 0:
        if is_json:
            return jsonify({
                'success': False,
                'message': 'Quantity must be greater than 0'
            }), 400
        else:
            flash('Quantity must be greater than 0', 'danger')
            return redirect(url_for('retailer.browse'))
    
    product = Product.query.get_or_404(product_id)
    
    # Check MOQ validation
    if product.moq_enabled and product.moq_type == 'quantity':
        if quantity < product.minimum_quantity:
            message = f'Minimum order quantity is {product.minimum_quantity} {product.unit}. You tried to add {quantity}.'
            if is_json:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
            else:
                flash(message, 'danger')
                return redirect(request.referrer or url_for('retailer.browse'))
    
    if 'cart' not in session:
        session['cart'] = {}
    
    session['cart'][str(product_id)] = quantity
    session.modified = True
    
    # Return appropriate response based on request type
    if is_json:
        return jsonify({'success': True, 'message': 'Added to cart successfully!'})
    else:
        flash(f'Added {quantity} {product.unit} of {product.product_name} to cart!', 'success')
        return redirect(request.referrer or url_for('retailer.cart'))

@bp.route('/api/cart-count')
@retailer_required
def cart_count():
    cart = session.get('cart', {})
    total_items = sum(cart.values())
    return jsonify({'count': total_items})

@bp.route('/checkout', methods=['GET', 'POST'])
@retailer_required
def checkout():
    cart = session.get('cart', {})
    
    if not cart:
        flash('Cart is empty', 'danger')
        return redirect(url_for('retailer.browse'))
    
    if request.method == 'POST':
        delivery_address = request.form.get('delivery_address')
        
        total_amount = 0
        cart_items = []
        
        for product_id, quantity in cart.items():
            product = Product.query.get(product_id)
            if product:
                amount = product.price * quantity
                total_amount += amount
                cart_items.append((product, quantity, amount))
        
        order = Order(
            buyer_id=current_user.id,
            seller_id=cart_items[0][0].vendor_id,
            total_amount=total_amount,
            delivery_address=delivery_address,
            order_status='pending'
        )
        
        db.session.add(order)
        db.session.flush()
        
        for product, quantity, amount in cart_items:
            item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                price_at_purchase=product.price
            )
            db.session.add(item)
        
        db.session.commit()
        
        session['cart'] = {}
        session.modified = True
        
        # Redirect to bill summary first (NEW FLOW)
        return redirect(url_for('payment.bill_summary', order_id=order.id))
    
    return render_template('retailer/checkout.html')

@bp.route('/orders')
@retailer_required
def orders():
    retailer_orders = Order.query.filter_by(
        buyer_id=current_user.id
    ).order_by(Order.created_at.desc()).all()
    
    return render_template('retailer/orders.html', orders=retailer_orders)

@bp.route('/orders/<int:order_id>/track')
@retailer_required
def track_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.buyer_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('retailer.orders'))
    
    assignment = DriverAssignment.query.filter_by(order_id=order_id).first()
    
    return render_template('retailer/order_tracking.html', order=order, assignment=assignment)

@bp.route('/credit')
@retailer_required
def credit_dashboard():
    credit = RetailerCredit.query.filter_by(retailer_id=current_user.id).first()
    
    if not credit:
        credit = RetailerCredit(retailer_id=current_user.id)
        db.session.add(credit)
        db.session.commit()
    
    credit_info = CreditSystem.calculate_credit_score(current_user.id)
    benefits = CreditSystem.get_tier_benefits(credit_info['tier'])
    
    return render_template('retailer/credit_dashboard.html',
                         credit=credit_info,
                         benefits=benefits)
