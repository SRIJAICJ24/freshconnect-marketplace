"""
Vision/Camera Routes
Handle product image analysis and camera captures
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from app.decorators import vendor_required
from app.vision_service import VisionService
import base64

bp = Blueprint('vision', __name__, url_prefix='/vision')


@bp.route('/analyze-product', methods=['POST'])
@vendor_required
def analyze_product():
    """Analyze product image and return identified information"""
    
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({
                'success': False,
                'message': 'No image provided'
            }), 400
        
        # Analyze image
        result = VisionService.analyze_product_image(image_data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing image: {str(e)}'
        }), 500


@bp.route('/quality-check', methods=['POST'])
@vendor_required
def quality_check():
    """Perform quality assessment on product image"""
    
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({
                'success': False,
                'message': 'No image provided'
            }), 400
        
        # Analyze quality
        result = VisionService.analyze_for_quality_check(image_data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error in quality check: {str(e)}'
        }), 500


@bp.route('/identify-multiple', methods=['POST'])
@vendor_required
def identify_multiple():
    """Identify multiple products in a single image"""
    
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({
                'success': False,
                'message': 'No image provided'
            }), 400
        
        # Identify products
        result = VisionService.identify_multiple_products(image_data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error identifying products: {str(e)}'
        }), 500


@bp.route('/camera-demo')
@vendor_required
def camera_demo():
    """Demo page for testing camera functionality"""
    return render_template('vision/camera_demo.html')
