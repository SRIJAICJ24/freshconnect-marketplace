import google.generativeai as genai
import os
import json
import re
from app import db
from app.models import ChatLog, Product, Order, RetailerCredit, ChatbotCommand

class ChatbotService:
    """
    REAL AI CHATBOT - Uses Google Gemini API
    THIS IS THE ONLY REAL API INTEGRATION
    """
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set in .env")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def get_response(self, message, user_role="retailer", user_id=None):
        """Get response from Gemini API"""
        
        try:
            system_prompt = f"""
            நீ FreshConnect சந்தை உதவியாள்.
            You are FreshConnect marketplace assistant.
            
            User Role: {user_role}
            
            தமிழ் மற்றும் ஆங்கிலத்தில் பதிலளி.
            Reply in mix of Tamil and English.
            
            சாதாரணமாக பேசு. நட்பாக வளையி.
            Be casual and friendly.
            
            சுருக்கமாக பதிலளி (2-3 வாக்கியம்).
            Keep response short (2-3 sentences).
            """
            
            full_prompt = f"{system_prompt}\n\nUser: {message}"
            
            response = self.model.generate_content(full_prompt)
            
            ai_response = response.text if response else "மன்னிக்கவும்"
            
            if user_id:
                chat_log = ChatLog(user_id=user_id, message=message, response=ai_response)
                db.session.add(chat_log)
                db.session.commit()
            
            return ai_response
        
        except Exception as e:
            print(f"[GEMINI ERROR] {str(e)}")
            return "தற்போது சேவை கிடைக்கவில்லை"


# ============ FEATURE 4: AI COMMAND PROCESSING ============

