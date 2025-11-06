"""
Voice Assistant Routes
Handle voice commands in Tamil and English
Enhanced with robust product search patterns
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import current_user, login_required
from app.models import Product, Order
from app import db
import re
from sqlalchemy import or_

bp = Blueprint('voice', __name__, url_prefix='/voice')


@bp.route('/test')
@login_required
def test_voice():
    """Test voice assistant configuration"""
    from app.voice_service import VoiceService
    import os
    
    # Test different queries
    test_queries = [
        "show me tomatoes",
        "list all vegetables",
        "find onions",
        "what fruits do you have",
        "check my orders"
    ]
    
    results = []
    for query in test_queries:
        # Test fallback system
        result = VoiceService.simple_understand_command(query, current_user.user_type)
        results.append({
            'query': query,
            'success': result['success'],
            'intent': result.get('command', {}).get('intent', 'unknown'),
            'entities': result.get('command', {}).get('entities', {})
        })
    
    return jsonify({
        'user_type': current_user.user_type,
        'gemini_api_configured': bool(os.environ.get('GEMINI_API_KEY')),
        'test_results': results,
        'status': 'Voice assistant fallback is working!' if all(r['success'] for r in results) else 'Some queries failed'
    })


@bp.route('/assistant')
@login_required
def assistant():
    """Voice assistant interface"""
    return render_template('voice/assistant.html')


@bp.route('/process-speech', methods=['POST'])
@login_required
def process_speech():
    """
    Process voice command
    Accepts transcribed text from Web Speech API
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        language = data.get('language', 'en')  # 'en' or 'ta'
        
        if not text:
            return jsonify({
                'success': False,
                'message': 'No speech text provided'
            }), 400
        
        # Try Gemini AI first
        command_result = VoiceService.understand_command(
            text=text,
            user_type=current_user.user_type,
            language=language
        )
        
        # FALLBACK: Use simple pattern matching if API fails
        if not command_result['success']:
            command_result = VoiceService.simple_understand_command(
                text=text,
                user_type=current_user.user_type
            )
        
        if not command_result['success']:
            return jsonify(command_result), 400
        
        command_data = command_result['command']
        
        # Process the command
        action_result = VoiceService.process_command_action(
            command_data=command_data,
            user_id=current_user.id,
            db_session=db.session
        )
        
        # Generate simple response (no API needed)
        if action_result['success']:
            response_text = action_result.get('message', 'Command processed successfully!')
        else:
            response_text = action_result.get('message', 'Could not process command')
        
        response = {
            'success': True,
            'text': response_text,
            'language': language
        }
        
        return jsonify({
            'success': True,
            'transcript': text,
            'command': command_data,
            'action_result': action_result,
            'response': response,
            'language': language
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing speech: {str(e)}'
        }), 500


