"""
Voice Assistant Routes
Handle voice commands in Tamil and English
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from app.voice_service import VoiceService
from app import db

bp = Blueprint('voice', __name__, url_prefix='/voice')


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
