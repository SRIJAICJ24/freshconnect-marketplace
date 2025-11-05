from flask import Blueprint, request, jsonify
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
        # Use SmartChatbotService for command processing (FEATURE 4)
        smart_service = SmartChatbotService()
        result = smart_service.process_command(message, current_user.id, current_user.user_type)
        
        # Return structured response for frontend handling
        return jsonify(result)
    except Exception as e:
        print(f"[CHATBOT API ERROR] {str(e)}")
        # Fallback to simple chatbot if command processing fails
        try:
            service = ChatbotService()
            response = service.get_response(message, current_user.user_type, current_user.id)
            return jsonify({'type': 'text', 'message': response})
        except:
            return jsonify({'type': 'error', 'message': str(e)}), 500
