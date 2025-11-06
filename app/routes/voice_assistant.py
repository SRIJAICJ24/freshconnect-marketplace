"""
Voice Assistant Routes
Handles natural language queries for product search
"""

from flask import Blueprint, request, jsonify, redirect, url_for
from app.models import Product, User, Order, DriverAssignment
from app import db
import re
from sqlalchemy import or_, and_

bp = Blueprint('voice_assistant', __name__, url_prefix='/voice')

def parse_voice_query(query):
    """
    Parse natural language voice query into search parameters
    Handles multiple query patterns
    """
    query = query.lower().strip()
    
    result = {
        'product_name': None,
        'max_price': None,
        'min_price': None,
        'category': None,
        'action': None,
        'redirect_url': None
    }
    
    # Pattern 1: "find/search/show [product] less than/under [price]"
    pattern1 = r'(?:find|search|show|get|looking for)\s+(.+?)\s+(?:less than|under|below|cheaper than)\s+(?:rs\.?|rupees?)\s*(\d+)'
    match = re.search(pattern1, query)
    if match:
        result['product_name'] = match.group(1).strip()
        result['max_price'] = float(match.group(2))
        result['action'] = 'search_product'
        return result
    
    # Pattern 2: "find [product] between [price1] and [price2]"
    pattern2 = r'(?:find|search|show)\s+(.+?)\s+between\s+(?:rs\.?|rupees?)\s*(\d+)\s+(?:and|to)\s+(?:rs\.?|rupees?)\s*(\d+)'
    match = re.search(pattern2, query)
    if match:
        result['product_name'] = match.group(1).strip()
        result['min_price'] = float(match.group(2))
        result['max_price'] = float(match.group(3))
        result['action'] = 'search_product'
        return result
    
    # Pattern 3: "find [product] more than/above [price]"
    pattern3 = r'(?:find|search|show)\s+(.+?)\s+(?:more than|above|over|expensive than)\s+(?:rs\.?|rupees?)\s*(\d+)'
    match = re.search(pattern3, query)
    if match:
        result['product_name'] = match.group(1).strip()
        result['min_price'] = float(match.group(2))
        result['action'] = 'search_product'
        return result
    
    # Pattern 4: "find cheapest/expensive [product]"
    pattern4 = r'(?:find|search|show)\s+(?:cheapest|least expensive)\s+(.+)'
    match = re.search(pattern4, query)
    if match:
        result['product_name'] = match.group(1).strip()
        result['action'] = 'search_cheapest'
        return result
    
    pattern4b = r'(?:find|search|show)\s+(?:most expensive|priciest)\s+(.+)'
    match = re.search(pattern4b, query)
    if match:
        result['product_name'] = match.group(1).strip()
        result['action'] = 'search_expensive'
        return result
    
    # Pattern 5: "show me [category] products"
    pattern5 = r'(?:show|display|find)\s+(?:me\s+)?(.+?)\s+products?'
    match = re.search(pattern5, query)
    if match:
        result['category'] = match.group(1).strip()
        result['action'] = 'search_category'
        return result
    
    # Pattern 6: Navigation commands
    navigation_patterns = {
        r'go to (?:my )?cart|show (?:my )?cart|open cart': 'retailer.cart',
        r'go to (?:my )?orders|show (?:my )?orders': 'retailer.orders',
        r'go to dashboard|show dashboard': 'retailer.dashboard',
        r'go to shop|start shopping|browse products': 'retailer.browse',
        r'logout|sign out|log out': 'auth.logout',
        r'go to home|go back|home page': 'main.index',
        r'track (?:my )?order|order status': 'retailer.orders',
    }
    
    for pattern, route in navigation_patterns.items():
        if re.search(pattern, query):
            result['action'] = 'navigate'
            result['redirect_url'] = route
            return result
    
    # Pattern 7: Order tracking by ID
    pattern7 = r'track order\s+(?:#)?(\d+)'
    match = re.search(pattern7, query)
    if match:
        result['action'] = 'track_order'
        result['order_id'] = match.group(1)
        return result
    
    # Pattern 8: Simple product name search
    pattern8 = r'(?:find|search|show|get|looking for)\s+(.+)'
    match = re.search(pattern8, query)
    if match:
        result['product_name'] = match.group(1).strip()
        result['action'] = 'search_product'
        return result
    
    # If no pattern matches, just search for the query
    result['product_name'] = query
    result['action'] = 'search_product'
    return result


