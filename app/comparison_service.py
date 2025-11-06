"""
Product Comparison Service
Handles vendor differentiation, comparison logic, and personalized recommendations
"""

from app import db
from app.models import (
    Product, User, Order, VendorRatingsCache, 
    VendorDeliveryMetrics, ProductComparison, ProductReview
)
from sqlalchemy import func, or_
from datetime import datetime, date, timedelta
from enum import Enum
import json
import uuid


class VendorTier(Enum):
    """Vendor tier classification based on performance"""
    PREMIUM = "PREMIUM"
    GOOD = "GOOD"
    BUDGET = "BUDGET"


class ProductComparisonService:
    """
    Service for comparing vendors selling the same product
    Provides scoring, ranking, and personalized recommendations
    """
    
    @staticmethod
    def search_products_with_vendors(product_name, filters=None, sort_by='value'):
        """
        Search for products by name and return all vendors selling it
        
        Args:
            product_name: Product name to search for
            filters: Dict with min_price, max_price, min_rating, max_delivery_time
            sort_by: 'price', 'rating', 'delivery_time', or 'value'
            
        Returns:
            List of vendor data with full comparison details
        """
        # Base query: find all active products matching name
        query = Product.query.filter(
            Product.product_name.ilike(f'%{product_name}%'),
            Product.is_active == True,
            Product.stock_quantity > 0
        )
        
        # Apply filters if provided
        if filters:
            if 'min_price' in filters and filters['min_price']:
                query = query.filter(Product.price >= filters['min_price'])
            if 'max_price' in filters and filters['max_price']:
                query = query.filter(Product.price <= filters['max_price'])
            if 'max_delivery_time' in filters and filters['max_delivery_time']:
                # Will filter after joining with delivery metrics
                pass
        
        products = query.all()
        
        # Build vendor comparison data
        vendors_data = []
        for product in products:
            vendor_data = ProductComparisonService._build_vendor_data(product)
            
            # Apply rating filter if specified
            if filters and 'min_rating' in filters and filters['min_rating']:
                if vendor_data['rating']['overall'] < filters['min_rating']:
                    continue
            
            # Apply delivery time filter if specified
            if filters and 'max_delivery_time' in filters and filters['max_delivery_time']:
                if vendor_data['metrics']['avg_delivery_time'] > filters['max_delivery_time']:
                    continue
            
            vendors_data.append(vendor_data)
        
        # Sort vendors
        vendors_data = ProductComparisonService._sort_vendors(vendors_data, sort_by)
        
        return {
            'product_name': product_name,
            'vendor_count': len(vendors_data),
            'vendors': vendors_data
        }
    
    @staticmethod
    def _build_vendor_data(product):
        """Build comprehensive vendor data for comparison"""
        vendor = product.vendor
        
        # Get cached ratings
        ratings_cache = VendorRatingsCache.query.filter_by(vendor_id=vendor.id).first()
        if not ratings_cache:
            # Create default cache if doesn't exist
            ratings_cache = ProductComparisonService._create_default_ratings_cache(vendor.id)
        
        # Get delivery metrics
        delivery_metrics = VendorDeliveryMetrics.query.filter_by(vendor_id=vendor.id).first()
        if not delivery_metrics:
            delivery_metrics = ProductComparisonService._create_default_delivery_metrics(vendor.id)
        
        # Get recent reviews
        recent_reviews = ProductReview.query.filter_by(
            vendor_id=vendor.id
        ).order_by(ProductReview.created_at.desc()).limit(3).all()
        
        reviews_data = [{
            'rating': (review.rating_quality + review.rating_delay + review.rating_communication) / 3,
            'comment': review.comment if review.comment else 'Great service',
            'date': review.created_at.strftime('%Y-%m-%d')
        } for review in recent_reviews]
        
        # Calculate value score
        value_score = ProductComparisonService.calculate_value_score(
            price=product.price,
            quality=ratings_cache.overall_rating,
            delivery_time=delivery_metrics.avg_delivery_time
        )
        
        # Determine tier
        tier = ProductComparisonService.determine_vendor_tier(
            price=product.price,
            rating=ratings_cache.overall_rating,
            delivery_time=delivery_metrics.avg_delivery_time
        )
        
        # Calculate days to expiry
        expiry_days = 0
        if product.expiry_date:
            expiry_days = (product.expiry_date - date.today()).days
            expiry_days = max(0, expiry_days)
        
        # Parse certifications
        certifications = []
        if product.certification:
            certifications = [c.strip() for c in product.certification.split(',')]
        
        return {
            'vendor_id': vendor.id,
            'vendor_name': vendor.business_name or vendor.name,
            'product_id': product.id,
            'price': float(product.price),
            'unit': product.unit,
            'moq': product.minimum_quantity if product.moq_enabled else 0,
            'rating': {
                'overall': round(ratings_cache.overall_rating, 2),
                'quality': round(ratings_cache.avg_quality_rating, 2),
                'punctuality': round(ratings_cache.avg_punctuality_rating, 2),
                'communication': round(ratings_cache.avg_communication_rating, 2)
            },
            'metrics': {
                'success_rate': round(ratings_cache.success_rate, 2),
                'on_time_rate': round(delivery_metrics.on_time_rate, 2),
                'repeat_customer_rate': round(ratings_cache.repeat_customer_rate, 2),
                'avg_delivery_time': delivery_metrics.avg_delivery_time,
                'total_reviews': ratings_cache.total_reviews
            },
            'product_details': {
                'freshness': product.freshness_level,
                'expiry_days': expiry_days,
                'quality_tier': product.quality_tier,
                'moq': product.minimum_quantity if product.moq_enabled else 0,
                'certifications': certifications,
                'stock_quantity': product.stock_quantity
            },
            'recent_reviews': reviews_data,
            'tier': tier.value,
            'value_score': value_score
        }
    
    @staticmethod
    def calculate_value_score(price, quality, delivery_time):
        """
        Calculate value score: Quality/Price ratio adjusted for delivery
        
        Algorithm:
        - Quality score (0-100): rating * 20 (5-star → 100 points)
        - Price score (0-100): Inverse price (lower = better)
        - Delivery score (0-100): Faster delivery = higher score
        - Weighted: 50% quality, 30% price, 20% delivery
        
        Returns:
            Float value between 0-10
        """
        # Normalize to 0-100 scale
        quality_score = quality * 20  # 5-star rating → 0-100
        
        # Price score: Lower price = higher score (normalize to typical range ₹10-100)
        if price > 0:
            price_score = max(0, 100 - (price * 1.0))  # Adjust multiplier based on typical prices
            price_score = min(100, price_score)
        else:
            price_score = 0
        
        # Delivery score: Faster = better (360 minutes = 6 hours = 0 points)
        delivery_score = max(0, 100 - (delivery_time / 3.6))  # 360 min → 0, 0 min → 100
        delivery_score = min(100, delivery_score)
        
        # Weighted calculation
        value_score = (quality_score * 0.5) + (price_score * 0.3) + (delivery_score * 0.2)
        
        # Convert to 0-10 scale
        return round(value_score / 10, 1)
    
    @staticmethod
    def determine_vendor_tier(price, rating, delivery_time):
        """
        Categorize vendor into tier based on performance
        
        PREMIUM: High quality (4.7+), fast delivery (<=4h)
        GOOD: Good quality (4.3+), reasonable delivery (<=6h)
        BUDGET: Below threshold
        """
        if rating >= 4.7 and delivery_time <= 240:  # 4 hours
            return VendorTier.PREMIUM
        elif rating >= 4.3 and delivery_time <= 360:  # 6 hours
            return VendorTier.GOOD
        else:
            return VendorTier.BUDGET
    
    @staticmethod
    def _sort_vendors(vendors_data, sort_by):
        """Sort vendors by specified criteria"""
        if sort_by == 'price':
            return sorted(vendors_data, key=lambda x: x['price'])
        elif sort_by == 'rating':
            return sorted(vendors_data, key=lambda x: x['rating']['overall'], reverse=True)
        elif sort_by == 'delivery_time':
            return sorted(vendors_data, key=lambda x: x['metrics']['avg_delivery_time'])
        elif sort_by == 'value':
            return sorted(vendors_data, key=lambda x: x['value_score'], reverse=True)
        else:
            return vendors_data
    
    @staticmethod
    def get_comparison_analysis(product_name):
        """
        Get detailed comparison analysis for all vendors selling a product
        
        Returns:
            Dict with vendor comparison matrix and analysis
        """
        result = ProductComparisonService.search_products_with_vendors(product_name)
        vendors = result['vendors']
        
        if not vendors:
            return {
                'product_name': product_name,
                'vendors_comparison_matrix': [],
                'analysis': {}
            }
        
        # Build comparison matrix
        comparison_matrix = []
        for vendor in vendors:
            comparison_matrix.append({
                'vendor_id': vendor['vendor_id'],
                'name': vendor['vendor_name'],
                'price': vendor['price'],
                'quality_rating': vendor['rating']['overall'],
                'delivery_hours': round(vendor['metrics']['avg_delivery_time'] / 60, 1),
                'success_rate': vendor['metrics']['success_rate'],
                'reviews_count': vendor['metrics']['total_reviews'],
                'freshness': vendor['product_details']['freshness'],
                'tier': vendor['tier']
            })
        
        # Analysis: find best in each category
        cheapest = min(vendors, key=lambda x: x['price'])
        best_quality = max(vendors, key=lambda x: x['rating']['overall'])
        fastest = min(vendors, key=lambda x: x['metrics']['avg_delivery_time'])
        best_value = max(vendors, key=lambda x: x['value_score'])
        most_reliable = max(vendors, key=lambda x: x['metrics']['success_rate'])
        
        analysis = {
            'cheapest_vendor': cheapest['vendor_id'],
            'best_quality_vendor': best_quality['vendor_id'],
            'fastest_delivery_vendor': fastest['vendor_id'],
            'best_value_vendor': best_value['vendor_id'],
            'most_reliable_vendor': most_reliable['vendor_id'],
            'price_range': {
                'min': cheapest['price'],
                'max': max(v['price'] for v in vendors)
            },
            'rating_range': {
                'min': min(v['rating']['overall'] for v in vendors),
                'max': best_quality['rating']['overall']
            }
        }
        
        return {
            'product_name': product_name,
            'vendors_comparison_matrix': comparison_matrix,
            'analysis': analysis
        }
    
    @staticmethod
    def get_personalized_recommendation(retailer_id, product_name, vendors_available):
        """
        Get AI-based recommendation based on retailer's purchase history
        
        Algorithm:
        1. Analyze retailer's past orders
        2. Identify preference patterns (quality vs price vs speed)
        3. Score each available vendor based on preferences
        4. Return best match with explanation
        """
        # Get retailer's order history
        past_orders = Order.query.filter_by(
            buyer_id=retailer_id,
            order_status='delivered'
        ).all()
        
        if not past_orders or len(past_orders) < 3:
            # New retailer or insufficient data → recommend highest rated
            return ProductComparisonService._recommend_for_new_retailer(vendors_available)
        
        # Analyze preference patterns
        avg_rating_chosen = 0
        avg_price_paid = 0
        count = 0
        
        for order in past_orders:
            if order.seller_id:
                ratings_cache = VendorRatingsCache.query.filter_by(vendor_id=order.seller_id).first()
                if ratings_cache:
                    avg_rating_chosen += ratings_cache.overall_rating
                    avg_price_paid += order.total_amount / max(order.items[0].quantity if order.items else 1, 1)
                    count += 1
        
        if count == 0:
            return ProductComparisonService._recommend_for_new_retailer(vendors_available)
        
        avg_rating_chosen = avg_rating_chosen / count
        avg_price_paid = avg_price_paid / count
        
        # Determine preference type and weights
        if avg_rating_chosen >= 4.5:
            # Quality-focused shopper
            preference_type = "quality-focused"
            weights = {"quality": 0.6, "price": 0.2, "delivery": 0.2}
        elif avg_price_paid < 45:  # Adjust threshold based on typical prices
            # Price-focused shopper
            preference_type = "price-focused"
            weights = {"quality": 0.2, "price": 0.6, "delivery": 0.2}
        else:
            # Balanced shopper
            preference_type = "balanced"
            weights = {"quality": 0.4, "price": 0.3, "delivery": 0.3}
        
        # Score each vendor
        vendor_scores = {}
        for vendor_id in vendors_available:
            product = Product.query.filter_by(
                vendor_id=vendor_id,
                product_name=product_name,
                is_active=True
            ).first()
            
            if not product:
                continue
            
            ratings_cache = VendorRatingsCache.query.filter_by(vendor_id=vendor_id).first()
            delivery_metrics = VendorDeliveryMetrics.query.filter_by(vendor_id=vendor_id).first()
            
            if not ratings_cache or not delivery_metrics:
                continue
            
            # Normalize scores to 0-1
            quality_score = ratings_cache.overall_rating / 5
            price_score = max(0, 1 - (product.price / 100))  # Adjust based on typical max price
            delivery_score = max(0, 1 - (delivery_metrics.avg_delivery_time / 480))  # 8 hours max
            
            # Calculate weighted score
            total_score = (
                (quality_score * weights["quality"]) +
                (price_score * weights["price"]) +
                (delivery_score * weights["delivery"])
            )
            
            vendor_scores[vendor_id] = {
                'score': total_score,
                'quality': ratings_cache.overall_rating,
                'price': product.price,
                'delivery_time': delivery_metrics.avg_delivery_time
            }
        
        if not vendor_scores:
            return ProductComparisonService._recommend_for_new_retailer(vendors_available)
        
        # Get vendor with highest score
        recommended_vendor_id = max(vendor_scores, key=lambda v: vendor_scores[v]['score'])
        recommended = vendor_scores[recommended_vendor_id]
        
        # Generate explanation
        if preference_type == "quality-focused":
            reason = f"You prefer high-quality vendors. This vendor has a {recommended['quality']:.1f}★ rating."
        elif preference_type == "price-focused":
            reason = f"You prefer competitive pricing. This vendor offers ₹{recommended['price']:.0f}/{product_name}."
        else:
            reason = f"Best balanced option: {recommended['quality']:.1f}★ quality at ₹{recommended['price']:.0f}."
        
        return {
            'recommended_vendor_id': recommended_vendor_id,
            'reason': reason,
            'recommendation_score': round(recommended['score'], 2),
            'analysis': {
                'your_avg_price_paid': round(avg_price_paid, 2),
                'your_quality_preference': round(avg_rating_chosen, 2),
                'preference_type': preference_type,
                'why_selected': reason
            }
        }
    
    @staticmethod
    def _recommend_for_new_retailer(vendors_available):
        """Recommend for retailer with no history - choose highest rated"""
        best_vendor_id = None
        best_rating = 0
        
        for vendor_id in vendors_available:
            ratings_cache = VendorRatingsCache.query.filter_by(vendor_id=vendor_id).first()
            if ratings_cache and ratings_cache.overall_rating > best_rating:
                best_rating = ratings_cache.overall_rating
                best_vendor_id = vendor_id
        
        if not best_vendor_id:
            best_vendor_id = vendors_available[0] if vendors_available else None
        
        return {
            'recommended_vendor_id': best_vendor_id,
            'reason': 'Highest rated vendor (recommended for new customers)',
            'recommendation_score': 0.8,
            'analysis': {
                'preference_type': 'new_customer',
                'why_selected': 'No order history yet. Recommending top-rated vendor.'
            }
        }
    
    @staticmethod
    def log_comparison(retailer_id, product_name, vendors_compared, selected_vendor_id=None, 
                      sort_preference=None, filters_applied=None):
        """
        Log a product comparison for analytics
        
        Returns:
            Comparison ID (UUID)
        """
        comparison_id = str(uuid.uuid4())
        
        comparison = ProductComparison(
            comparison_id=comparison_id,
            retailer_id=retailer_id,
            product_name=product_name,
            vendors_compared=json.dumps(vendors_compared),
            selected_vendor_id=selected_vendor_id,
            sort_preference=sort_preference,
            filters_applied=json.dumps(filters_applied) if filters_applied else None,
            created_at=datetime.utcnow()
        )
        
        db.session.add(comparison)
        db.session.commit()
        
        return comparison_id
    
    @staticmethod
    def get_vendor_profile(vendor_id):
        """
        Get detailed vendor profile with all metrics
        
        Returns:
            Complete vendor profile data
        """
        vendor = User.query.get(vendor_id)
        if not vendor or vendor.user_type != 'vendor':
            return None
        
        ratings_cache = VendorRatingsCache.query.filter_by(vendor_id=vendor_id).first()
        delivery_metrics = VendorDeliveryMetrics.query.filter_by(vendor_id=vendor_id).first()
        
        if not ratings_cache:
            ratings_cache = ProductComparisonService._create_default_ratings_cache(vendor_id)
        if not delivery_metrics:
            delivery_metrics = ProductComparisonService._create_default_delivery_metrics(vendor_id)
        
        # Get total orders
        total_orders = Order.query.filter_by(seller_id=vendor_id).count()
        success_count = Order.query.filter_by(
            seller_id=vendor_id,
            order_status='delivered'
        ).count()
        
        # Get recent reviews
        recent_reviews = ProductReview.query.filter_by(
            vendor_id=vendor_id
        ).order_by(ProductReview.created_at.desc()).limit(10).all()
        
        reviews_data = []
        for review in recent_reviews:
            if review.retailer:
                reviews_data.append({
                    'reviewer': f"{review.retailer.name} (Retailer)",
                    'rating': round((review.rating_quality + review.rating_delay + review.rating_communication) / 3, 1),
                    'quality': review.rating_quality,
                    'punctuality': review.rating_delay,
                    'communication': review.rating_communication,
                    'comment': review.comment or 'Great service',
                    'date': review.created_at.strftime('%Y-%m-%d')
                })
        
        return {
            'vendor_id': vendor.id,
            'name': vendor.business_name or vendor.name,
            'joined_date': vendor.created_at.strftime('%Y-%m-%d'),
            'location': vendor.address or 'Location not specified',
            'phone': vendor.phone,
            'city': vendor.city,
            'ratings': {
                'quality': round(ratings_cache.avg_quality_rating, 2),
                'punctuality': round(ratings_cache.avg_punctuality_rating, 2),
                'communication': round(ratings_cache.avg_communication_rating, 2),
                'overall': round(ratings_cache.overall_rating, 2)
            },
            'performance': {
                'total_orders': total_orders,
                'success_rate': round(ratings_cache.success_rate, 2),
                'repeat_customers': round(ratings_cache.repeat_customer_rate, 2),
                'avg_rating': round(ratings_cache.overall_rating, 2),
                'on_time_delivery': round(delivery_metrics.on_time_rate, 2)
            },
            'delivery_metrics': {
                'avg_time_minutes': delivery_metrics.avg_delivery_time,
                'avg_time_hours': round(delivery_metrics.avg_delivery_time / 60, 1),
                'min_time_minutes': delivery_metrics.min_delivery_time,
                'max_time_minutes': delivery_metrics.max_delivery_time,
                'on_time_count': delivery_metrics.delivery_on_time_count,
                'late_count': delivery_metrics.delivery_late_count
            },
            'recent_reviews': reviews_data,
            'total_reviews': ratings_cache.total_reviews
        }
    
    @staticmethod
    def _create_default_ratings_cache(vendor_id):
        """Create default ratings cache for new vendor"""
        cache = VendorRatingsCache(
            vendor_id=vendor_id,
            avg_quality_rating=4.0,
            avg_punctuality_rating=4.0,
            avg_communication_rating=4.0,
            overall_rating=4.0,
            total_reviews=0,
            success_rate=95.0,
            on_time_rate=90.0,
            repeat_customer_rate=0.0
        )
        db.session.add(cache)
        db.session.commit()
        return cache
    
    @staticmethod
    def _create_default_delivery_metrics(vendor_id):
        """Create default delivery metrics for new vendor"""
        metrics = VendorDeliveryMetrics(
            vendor_id=vendor_id,
            avg_delivery_time=240,  # 4 hours default
            min_delivery_time=120,
            max_delivery_time=360,
            delivery_on_time_count=0,
            delivery_late_count=0,
            total_deliveries=0
        )
        db.session.add(metrics)
        db.session.commit()
        return metrics
    
    @staticmethod
    def update_vendor_ratings_cache(vendor_id):
        """
        Update vendor ratings cache from ProductReview data
        Should be called after each new review
        """
        reviews = ProductReview.query.filter_by(vendor_id=vendor_id).all()
        
        if not reviews:
            return
        
        # Calculate averages
        total_reviews = len(reviews)
        avg_quality = sum(r.rating_quality for r in reviews) / total_reviews
        avg_punctuality = sum(r.rating_delay for r in reviews) / total_reviews
        avg_communication = sum(r.rating_communication for r in reviews) / total_reviews
        overall = (avg_quality + avg_punctuality + avg_communication) / 3
        
        # Calculate success rate from orders
        total_orders = Order.query.filter_by(seller_id=vendor_id).count()
        successful_orders = Order.query.filter_by(
            seller_id=vendor_id,
            order_status='delivered'
        ).count()
        success_rate = (successful_orders / total_orders * 100) if total_orders > 0 else 0
        
        # Get or create cache
        cache = VendorRatingsCache.query.filter_by(vendor_id=vendor_id).first()
        if not cache:
            cache = VendorRatingsCache(vendor_id=vendor_id)
            db.session.add(cache)
        
        # Update values
        cache.avg_quality_rating = round(avg_quality, 2)
        cache.avg_punctuality_rating = round(avg_punctuality, 2)
        cache.avg_communication_rating = round(avg_communication, 2)
        cache.overall_rating = round(overall, 2)
        cache.total_reviews = total_reviews
        cache.success_rate = round(success_rate, 2)
        cache.last_updated = datetime.utcnow()
        
        db.session.commit()