@bp.route('/text-to-speech', methods=['POST'])
@login_required
def text_to_speech():
    """
    Convert text to speech
    Returns audio data or signals to use Web Speech API
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        language = data.get('language', 'en-US')
        
        if not text:
            return jsonify({
                'success': False,
                'message': 'No text provided'
            }), 400
        
        # Use Web Speech API (client-side)
        result = VoiceService.text_to_speech(
            text=text,
            language_code=language,
            use_web_api=True
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'TTS error: {str(e)}'
        }), 500


@bp.route('/quick-commands')
@login_required
def quick_commands():
    """Get list of suggested commands for current user"""
    
    commands = {
        'retailer': [
            {
                'en': 'Order 5 kg tomatoes',
                'ta': 'நான் 5 கிலோ தக்காளி ஆர்டர் செய்ய விரும்புகிறேன்'
            },
            {
                'en': 'Show me fresh vegetables',
                'ta': 'எனக்கு புதிய காய்கறிகள் காட்டுங்கள்'
            },
            {
                'en': 'Check my order status',
                'ta': 'என் ஆர்டர் நிலையைச் சரிபார்க்கவும்'
            },
            {
                'en': 'What fruits are available?',
                'ta': 'என்ன பழங்கள் கிடைக்கின்றன?'
            }
        ],
        'vendor': [
            {
                'en': 'Show my pending orders',
                'ta': 'எனது நிலுவையில் உள்ள ஆர்டர்களைக் காட்டு'
            },
            {
                'en': 'Add new product',
                'ta': 'புதிய தயாரிப்பைச் சேர்க்கவும்'
            },
            {
                'en': 'Check inventory status',
                'ta': 'சரக்கு நிலையைச் சரிபார்க்கவும்'
            }
        ],
        'admin': [
            {
                'en': 'Show system reports',
                'ta': 'கணினி அறிக்கைகளைக் காட்டு'
            },
            {
                'en': 'View all pending orders',
                'ta': 'அனைத்து நிலுவையில் உள்ள ஆர்டர்களையும் பார்க்கவும்'
            }
        ],
        'driver': [
            {
                'en': 'Show my deliveries',
                'ta': 'எனது டெலிவரிகளைக் காட்டு'
            },
            {
                'en': 'Update delivery status',
                'ta': 'டெலிவரி நிலையை புதுப்பிக்கவும்'
            }
        ]
    }
    
    user_commands = commands.get(current_user.user_type, commands['retailer'])
    
    return jsonify({
        'success': True,
        'commands': user_commands
    })


@bp.route('/demo')
@login_required
def demo():
    """Voice assistant demo page"""
    return render_template('voice/demo.html')


@bp.route('/query', methods=['POST'])
@login_required
def process_voice_query():
    """
    Enhanced voice query processing with multiple pattern recognition
    Works without external API - instant results
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip().lower()
        
        if not query:
            return jsonify({
                'success': False,
                'message': 'No query provided'
            }), 400
        
        # Parse query using multiple patterns
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
                    'suggestions': get_suggestions(parsed['product_name']),
                    'examples': [
                        "Find tomatoes less than 50 rupees",
                        "Show me vegetables",
                        "Search onions under 30 rupees"
                    ]
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


def parse_voice_query(query):
    """
    Parse natural language voice query into search parameters
    Handles multiple query patterns - works without API
    """
    result = {
        'product_name': None,
        'max_price': None,
        'min_price': None,
        'category': None,
        'action': None,
        'redirect_url': None
    }
    
    # Pattern 1: "find/search/show [product] less than/under [price]"
    pattern1 = r'(?:find|search|show|get|looking for)\s+(.+?)\s+(?:less than|under|below|cheaper than)\s+(?:rs\.?|rupees?|₹)?\s*(\d+)'
    match = re.search(pattern1, query)
    if match:
        result['product_name'] = match.group(1).strip()
        result['max_price'] = float(match.group(2))
        result['action'] = 'search_product'
        return result
    
    # Pattern 2: "find [product] between [price1] and [price2]"
    pattern2 = r'(?:find|search|show)\s+(.+?)\s+between\s+(?:rs\.?|rupees?|₹)?\s*(\d+)\s+(?:and|to)\s+(?:rs\.?|rupees?|₹)?\s*(\d+)'
    match = re.search(pattern2, query)
    if match:
        result['product_name'] = match.group(1).strip()
        result['min_price'] = float(match.group(2))
        result['max_price'] = float(match.group(3))
        result['action'] = 'search_product'
        return result
    
    # Pattern 3: "find [product] more than/above [price]"
    pattern3 = r'(?:find|search|show)\s+(.+?)\s+(?:more than|above|over)\s+(?:rs\.?|rupees?|₹)?\s*(\d+)'
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
    
    # Default: search for the query as-is
    result['product_name'] = query
    result['action'] = 'search_product'
    return result


def search_products(parsed):
    """Search products based on parsed parameters"""
    query = Product.query.filter(Product.stock_quantity > 0)
    
    # Filter by product name
    if parsed['product_name']:
        # Remove common words
        clean_name = parsed['product_name']
        for word in ['the', 'a', 'an', 'some', 'any', 'per', 'kg']:
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
    """Get similar product suggestions"""
    if not product_name:
        return []
    
    # Get products with similar names
    similar = Product.query.filter(
        Product.product_name.ilike(f"%{product_name[:3]}%")
    ).limit(5).all()
    
    return [p.product_name for p in similar]


@bp.route('/help', methods=['GET'])
def get_help():
    """Return voice command examples"""
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