@bp.route('/query', methods=['POST'])
def process_voice_query():
    """
    Process voice query and return search results
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'message': 'No query provided'
            }), 400
        
        # Parse the query
        parsed = parse_voice_query(query)
        
        # Handle navigation
        if parsed['action'] == 'navigate':
            return jsonify({
                'success': True,
                'action': 'navigate',
                'url': url_for(parsed['redirect_url']),
                'message': f"Taking you there..."
            })
        
        # Handle order tracking
        if parsed['action'] == 'track_order':
            order_id = parsed.get('order_id')
            return jsonify({
                'success': True,
                'action': 'navigate',
                'url': url_for('order_tracking.track_order', order_id=order_id),
                'message': f"Tracking order #{order_id}"
            })
        
        # Handle product search
        if parsed['action'] in ['search_product', 'search_cheapest', 'search_expensive']:
            products = search_products(parsed)
            
            if products:
                return jsonify({
                    'success': True,
                    'action': 'search',
                    'products': [{
                        'id': p.id,
                        'name': p.product_name,
                        'price': p.price,
                        'stock': p.stock_quantity,
                        'unit': p.unit,
                        'category': p.category,
                        'vendor': p.vendor.business_name if p.vendor else 'Unknown'
                    } for p in products],
                    'message': f"Found {len(products)} product(s)",
                    'parsed_query': {
                        'product': parsed['product_name'],
                        'max_price': parsed['max_price'],
                        'min_price': parsed['min_price']
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f"No products found matching '{query}'",
                    'suggestions': get_suggestions(parsed['product_name'])
                })
        
        # Handle category search
        if parsed['action'] == 'search_category':
            products = Product.query.filter(
                Product.category.ilike(f"%{parsed['category']}%"),
                Product.stock_quantity > 0
            ).limit(20).all()
            
            if products:
                return jsonify({
                    'success': True,
                    'action': 'search',
                    'products': [{
                        'id': p.id,
                        'name': p.product_name,
                        'price': p.price,
                        'stock': p.stock_quantity,
                        'unit': p.unit,
                        'category': p.category
                    } for p in products],
                    'message': f"Found {len(products)} {parsed['category']} products"
                })
        
        return jsonify({
            'success': False,
            'message': "I didn't understand that. Try asking differently.",
            'examples': [
                "Find tomatoes less than 50 rupees",
                "Show me vegetables",
                "Search for onions between 20 and 40 rupees",
                "Go to my cart"
            ]
        })
        
    except Exception as e:
        print(f"❌ Voice query error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Error processing query'
        }), 500


def search_products(parsed):
    """
    Search products based on parsed parameters
    """
    query = Product.query.filter(Product.stock_quantity > 0)
    
    # Filter by product name
    if parsed['product_name']:
        # Remove common words
        clean_name = parsed['product_name']
        for word in ['the', 'a', 'an', 'some', 'any']:
            clean_name = clean_name.replace(f' {word} ', ' ')
        
        query = query.filter(
            or_(
                Product.product_name.ilike(f"%{clean_name}%"),
                Product.category.ilike(f"%{clean_name}%"),
                Product.description.ilike(f"%{clean_name}%")
            )
        )
    
    # Filter by price
    if parsed['max_price']:
        query = query.filter(Product.price <= parsed['max_price'])
    
    if parsed['min_price']:
        query = query.filter(Product.price >= parsed['min_price'])
    
    # Sort based on action
    if parsed['action'] == 'search_cheapest':
        query = query.order_by(Product.price.asc())
    elif parsed['action'] == 'search_expensive':
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.product_name)
    
    return query.limit(20).all()


def get_suggestions(product_name):
    """
    Get similar product suggestions
    """
    if not product_name:
        return []
    
    # Get products with similar names
    similar = Product.query.filter(
        Product.product_name.ilike(f"%{product_name[:3]}%")
    ).limit(5).all()
    
    return [p.product_name for p in similar]


@bp.route('/help', methods=['GET'])
def get_help():
    """
    Return voice command examples
    """
    examples = {
        'product_search': [
            "Find tomatoes less than 50 rupees",
            "Search onions under 30 rupees per kg",
            "Show me potatoes below 20 rupees",
            "Get carrots cheaper than 40 rupees"
        ],
        'price_range': [
            "Find tomatoes between 30 and 50 rupees",
            "Search onions from 20 to 40 rupees"
        ],
        'category': [
            "Show me vegetable products",
            "Display fruit products",
            "Find dairy products"
        ],
        'navigation': [
            "Go to my cart",
            "Show my orders",
            "Open dashboard",
            "Start shopping",
            "Go to home"
        ],
        'ordering': [
            "Find cheapest tomatoes",
            "Show most expensive onions"
        ],
        'tracking': [
            "Track my order",
            "Track order 123",
            "Show order status"
        ]
    }
    
    return jsonify({
        'success': True,
        'examples': examples,
        'tips': [
            "Speak clearly and naturally",
            "Include product name and price",
            "Use 'rupees', 'rs', or price numbers",
            "Try different phrasings if not understood"
        ]
    })
