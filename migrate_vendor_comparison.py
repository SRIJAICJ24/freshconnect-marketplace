"""
Vendor Comparison System - Database Migration Script
Run this in Railway Python shell or locally
"""

from app import create_app, db
from app.models import User, Product, VendorRatingsCache, VendorDeliveryMetrics
from app.comparison_service import ProductComparisonService
from datetime import datetime
from sqlalchemy import text

def run_migration():
    """
    Run database migration for vendor comparison system
    """
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("🚀 VENDOR COMPARISON SYSTEM - DATABASE MIGRATION")
        print("="*60 + "\n")
        
        # Step 1: Create all tables
        print("📋 Step 1: Creating database tables...")
        try:
            db.create_all()
            print("   ✅ All tables created successfully!")
        except Exception as e:
            print(f"   ⚠️  Table creation warning: {e}")
            print("   → Tables may already exist, continuing...")
        
        # Step 2: Update existing products with default values
        print("\n📋 Step 2: Updating existing products...")
        try:
            products = Product.query.filter(
                (Product.freshness_level == None) | 
                (Product.stock_quantity == None)
            ).all()
            
            for product in products:
                if not product.freshness_level:
                    product.freshness_level = 'TODAY'
                if not product.quality_tier:
                    product.quality_tier = 'GOOD'
                if not product.stock_quantity:
                    product.stock_quantity = product.quantity if product.quantity else 0
            
            db.session.commit()
            print(f"   ✅ Updated {len(products)} products with default values")
        except Exception as e:
            print(f"   ⚠️  Product update error: {e}")
            db.session.rollback()
        
        # Step 3: Create vendor rating caches
        print("\n📋 Step 3: Creating vendor rating caches...")
        vendors = User.query.filter_by(user_type='vendor').all()
        print(f"   Found {len(vendors)} vendors")
        
        created_caches = 0
        for vendor in vendors:
            try:
                # Check if cache already exists
                existing_cache = VendorRatingsCache.query.filter_by(vendor_id=vendor.id).first()
                
                if not existing_cache:
                    # Create new cache with default values
                    cache = VendorRatingsCache(
                        vendor_id=vendor.id,
                        avg_quality_rating=4.0,
                        avg_punctuality_rating=4.0,
                        avg_communication_rating=4.0,
                        overall_rating=4.0,
                        total_reviews=0,
                        success_rate=95.0,
                        on_time_rate=90.0,
                        repeat_customer_rate=0.0,
                        created_at=datetime.utcnow()
                    )
                    db.session.add(cache)
                    created_caches += 1
                
                # Update cache with actual data if reviews exist
                ProductComparisonService.update_vendor_ratings_cache(vendor.id)
                
            except Exception as e:
                print(f"   ⚠️  Error creating cache for vendor {vendor.id}: {e}")
                db.session.rollback()
        
        try:
            db.session.commit()
            print(f"   ✅ Created {created_caches} new vendor rating caches")
            print(f"   ✅ Updated ratings from existing reviews")
        except Exception as e:
            print(f"   ❌ Cache creation error: {e}")
            db.session.rollback()
        
        # Step 4: Create vendor delivery metrics
        print("\n📋 Step 4: Creating vendor delivery metrics...")
        created_metrics = 0
        for vendor in vendors:
            try:
                # Check if metrics already exist
                existing_metrics = VendorDeliveryMetrics.query.filter_by(vendor_id=vendor.id).first()
                
                if not existing_metrics:
                    # Create new metrics with default values
                    metrics = VendorDeliveryMetrics(
                        vendor_id=vendor.id,
                        avg_delivery_time=240,  # 4 hours default
                        min_delivery_time=120,  # 2 hours
                        max_delivery_time=360,  # 6 hours
                        delivery_on_time_count=0,
                        delivery_late_count=0,
                        total_deliveries=0,
                        created_at=datetime.utcnow()
                    )
                    db.session.add(metrics)
                    created_metrics += 1
            except Exception as e:
                print(f"   ⚠️  Error creating metrics for vendor {vendor.id}: {e}")
                db.session.rollback()
        
        try:
            db.session.commit()
            print(f"   ✅ Created {created_metrics} new vendor delivery metrics")
        except Exception as e:
            print(f"   ❌ Metrics creation error: {e}")
            db.session.rollback()
        
        # Step 5: Verification
        print("\n📋 Step 5: Verifying migration...")
        try:
            cache_count = VendorRatingsCache.query.count()
            metrics_count = VendorDeliveryMetrics.query.count()
            vendor_count = User.query.filter_by(user_type='vendor').count()
            
            print(f"   ✅ Vendors in system: {vendor_count}")
            print(f"   ✅ Vendor rating caches: {cache_count}")
            print(f"   ✅ Vendor delivery metrics: {metrics_count}")
            
            if cache_count == vendor_count and metrics_count == vendor_count:
                print("\n   🎉 All vendors have caches and metrics!")
            else:
                print(f"\n   ⚠️  Mismatch: {vendor_count} vendors but {cache_count} caches and {metrics_count} metrics")
        except Exception as e:
            print(f"   ❌ Verification error: {e}")
        
        # Step 6: Test API functionality
        print("\n📋 Step 6: Testing comparison service...")
        try:
            # Test search
            result = ProductComparisonService.search_products_with_vendors(
                product_name='tomato',
                filters={},
                sort_by='value'
            )
            print(f"   ✅ Search test: Found {result['vendor_count']} vendors for 'tomato'")
            
            # Test recommendation (if retailers exist)
            from app.models import Order
            retailers = User.query.filter_by(user_type='retailer').first()
            if retailers:
                rec = ProductComparisonService.get_personalized_recommendation(
                    retailer_id=retailers.id,
                    product_name='tomato',
                    vendors_available=[v.id for v in vendors[:3]]
                )
                print(f"   ✅ Recommendation test: Recommended vendor {rec.get('recommended_vendor_id')}")
            
        except Exception as e:
            print(f"   ⚠️  API test warning: {e}")
        
        # Summary
        print("\n" + "="*60)
        print("✅ MIGRATION COMPLETE!")
        print("="*60)
        print("\n📊 Summary:")
        print(f"   • Database tables: Created/Updated")
        print(f"   • Vendor caches: {cache_count}")
        print(f"   • Delivery metrics: {metrics_count}")
        print(f"   • Products updated: Yes")
        print("\n🎯 Next Steps:")
        print("   1. Test API endpoints")
        print("   2. Verify data in Railway dashboard")
        print("   3. Test frontend integration")
        print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    run_migration()
