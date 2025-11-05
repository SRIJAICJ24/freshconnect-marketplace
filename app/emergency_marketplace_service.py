"""
Emergency Marketplace Service

Allows vendors to quickly sell expiring products at discounts
Provides retailers with special deals
Tracks waste prevention metrics
"""

from app import db
from app.models import Product, Order, EmergencyMarketplaceMetrics, User, OrderItem
from datetime import datetime, timedelta, date
import random


class EmergencyMarketplaceService:
    """
    Emergency Marketplace Management
    
    Allows vendors to quickly sell expiring products at discounts
    Provides retailers with special deals
    Tracks waste prevention metrics
    """
    
    # Configuration
    AUTO_FLAG_DAYS_BEFORE_EXPIRY = 3  # Auto-flag if expiring in 3 days
    MIN_DISCOUNT = 25  # Minimum 25% discount for emergency sales
    MAX_DISCOUNT = 70  # Maximum 70% discount
    
    @staticmethod
    def auto_flag_expiring_products():
        """
        MOCK: Auto-flag products as emergency if expiring soon
        
        Runs daily/scheduled:
        - Check all active products
        - If expiry_date <= today + AUTO_FLAG_DAYS
        - Mark as emergency with suggested discount
        """
        
        cutoff_date = date.today() + timedelta(days=EmergencyMarketplaceService.AUTO_FLAG_DAYS_BEFORE_EXPIRY)
        
        # Find products expiring soon
        expiring_products = Product.query.filter(
            Product.expiry_date <= cutoff_date,
            Product.expiry_date > date.today(),
            Product.is_active == True,
            Product.is_emergency == False
        ).all()
        
        auto_flagged = 0
        
        for product in expiring_products:
            days_left = (product.expiry_date - date.today()).days
            
            # MOCK: Suggest discount based on days left
            if days_left == 0:
                suggested_discount = 60  # Expires today - 60% off
            elif days_left == 1:
                suggested_discount = 50  # Tomorrow - 50% off
            elif days_left == 2:
                suggested_discount = 40  # In 2 days - 40% off
            else:
                suggested_discount = 30  # In 3 days - 30% off
            
            # Mark as emergency with suggested discount
            product.mark_as_emergency(suggested_discount)
            db.session.add(product)
            auto_flagged += 1
            
            print(f"[AUTO-FLAG] {product.product_name} from {product.vendor.business_name}: {suggested_discount}% off")
        
        db.session.commit()
        
        return {
            'auto_flagged': auto_flagged,
            'message': f'Auto-flagged {auto_flagged} products as emergency'
        }
    
    @staticmethod
    def get_emergency_marketplace_products(category=None, min_discount=0, sort_by='urgency'):
        """
        Get all emergency marketplace products
        
        Sort options:
        - urgency: Most urgent first (expiring soon)
        - discount: Highest discount first
        - newest: Recently marked
        - vendor: Group by vendor
        """
        
        query = Product.query.filter_by(
            is_emergency=True,
            is_active=True
        )
        
        # Filter by category if provided
        if category:
            query = query.filter_by(category=category)
        
        # Filter by minimum discount
        if min_discount > 0:
            query = query.filter(Product.emergency_discount >= min_discount)
        
        products = query.all()
        
        # Sort based on preference
        if sort_by == 'urgency':
            # Sort by days_until_expiry ascending (most urgent first)
            products.sort(key=lambda p: (p.days_until_expiry if p.days_until_expiry is not None else 999, -p.emergency_discount))
        elif sort_by == 'discount':
            # Highest discount first
            products.sort(key=lambda p: p.emergency_discount, reverse=True)
        elif sort_by == 'newest':
            # Recently marked first
            products.sort(key=lambda p: p.emergency_marked_at if p.emergency_marked_at else datetime.min, reverse=True)
        elif sort_by == 'vendor':
            # Group by vendor
            products.sort(key=lambda p: p.vendor.business_name)
        
        return products
    
    @staticmethod
    def get_emergency_categories():
        """Get list of product categories with emergency items"""
        
        emergency_products = Product.query.filter_by(
            is_emergency=True,
            is_active=True
        ).all()
        
        categories = set()
        for product in emergency_products:
            categories.add(product.category)
        
        return sorted(list(categories))
    
    @staticmethod
    def mark_vendor_product_emergency(product_id, discount_percentage, vendor_id):
        """
        Vendor manually marks product as emergency sale
        
        Validates:
        - Product belongs to vendor
        - Discount is within acceptable range
        - Product is not already emergency
        """
        
        try:
            product = Product.query.get_or_404(product_id)
            
            # Verify ownership
            if product.vendor_id != vendor_id:
                return False, "Unauthorized: Product doesn't belong to you"
            
            # Validate discount
            if discount_percentage < EmergencyMarketplaceService.MIN_DISCOUNT:
                return False, f"Minimum discount is {EmergencyMarketplaceService.MIN_DISCOUNT}%"
            
            if discount_percentage > EmergencyMarketplaceService.MAX_DISCOUNT:
                return False, f"Maximum discount is {EmergencyMarketplaceService.MAX_DISCOUNT}%"
            
            # Check if already emergency
            if product.is_emergency:
                return False, "Product is already in emergency sale"
            
            # Check expiry date
            if product.expiry_date and product.expiry_date <= date.today():
                return False, "Product has already expired"
            
            # Mark as emergency
            product.mark_as_emergency(discount_percentage)
            db.session.commit()
            
            print(f"[EMERGENCY] {product.product_name} marked by {product.vendor.business_name}: {discount_percentage}% off")
            
            return True, {
                'message': 'Product marked as emergency!',
                'product_name': product.product_name,
                'original_price': product.original_price_backup,
                'discount': discount_percentage,
                'new_price': product.price,
                'expiry': product.expiry_date.strftime('%d-%m-%Y') if product.expiry_date else 'Not set'
            }
        
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def remove_emergency_status(product_id, vendor_id):
        """Vendor removes emergency status from product"""
        
        try:
            product = Product.query.get_or_404(product_id)
            
            if product.vendor_id != vendor_id:
                return False, "Unauthorized"
            
            if not product.is_emergency:
                return False, "Product is not in emergency sale"
            
            product.remove_emergency()
            db.session.commit()
            
            print(f"[REMOVED] {product.product_name} removed from emergency")
            
            return True, "Removed from emergency marketplace"
        
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def calculate_and_update_metrics(target_date=None):
        """
        Calculate daily metrics for emergency marketplace
        
        Metrics tracked:
        - Products on emergency
        - Items sold
        - Waste prevented
        - Financial impact
        """
        
        if target_date is None:
            target_date = date.today()
        
        try:
            # Get emergency products
            emergency_products = Product.query.filter_by(
                is_emergency=True,
                is_active=True
            ).all()
            
            total_emergency = len(emergency_products)
            
            # Calculate financial impact
            total_original_value = sum(
                (p.original_price_backup or p.price) * p.quantity 
                for p in emergency_products
            )
            total_emergency_value = sum(p.price * p.quantity for p in emergency_products)
            total_discount_given = total_original_value - total_emergency_value
            
            # Estimate waste prevented (MOCK: assume 50% would be wasted without emergency marketplace)
            estimated_waste_kg = sum(p.quantity * 0.5 for p in emergency_products)
            
            # Count unique vendors and retailers
            vendors_with_emergency = len(set(p.vendor_id for p in emergency_products))
            
            # Get orders with emergency products from today
            orders_today = Order.query.filter(
                Order.created_at >= datetime.combine(target_date, datetime.min.time()),
                Order.created_at < datetime.combine(target_date + timedelta(days=1), datetime.min.time())
            ).all()
            
            emergency_orders = [o for o in orders_today if any(item.product.is_emergency for item in o.items)]
            retailers_buying = len(set(o.buyer_id for o in emergency_orders))
            items_sold = sum(
                sum(item.quantity for item in o.items if item.product.is_emergency) 
                for o in emergency_orders
            )
            sales_value = sum(o.total_amount for o in emergency_orders)
            
            # Create/update metrics
            metrics = EmergencyMarketplaceMetrics.query.filter_by(date=target_date).first()
            
            if not metrics:
                metrics = EmergencyMarketplaceMetrics(date=target_date)
            
            metrics.total_emergency_products = total_emergency
            metrics.total_emergency_items_sold = int(items_sold)
            metrics.original_value_at_risk = total_original_value
            metrics.emergency_sale_value = total_emergency_value
            metrics.total_discount_given = total_discount_given
            metrics.vendor_recovery_value = sales_value
            metrics.estimated_waste_prevented_kg = estimated_waste_kg
            metrics.unique_vendors = vendors_with_emergency
            metrics.unique_retailers = retailers_buying
            
            db.session.add(metrics)
            db.session.commit()
            
            print(f"[METRICS] Updated for {target_date}: {total_emergency} products, {items_sold} items sold")
            
            return metrics
        
        except Exception as e:
            db.session.rollback()
            print(f"[METRICS ERROR] {str(e)}")
            return None
    
    @staticmethod
    def get_metrics_summary(days=7):
        """
        Get summary metrics for last N days
        
        Returns:
        - Total waste prevented (kg)
        - Total money given back to retailers
        - Total vendors participating
        - Trending data for charts
        """
        
        start_date = date.today() - timedelta(days=days)
        
        metrics = EmergencyMarketplaceMetrics.query.filter(
            EmergencyMarketplaceMetrics.date >= start_date
        ).all()
        
        if not metrics:
            return {
                'waste_prevented_kg': 0,
                'retailer_savings': 0,
                'vendor_recovery': 0,
                'vendors_count': 0,
                'retailers_count': 0,
                'items_sold': 0,
                'trend': []
            }
        
        summary = {
            'waste_prevented_kg': round(sum(m.estimated_waste_prevented_kg for m in metrics), 2),
            'retailer_savings': round(sum(m.total_discount_given for m in metrics), 2),
            'vendor_recovery': round(sum(m.vendor_recovery_value for m in metrics), 2),
            'vendors_count': max((m.unique_vendors for m in metrics), default=0),
            'retailers_count': max((m.unique_retailers for m in metrics), default=0),
            'items_sold': sum(m.total_emergency_items_sold for m in metrics),
            'trend': [
                {
                    'date': m.date.strftime('%d-%m'),
                    'products': m.total_emergency_products,
                    'sold': m.total_emergency_items_sold,
                    'waste_prevented_kg': m.estimated_waste_prevented_kg
                }
                for m in sorted(metrics, key=lambda x: x.date)
            ]
        }
        
        return summary
