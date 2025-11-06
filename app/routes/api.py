from flask import Blueprint, request, jsonify, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Product, DriverAssignment
from app.driver_service import MockDriverService
from app.ai_service import ChatbotService, SmartChatbotService

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/validate-moq/<int:product_id>', methods=['POST'])
def validate_moq(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = request.json.get('quantity')
    
    if product.moq_enabled:
        if product.moq_type == 'quantity':
            if quantity < product.minimum_quantity:
                return jsonify({
                    'valid': False,
                    'message': f'Minimum: {product.minimum_quantity}'
                }), 400
    
    return jsonify({'valid': True})

@bp.route('/driver-location/<int:assignment_id>')
def get_driver_location(assignment_id):
    try:
        location = MockDriverService.get_mock_driver_location(assignment_id)
        return jsonify(location)
    except:
        return jsonify({'error': 'Not found'}), 404

@bp.route('/chatbot', methods=['POST'])
@login_required
def chatbot():
    message = request.json.get('message')
    
    try:
        # First try SmartChatbotService for advanced features
        smart_service = SmartChatbotService()
        result = smart_service.process_command(message, current_user.id, current_user.user_type)
        return jsonify(result)
    except Exception as e:
        print(f"[CHATBOT API ERROR] {str(e)}")
        
        # Fallback: Try voice-style pattern matching for product search
        try:
            import re
            from sqlalchemy import or_
            query_lower = message.lower().strip()
            
            # Pattern 1: "find/search [product] less than/under [price]"
            pattern1 = r'(?:find|search|show|get|looking for)\s+(.+?)\s+(?:less than|under|below|cheaper than)\s+(?:rs\.?|rupees?|₹)?\s*(\d+)'
            match = re.search(pattern1, query_lower)
            
            if match:
                product_name = match.group(1).strip()
                max_price = float(match.group(2))
                
                # Search products
                products = Product.query.filter(
                    or_(
                        Product.product_name.ilike(f"%{product_name}%"),
                        Product.category.ilike(f"%{product_name}%")
                    ),
                    Product.price <= max_price,
                    Product.stock_quantity > 0
                ).limit(10).all()
                
                if products:
                    results = [{
                        'name': p.product_name,
                        'price': p.price,
                        'unit': p.unit,
                        'vendor': p.vendor.business_name if p.vendor else 'Unknown'
                    } for p in products]
                    
                    return jsonify({
                        'type': 'search_results',
                        'message': f'Found {len(products)} {product_name} under ₹{max_price}',
                        'results': results,
                        'redirect': url_for('retailer.browse'),
                        'action': 'View all products'
                    })
                else:
                    return jsonify({
                        'type': 'text',
                        'message': f'No {product_name} found under ₹{max_price}. Try increasing your budget or search for similar products.'
                    })
            
            # Pattern 2: Simple product search "find [product]"
            pattern2 = r'(?:find|search|show|get)\s+(.+)'
            match = re.search(pattern2, query_lower)
            
            if match:
                product_name = match.group(1).strip()
                products = Product.query.filter(
                    or_(
                        Product.product_name.ilike(f"%{product_name}%"),
                        Product.category.ilike(f"%{product_name}%")
                    ),
                    Product.stock_quantity > 0
                ).limit(10).all()
                
                if products:
                    results = [{
                        'name': p.product_name,
                        'price': p.price,
                        'unit': p.unit,
                        'vendor': p.vendor.business_name if p.vendor else 'Unknown'
                    } for p in products]
                    
                    return jsonify({
                        'type': 'search_results',
                        'message': f'Found {len(products)} results for "{product_name}"',
                        'results': results,
                        'redirect': url_for('retailer.browse'),
                        'action': 'View all products'
                    })
            
            # Final fallback: Try basic chatbot
            service = ChatbotService()
            response = service.get_response(message, current_user.user_type, current_user.id)
            return jsonify({'type': 'text', 'message': response})
            
        except Exception as fallback_error:
            print(f"[CHATBOT FALLBACK ERROR] {fallback_error}")
            return jsonify({
                'type': 'help',
                'message': 'I can help you search for products!',
                'examples': [
                    '"Find tomatoes less than 50 rupees"',
                    '"Search onions under 30"',
                    '"Show me vegetables"',
                    '"Order 5 kg tomatoes"',
                    '"Check my orders"'
                ]
            })