class SmartChatbotService:
    """
    AI-POWERED COMMAND PROCESSOR
    
    User says: "Find tomato sellers less than 50/kg"
    AI understands: Intent=search, Product=tomato, Price<50
    App shows: Search results page with filtered products
    """
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def extract_intent_simple(self, message, user_role):
        """
        Simple intent extraction using keywords
        Fallback if Gemini fails to parse
        """
        message_lower = message.lower()
        
        # Search products
        if any(word in message_lower for word in ['find', 'search', 'show products', 'கண்டுபிடி', 'தேடு']):
            # Extract product name and price
            product = None
            price_max = None
            
            # Common products
            products = ['tomato', 'potato', 'onion', 'rice', 'wheat', 'carrot']
            for p in products:
                if p in message_lower:
                    product = p
                    break
            
            # Extract price
            price_match = re.search(r'(\d+)', message_lower)
            if price_match:
                price_max = int(price_match.group(1))
            
            return {
                'intent': 'search_products',
                'parameters': {'product': product, 'price_max': price_max},
                'confidence': 0.7
            }
        
        # Check orders
        elif any(word in message_lower for word in ['orders', 'my order', 'வரிசை', 'ஆர்டர்']):
            return {
                'intent': 'check_orders',
                'parameters': {},
                'confidence': 0.8
            }
        
        # Check credit
        elif any(word in message_lower for word in ['credit', 'score', 'கடன்']):
            return {
                'intent': 'check_credit',
                'parameters': {},
                'confidence': 0.8
            }
        
        # Help
        else:
            return {
                'intent': 'help',
                'parameters': {},
                'confidence': 0.9
            }
    
    def process_command(self, message, user_id, user_role):
        """
        Process user command and coordinate response
        """
        
        try:
            # Try simple intent extraction first (faster, no API call)
            result = self.extract_intent_simple(message, user_role)
            
            intent = result.get('intent', 'help')
            parameters = result.get('parameters', {})
            
            # Execute command based on intent
            if intent == 'search_products':
                return self.search_products_command(parameters, user_role, user_id)
            
            elif intent == 'check_orders':
                return self.check_orders_command(user_id, user_role)
            
            elif intent == 'check_credit':
                return self.check_credit_command(user_id)
            
            else:  # help or unknown
                return self.help_response(user_role, message)
        
        except Exception as e:
            print(f"[CHATBOT COMMAND ERROR] {str(e)}")
            return {
                'type': 'error',
                'message': 'Sorry, I couldn\'t understand. Try again.',
                'redirect': None
            }
    
    def search_products_command(self, parameters, user_role, user_id):
        """
        Command: "Find tomato sellers less than 50/kg"
        Result: Filtered product search page
        """
        
        product_name = parameters.get('product', '').lower() if parameters.get('product') else None
        price_max = parameters.get('price_max')
        
        # Query products
        query = Product.query.filter_by(is_active=True)
        
        if product_name:
            query = query.filter(Product.product_name.ilike(f'%{product_name}%'))
        
        if price_max:
            query = query.filter(Product.price <= price_max)
        
        results = query.limit(5).all()
        
        # Store command for tracking
        if user_id:
            command = ChatbotCommand(
                user_id=user_id,
                command_text=f"Search {product_name} price < ₹{price_max}" if price_max else f"Search {product_name}",
                command_intent='search_products',
                parameters=parameters,
                result_type='search_results',
                result_url=f'/retailer/browse?search={product_name or ""}&max_price={price_max or ""}'
            )
            db.session.add(command)
            db.session.commit()
        
        if len(results) == 0:
            return {
                'type': 'text',
                'message': f'No products found matching your search. Try browsing all products!',
                'redirect': '/retailer/browse'
            }
        
        return {
            'type': 'search_results',
            'message': f'Found {len(results)} products:',
            'results': [{
                'id': p.id,
                'name': p.product_name,
                'price': p.price,
                'vendor': p.vendor.business_name,
                'unit': p.unit
            } for p in results],
            'redirect': f'/retailer/browse?search={product_name or ""}&max_price={price_max or ""}',
            'action': 'View all results'
        }
    
    def check_orders_command(self, user_id, user_role):
        """
        Command: "Show my orders"
        Result: Orders list/dashboard
        """
        
        if user_role == 'retailer':
            orders = Order.query.filter_by(buyer_id=user_id).order_by(Order.created_at.desc()).limit(3).all()
            redirect_url = '/retailer/orders'
        elif user_role == 'vendor':
            orders = Order.query.filter_by(seller_id=user_id).order_by(Order.created_at.desc()).limit(3).all()
            redirect_url = '/vendor/orders'
        else:
            return {'type': 'text', 'message': 'Order tracking not available for your role.'}
        
        return {
            'type': 'order_list',
            'message': f'You have {len(orders)} recent orders:',
            'recent_orders': [{
                'id': o.id,
                'status': o.order_status,
                'amount': o.total_amount,
                'date': o.created_at.strftime('%d-%m-%Y')
            } for o in orders],
            'redirect': redirect_url,
            'action': 'View all orders'
        }
    
    def check_credit_command(self, user_id):
        """
        Command: "What's my credit score?"
        Result: Credit dashboard
        """
        
        from app.credit_system import CreditSystem
        
        try:
            credit_info = CreditSystem.calculate_credit_score(user_id)
            
            return {
                'type': 'credit_info',
                'message': f'Your credit score: {credit_info["score"]}/1000',
                'tier': credit_info['tier_name'],
                'details': {
                    'score': credit_info['score'],
                    'tier': credit_info['tier'],
                    'tier_name': credit_info['tier_name']
                },
                'redirect': '/retailer/credit',
                'action': 'View full credit dashboard'
            }
        except:
            return {
                'type': 'text',
                'message': 'Credit information not available. Complete some orders first!'
            }
    
    def help_response(self, user_role, original_message):
        """
        Help message with examples and simple response
        """
        
        # Also provide a simple conversational response
        try:
            simple_response = ChatbotService().get_response(original_message, user_role)
            
            if user_role == 'retailer':
                examples = [
                    "Find tomato sellers less than 50/kg",
                    "Show my orders",
                    "What's my credit score?"
                ]
            elif user_role == 'vendor':
                examples = [
                    "Show my orders",
                    "View my products"
                ]
            else:
                examples = ["How can I help?"]
            
            return {
                'type': 'help',
                'message': simple_response,
                'examples': examples,
                'redirect': None
            }
        except:
            return {
                'type': 'text',
                'message': 'நான் உங்களுக்கு எப்படி உதவ முடியும்? How can I help you?'
            }
