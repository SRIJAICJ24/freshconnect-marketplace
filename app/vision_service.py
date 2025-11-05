"""
Vision Service for Product Recognition
Uses Gemini Vision API to identify products from images
"""

import google.generativeai as genai
import os
from PIL import Image
import io
import base64
import json


class VisionService:
    """
    Service for analyzing product images using Gemini Vision API
    """
    
    # Configure Gemini API
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    
    @staticmethod
    def configure_api():
        """Configure Gemini API with key"""
        if VisionService.GEMINI_API_KEY:
            genai.configure(api_key=VisionService.GEMINI_API_KEY)
            return True
        return False
    
    @staticmethod
    def analyze_product_image(image_data):
        """
        Analyze product image and extract information
        
        Args:
            image_data: Base64 encoded image or file path
            
        Returns:
            dict with product information
        """
        try:
            # Configure API
            if not VisionService.configure_api():
                return {
                    'success': False,
                    'message': 'Gemini API key not configured. Please set GEMINI_API_KEY environment variable.'
                }
            
            # Load image
            if image_data.startswith('data:image'):
                # Base64 encoded image
                image_data = image_data.split(',')[1]
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
            else:
                # File path
                image = Image.open(image_data)
            
            # Create model
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Prepare prompt for product identification
            prompt = """
            Analyze this image of a fresh produce product and provide the following information in JSON format:
            
            {
                "product_name": "Name of the product (e.g., Tomato, Potato, Apple)",
                "category": "Category (must be one of: Vegetables, Fruits, Grains, Dairy, Meat, Other)",
                "description": "Brief description of the product (2-3 sentences)",
                "estimated_weight_per_unit": "Estimated weight in kg (e.g., 0.15 for small tomato, 0.5 for cabbage)",
                "unit": "kg or pieces",
                "quality_assessment": "Quality rating: Excellent/Good/Fair/Poor",
                "freshness_indicators": "Visual freshness indicators observed",
                "suggested_price_range": "Estimated price range in INR per kg (e.g., 40-60)",
                "storage_tips": "Brief storage recommendation",
                "confidence": "Confidence level: High/Medium/Low"
            }
            
            Only provide the JSON response, no additional text.
            If you cannot identify the product clearly, set confidence to "Low" and provide best estimates.
            """
            
            # Generate response
            response = model.generate_content([prompt, image])
            
            # Parse response
            result_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            elif result_text.startswith('```'):
                result_text = result_text.replace('```', '').strip()
            
            # Parse JSON
            product_info = json.loads(result_text)
            
            return {
                'success': True,
                'product_info': product_info,
                'raw_response': response.text
            }
            
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'message': f'Could not parse AI response: {str(e)}',
                'raw_response': result_text if 'result_text' in locals() else 'No response'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error analyzing image: {str(e)}'
            }
    
    @staticmethod
    def analyze_for_quality_check(image_data):
        """
        Analyze product image for quality assessment only
        Used for quality control and grading
        """
        try:
            if not VisionService.configure_api():
                return {
                    'success': False,
                    'message': 'API key not configured'
                }
            
            # Load image
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
            else:
                image = Image.open(image_data)
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = """
            Analyze this fresh produce image and provide a quality assessment in JSON format:
            
            {
                "overall_quality": "Excellent/Good/Fair/Poor",
                "freshness_score": "1-10 rating",
                "visual_defects": ["List any visible defects or issues"],
                "color_assessment": "Description of color quality",
                "ripeness_level": "Unripe/Ripe/Overripe",
                "estimated_shelf_life_days": "Estimated days until spoilage",
                "recommendations": "Recommendations for handling or pricing"
            }
            
            Provide only the JSON response.
            """
            
            response = model.generate_content([prompt, image])
            result_text = response.text.strip()
            
            # Clean JSON
            if result_text.startswith('```'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            quality_info = json.loads(result_text)
            
            return {
                'success': True,
                'quality_info': quality_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error in quality check: {str(e)}'
            }
    
    @staticmethod
    def identify_multiple_products(image_data):
        """
        Identify multiple products in a single image
        Useful for bulk product uploads
        """
        try:
            if not VisionService.configure_api():
                return {
                    'success': False,
                    'message': 'API key not configured'
                }
            
            # Load image
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
            else:
                image = Image.open(image_data)
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = """
            Identify all fresh produce products visible in this image.
            Provide a JSON array of products:
            
            [
                {
                    "product_name": "Product 1",
                    "category": "Category",
                    "estimated_quantity": "How many visible",
                    "position": "Location in image (left/center/right/top/bottom)"
                },
                ...
            ]
            
            Provide only the JSON array.
            """
            
            response = model.generate_content([prompt, image])
            result_text = response.text.strip()
            
            # Clean JSON
            if result_text.startswith('```'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            products = json.loads(result_text)
            
            return {
                'success': True,
                'products': products,
                'count': len(products)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error identifying products: {str(e)}'
            }
