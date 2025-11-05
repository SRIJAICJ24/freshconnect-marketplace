"""
Voice Assistant Service
Supports Tamil and English voice commands for FreshConnect
Uses Web Speech API (browser-based) for speech recognition and synthesis
"""

import google.generativeai as genai
import os
import base64
import json
from datetime import datetime

# Optional: Google Cloud Speech services (not required)
try:
    from google.cloud import speech_v1 as speech
    from google.cloud import texttospeech
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    speech = None
    texttospeech = None


class VoiceService:
    """
    Service for voice recognition and command processing
    Supports both Tamil (தமிழ்) and English
    """
    
    # Configure API keys
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GOOGLE_CLOUD_API_KEY = os.environ.get('GOOGLE_CLOUD_API_KEY', '')
    
    @staticmethod
    def configure_api():
        """Configure APIs"""
        if VoiceService.GEMINI_API_KEY:
            genai.configure(api_key=VoiceService.GEMINI_API_KEY)
            return True
        return False
    
    @staticmethod
    def transcribe_audio_web_api(audio_data, language='en-US'):
        """
        Transcribe audio using Web Speech API (client-side)
        This is a fallback method that processes already transcribed text
        """
        # Web Speech API handles transcription on client side
        # This method is for server-side processing of the transcribed text
        return {
            'success': True,
            'text': audio_data,
            'language': language
        }
    
    @staticmethod
    def transcribe_audio_google_api(audio_content, language_code='en-US'):
        """
        Transcribe audio using Google Cloud Speech-to-Text API
        Supports Tamil (ta-IN) and English (en-US, en-IN)
        
        NOTE: Requires Google Cloud credentials
        """
        try:
            # Check if Google Cloud is available
            if not GOOGLE_CLOUD_AVAILABLE:
                return {
                    'success': False,
                    'message': 'Google Cloud Speech not installed. Using Web Speech API instead.'
                }
            
            # Check if Google Cloud credentials are set
            if not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
                return {
                    'success': False,
                    'message': 'Google Cloud credentials not configured. Using Web Speech API instead.'
                }
            
            client = speech.SpeechClient()
            
            # Configure recognition
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=48000,
                language_code=language_code,
                alternative_language_codes=['ta-IN', 'en-IN', 'en-US'],  # Multi-language support
                enable_automatic_punctuation=True,
            )
            
            audio = speech.RecognitionAudio(content=audio_content)
            
            # Perform recognition
            response = client.recognize(config=config, audio=audio)
            
            if not response.results:
                return {
                    'success': False,
                    'message': 'No speech detected'
                }
            
            # Get best transcript
            transcript = response.results[0].alternatives[0].transcript
            confidence = response.results[0].alternatives[0].confidence
            
            return {
                'success': True,
                'text': transcript,
                'confidence': confidence,
                'language': language_code
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Transcription error: {str(e)}'
            }
    
    @staticmethod
    def simple_understand_command(text, user_type='retailer'):
        """
        Simple pattern matching fallback (NO API REQUIRED)
        ALWAYS works - extracts intent using keywords
        """
        import re
        
        text_lower = text.lower()
        
        # Default structure
        command = {
            'intent': 'unknown',
            'entities': {},
            'confidence': 'low',
            'language_detected': 'en'
        }
        
        # Extract numbers
        numbers = re.findall(r'\d+', text)
        
        # PATTERN 1: Order/Find Products (detect product mentions)
        # Common product names - expanded list
        products = {
            'tomato': ['tomato', 'tomatoes', 'தக்காளி', 'tamato'],
            'potato': ['potato', 'potatoes', 'உருளைக்கிழங்கு', 'aloo'],
            'onion': ['onion', 'onions', 'வெங்காயம்', 'pyaz'],
            'carrot': ['carrot', 'carrots', 'கேரட்'],
            'apple': ['apple', 'apples', 'ஆப்பிள்', 'seb'],
            'banana': ['banana', 'bananas', 'வாழைப்பழம்', 'kela'],
            'orange': ['orange', 'oranges', 'ஆரஞ்சு', 'santra'],
            'mango': ['mango', 'mangoes', 'மா', 'aam'],
            'rice': ['rice', 'அரிசி', 'chawal'],
            'wheat': ['wheat', 'கோதுமை', 'gehun'],
            'lentil': ['lentil', 'lentils', 'dal', 'பருப்பு'],
            'cabbage': ['cabbage', 'முட்டைகோஸ்'],
            'cauliflower': ['cauliflower', 'பூக்கோஸ்', 'gobi'],
            'spinach': ['spinach', 'கீரை', 'palak'],
            'grape': ['grape', 'grapes', 'திராட்சை', 'angoor'],
            'vegetable': ['vegetable', 'vegetables', 'காய்கறி', 'veggies', 'veggie', 'sabzi'],
            'fruit': ['fruit', 'fruits', 'பழம்', 'phal']
        }
        
        detected_product = None
        for product, keywords in products.items():
            if any(k in text_lower for k in keywords):
                detected_product = product
                break
        
        # If product detected OR order/find keywords present
        product_keywords = ['order', 'find', 'show', 'search', 'get', 'want', 'need', 'buy', 'purchase', 
                           'வேண்டும்', 'காட்டு', 'kg', 'of', 'list', 'all', 'available', 'price', 
                           'cost', 'tell me', 'what', 'any', 'have']
        has_product_keyword = any(word in text_lower for word in product_keywords)
        
        if detected_product or has_product_keyword:
            command['intent'] = 'order_product'
            
            if detected_product:
                command['entities']['product_name'] = detected_product
            else:
                # Extract product name (everything except numbers and common words)
                stop_words = ['order', 'find', 'show', 'me', 'kg', 'of', 'get', 'i', 'want', 'need', 'less', 'than', 'for', 'rupees', 'a', 'the']
                words = text_lower.split()
                product_words = [w for w in words if w not in stop_words and not w.isdigit()]
                
                if product_words:
                    command['entities']['product_name'] = ' '.join(product_words)
            
            if numbers:
                command['entities']['quantity'] = numbers[0]
            
            # Detect category
            if detected_product in ['tomato', 'potato', 'onion', 'carrot']:
                command['entities']['category'] = 'Vegetables'
            elif detected_product in ['apple', 'banana', 'orange']:
                command['entities']['category'] = 'Fruits'
            elif 'vegetable' in text_lower or 'காய்கறி' in text_lower:
                command['entities']['category'] = 'Vegetables'
                if not command['entities'].get('product_name'):
                    command['intent'] = 'list_products'
            elif 'fruit' in text_lower or 'பழம்' in text_lower:
                command['entities']['category'] = 'Fruits'
                if not command['entities'].get('product_name'):
                    command['intent'] = 'list_products'
            
            command['confidence'] = 'high'
        
        # PATTERN 2: Check Orders
        order_keywords = ['order', 'track', 'status', 'check', 'my order', 'where']
        if any(word in text_lower for word in order_keywords) and 'order' in text_lower:
            if numbers:
                command['intent'] = 'check_order_status'
                command['entities']['order_id'] = numbers[0]
            else:
                command['intent'] = 'list_orders'
            command['confidence'] = 'high'
        
        # PATTERN 3: Help
        if any(word in text_lower for word in ['help', 'what can you do', 'commands']):
            command['intent'] = 'help'
            command['confidence'] = 'high'
        
        return {
            'success': True,
            'command': command,
            'raw_text': text
        }
    
    @staticmethod
    def understand_command(text, user_type='retailer', language='en'):
        """
        Use Gemini AI to understand voice command and extract intent
        Supports both Tamil and English
        
        Args:
            text: Transcribed text (Tamil or English)
            user_type: retailer, vendor, driver, admin
            language: 'en' or 'ta'
        """
        try:
            if not VoiceService.configure_api():
                return {
                    'success': False,
                    'message': 'Gemini API not configured'
                }
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Create context-aware prompt
            prompt = f"""
You are a voice assistant for FreshConnect, a fresh produce marketplace.
User Type: {user_type}
Language: {"Tamil (தமிழ்)" if language == 'ta' else "English"}

Analyze this voice command and extract structured information in JSON format:

Command: "{text}"

Return JSON with this structure:
{{
    "intent": "The main action (order_product, check_status, add_product, list_products, help, etc.)",
    "entities": {{
        "product_name": "Product name if mentioned",
        "quantity": "Quantity if mentioned (number)",
        "unit": "Unit if mentioned (kg, pieces, etc.)",
        "category": "Category if mentioned (Vegetables, Fruits, etc.)",
        "order_id": "Order ID if mentioned",
        "price": "Price if mentioned"
    }},
    "confidence": "high/medium/low",
    "language_detected": "ta or en",
    "english_translation": "English translation if input was Tamil",
    "clarification_needed": "What information is missing, if any",
    "suggested_response": "Suggested response to user in their language"
}}

Common intents by user type:
- Retailer: order_product, check_order_status, view_products, add_to_cart, track_order
- Vendor: add_product, update_inventory, check_orders, view_sales
- Admin: view_reports, manage_users, system_status

Examples:
- "I want to order 5 kg tomatoes" -> intent: order_product, entities: {{product: tomatoes, quantity: 5, unit: kg}}
- "நான் 3 கிலோ தக்காளி வேண்டும்" -> intent: order_product (Tamil: I want 3 kg tomatoes)
- "Check order status for order 123" -> intent: check_order_status, entities: {{order_id: 123}}

Return ONLY the JSON, no additional text.
"""
            
            response = model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Clean JSON
            if result_text.startswith('```'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            command_data = json.loads(result_text)
            
            return {
                'success': True,
                'command': command_data,
                'raw_text': text
            }
            
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'message': f'Could not parse command: {str(e)}',
                'raw_response': result_text if 'result_text' in locals() else ''
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error understanding command: {str(e)}'
            }
    
    @staticmethod
    def text_to_speech(text, language_code='en-US', use_web_api=True):
        """
        Convert text to speech
        Supports Tamil (ta-IN) and English (en-US, en-IN)
        
        Args:
            text: Text to convert
            language_code: 'en-US', 'en-IN', or 'ta-IN'
            use_web_api: Use Web Speech API (client-side) instead of Google Cloud
        """
        if use_web_api:
            # Web Speech API handles TTS on client side
            return {
                'success': True,
                'text': text,
                'language': language_code,
                'method': 'web_api'
            }
        
        try:
            # Check if Google Cloud is available
            if not GOOGLE_CLOUD_AVAILABLE:
                return {
                    'success': False,
                    'message': 'Google Cloud TTS not installed. Use Web Speech API instead.',
                    'fallback': True,
                    'text': text
                }
            
            # Google Cloud Text-to-Speech (requires credentials)
            if not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
                return {
                    'success': False,
                    'message': 'Google Cloud credentials not set. Use Web Speech API instead.',
                    'fallback': True,
                    'text': text
                }
            
            client = texttospeech.TextToSpeechClient()
            
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Select voice based on language
            if language_code.startswith('ta'):
                voice = texttospeech.VoiceSelectionParams(
                    language_code='ta-IN',
                    name='ta-IN-Standard-A'  # Tamil voice
                )
            else:
                voice = texttospeech.VoiceSelectionParams(
                    language_code='en-IN',
                    name='en-IN-Wavenet-D'  # Indian English voice
                )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Return base64 encoded audio
            audio_base64 = base64.b64encode(response.audio_content).decode('utf-8')
            
            return {
                'success': True,
                'audio': audio_base64,
                'text': text,
                'language': language_code,
                'method': 'google_cloud'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'TTS error: {str(e)}',
                'fallback': True,
                'text': text
            }
    
    @staticmethod
    def process_command_action(command_data, user_id, db_session):
        """
        Process the understood command and perform actions
        
        Args:
            command_data: Parsed command from understand_command()
            user_id: Current user ID
            db_session: Database session
        """
        from app.models import Product, Order, User
        
        try:
            intent = command_data.get('intent', '')
            entities = command_data.get('entities', {})
            
            result = {
                'success': False,
                'action': intent,
                'message': '',
                'data': {}
            }
            
            # Handle different intents
            if intent == 'order_product' or intent == 'list_products':
                product_name = entities.get('product_name')
                quantity = entities.get('quantity')
                category = entities.get('category')
                
                # Build query
                query = Product.query.filter(Product.is_active == True)
                
                if product_name:
                    query = query.filter(Product.product_name.ilike(f'%{product_name}%'))
                
                if category:
                    query = query.filter(Product.category.ilike(f'%{category}%'))
                
                products = query.limit(10).all()
                
                if not products:
                    result['message'] = f'No products found'
                    if product_name:
                        result['message'] = f'No products found matching "{product_name}"'
                    return result
                
                result['success'] = True
                result['message'] = f'Found {len(products)} product(s)'
                if product_name:
                    result['message'] = f'Found {len(products)} product(s) matching "{product_name}"'
                    
                result['data']['products'] = [
                    {
                        'id': p.id,
                        'name': p.product_name,
                        'category': p.category,
                        'price': float(p.price),
                        'unit': p.unit,
                        'vendor': p.vendor.name if p.vendor else 'Unknown'
                    }
                    for p in products
                ]
                result['data']['quantity'] = quantity
                return result
            
            elif intent == 'view_products':
                category = entities.get('category')
                
                query = Product.query.filter(Product.is_active == True)
                
                if category:
                    query = query.filter(Product.category.ilike(f'%{category}%'))
                
                products = query.limit(10).all()
                
                result['success'] = True
                result['message'] = f'Found {len(products)} products'
                result['data']['products'] = [
                    {
                        'id': p.id,
                        'name': p.product_name,
                        'category': p.category,
                        'price': float(p.price),
                        'unit': p.unit,
                        'vendor': p.vendor.name if p.vendor else 'Unknown'
                    }
                    for p in products
                ]
                return result
            
            elif intent == 'list_orders':
                # Get user's recent orders
                orders = Order.query.filter(
                    Order.buyer_id == user_id
                ).order_by(Order.order_date.desc()).limit(10).all()
                
                result['success'] = True
                result['message'] = f'You have {len(orders)} recent order(s)'
                result['data']['orders'] = [
                    {
                        'id': o.id,
                        'status': o.order_status,
                        'total': float(o.total_amount),
                        'date': o.order_date.strftime('%Y-%m-%d')
                    }
                    for o in orders
                ]
                return result
            
            elif intent == 'check_order_status' or intent == 'track_order':
                order_id = entities.get('order_id')
                
                if not order_id:
                    # Get user's recent orders
                    orders = Order.query.filter(
                        Order.buyer_id == user_id
                    ).order_by(Order.order_date.desc()).limit(5).all()
                    
                    result['success'] = True
                    result['message'] = f'You have {len(orders)} recent orders'
                    result['data']['orders'] = [
                        {
                            'id': o.id,
                            'status': o.order_status,
                            'total': float(o.total_amount),
                            'date': o.order_date.strftime('%Y-%m-%d')
                        }
                        for o in orders
                    ]
                    return result
                
                # Get specific order
                order = Order.query.filter(
                    Order.id == order_id,
                    Order.buyer_id == user_id
                ).first()
                
                if not order:
                    result['message'] = f'Order #{order_id} not found'
                    return result
                
                result['success'] = True
                result['message'] = f'Order #{order_id} status: {order.order_status}'
                result['data']['order'] = {
                    'id': order.id,
                    'status': order.order_status,
                    'total': float(order.total_amount),
                    'date': order.order_date.strftime('%Y-%m-%d'),
                    'items_count': len(order.items) if hasattr(order, 'items') else 0
                }
                return result
            
            elif intent == 'help':
                user = User.query.get(user_id)
                user_type = user.user_type if user else 'retailer'
                
                help_text = {
                    'retailer': 'You can say: "Order 5 kg tomatoes", "Check my order status", "Show me vegetables", "Track order 123"',
                    'vendor': 'You can say: "Add new product", "Check my orders", "Show sales report", "Update inventory"',
                    'admin': 'You can say: "Show reports", "View system status", "List all orders"'
                }
                
                result['success'] = True
                result['message'] = help_text.get(user_type, help_text['retailer'])
                return result
            
            else:
                result['message'] = f'I understood "{intent}" but cannot process it yet. Try: "Order product", "Check status", or "Help"'
                return result
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error processing command: {str(e)}',
                'action': 'error'
            }
    
    @staticmethod
    def generate_response(command_result, language='en'):
        """
        Generate natural language response based on command result
        
        Args:
            command_result: Result from process_command_action()
            language: 'en' or 'ta' for response language
        """
        try:
            if not VoiceService.configure_api():
                # Fallback to simple response
                return {
                    'success': True,
                    'text': command_result.get('message', 'Command processed'),
                    'language': language
                }
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
Generate a natural, conversational response in {"Tamil (தமிழ்)" if language == 'ta' else "English"}.

Action: {command_result.get('action', 'unknown')}
Success: {command_result.get('success', False)}
Message: {command_result.get('message', '')}
Data: {json.dumps(command_result.get('data', {}), indent=2)}

Create a friendly, helpful response that:
1. Confirms what was done
2. Mentions key information from the data
3. Suggests next steps if appropriate
4. Uses natural conversational language
5. Is concise (2-3 sentences max)

{"Respond in Tamil script (தமிழ்)." if language == 'ta' else "Respond in English."}

Return ONLY the response text, no additional formatting.
"""
            
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            return {
                'success': True,
                'text': response_text,
                'language': language
            }
            
        except Exception as e:
            return {
                'success': True,
                'text': command_result.get('message', 'Done'),
                'language': language
            }
