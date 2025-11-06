"""
Product Comparison & Vendor Differentiation API Routes
"""

from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app.comparison_service import ProductComparisonService
from app.models import Product, VendorRatingsCache
from app import db

bp = Blueprint('comparison', __name__, url_prefix='/api/comparison')


@bp.route('/products/search', methods=['POST'])
@login_required
def search_products():
    """
    Search products and return all vendors selling it with comparison data
    
    Request Body:
    {
        "product_name": "tomato",
        "sort_by": "price|rating|delivery_time|value",
        "filter": {
            "min_price": 30,
            "max_price": 50,
            "min_rating": 4.0,
            "max_delivery_time": 360
        }
    }
    """
    try:
        data = request.get_json()
        product_name = data.get('product_name', '').strip()
        
        if not product_name:
            return jsonify({
                'success': False,
                'message': 'Product name is required'
            }), 400
        
        sort_by = data.get('sort_by', 'value')
        filters = data.get('filter', {})
        
        # Search using comparison service
        result = ProductComparisonService.search_products_with_vendors(
            product_name=product_name,
            filters=filters,
            sort_by=sort_by
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        print(f"❌ Error in search_products: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/products/<int:product_id>/compare', methods=['GET'])
@login_required
def compare_product(product_id):
    """
    Get detailed comparison of all vendors selling this product
    """
    try:
        product = Product.query.get_or_404(product_id)
        
        # Get comparison analysis
        result = ProductComparisonService.get_comparison_analysis(product.product_name)
        
        return jsonify({
            'success': True,
            'data': {
                'product_id': product_id,
                'product_name': product.product_name,
                'vendors_comparison_matrix': result['vendors_comparison_matrix'],
                'analysis': result['analysis']
            }
        })
        
    except Exception as e:
        print(f"❌ Error in compare_product: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/recommendations/personalized', methods=['POST'])
@login_required
def get_personalized_recommendation():
    """
    Get AI-based personalized vendor recommendation
    
    Request Body:
    {
        "product_name": "Tomato",
        "vendors_available": [123, 456, 789]
    }
    """
    try:
        data = request.get_json()
        product_name = data.get('product_name', '').strip()
        vendors_available = data.get('vendors_available', [])
        
        if not product_name or not vendors_available:
            return jsonify({
                'success': False,
                'message': 'Product name and vendors list are required'
            }), 400
        
        # Get personalized recommendation
        recommendation = ProductComparisonService.get_personalized_recommendation(
            retailer_id=current_user.id,
            product_name=product_name,
            vendors_available=vendors_available
        )
        
        return jsonify({
            'success': True,
            'data': recommendation
        })
        
    except Exception as e:
        print(f"❌ Error in get_personalized_recommendation: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/vendors/<int:vendor_id>/profile', methods=['GET'])
@login_required
def get_vendor_profile(vendor_id):
    """
    Get detailed vendor profile with all metrics
    """
    try:
        profile = ProductComparisonService.get_vendor_profile(vendor_id)
        
        if not profile:
            return jsonify({
                'success': False,
                'message': 'Vendor not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': profile
        })
        
    except Exception as e:
        print(f"❌ Error in get_vendor_profile: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/products/compare/log', methods=['POST'])
@login_required
def log_comparison():
    """
    Log a product comparison action for analytics
    
    Request Body:
    {
        "product_name": "Tomato",
        "vendors_compared": [123, 456, 789],
        "selected_vendor": 456,
        "sort_preference": "value",
        "filters_applied": {"min_price": 30, "max_price": 50}
    }
    """
    try:
        data = request.get_json()
        product_name = data.get('product_name', '').strip()
        vendors_compared = data.get('vendors_compared', [])
        selected_vendor = data.get('selected_vendor')
        sort_preference = data.get('sort_preference')
        filters_applied = data.get('filters_applied')
        
        if not product_name or not vendors_compared:
            return jsonify({
                'success': False,
                'message': 'Product name and vendors list are required'
            }), 400
        
        # Log comparison
        comparison_id = ProductComparisonService.log_comparison(
            retailer_id=current_user.id,
            product_name=product_name,
            vendors_compared=vendors_compared,
            selected_vendor_id=selected_vendor,
            sort_preference=sort_preference,
            filters_applied=filters_applied
        )
        
        return jsonify({
            'success': True,
            'data': {
                'comparison_id': comparison_id,
                'message': 'Comparison logged successfully'
            }
        })
        
    except Exception as e:
        print(f"❌ Error in log_comparison: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ============ FRONTEND ROUTES ============

@bp.route('/search-page', methods=['GET'])
@login_required
def search_page():
    """Render product comparison search page"""
    product_name = request.args.get('product', '')
    return render_template('comparison/search.html', product_name=product_name)


@bp.route('/compare-page/<product_name>', methods=['GET'])
@login_required
def compare_page(product_name):
    """Render comparison matrix page"""
    return render_template('comparison/compare.html', product_name=product_name)


@bp.route('/vendor-profile/<int:vendor_id>', methods=['GET'])
@login_required
def vendor_profile_page(vendor_id):
    """Render vendor detail profile page"""
    return render_template('comparison/vendor_profile.html', vendor_id=vendor_id)
