"""
Initialize Emergency Marketplace with Sample Data

Creates sample products with expiry dates and marks some as emergency sales
"""

from app import create_app, db
from app.models import Product, User
from app.emergency_marketplace_service import EmergencyMarketplaceService
from datetime import datetime, timedelta, date
import random

def create_sample_emergency_products():
    """Create products with approaching expiry dates"""
    
    print("="*60)
    print("Creating Emergency Marketplace Sample Data")
    print("="*60)
    
    # Get vendors
    vendors = User.query.filter_by(user_type='vendor').all()
    
    if not vendors:
        print("No vendors found! Run seed_data.py first.")
        return
    
    vendor = vendors[0]
    print(f"\nUsing vendor: {vendor.business_name}")
    
    # Sample products with different expiry urgencies
    emergency_products = [
        {
            'name': 'Fresh Tomatoes (Expiring Today)',
            'category': 'Vegetables',
            'price': 40.0,
            'quantity': 100.0,
            'unit': 'kg',
            'expiry_days': 0,  # Expires today
            'discount': 60  # 60% off
        },
        {
            'name': 'Red Onions (Expiring Tomorrow)',
            'category': 'Vegetables',
            'price': 35.0,
            'quantity': 150.0,
            'unit': 'kg',
            'expiry_days': 1,  # Expires tomorrow
            'discount': 50  # 50% off
        },
        {
            'name': 'Carrots (2 Days Left)',
            'category': 'Vegetables',
            'price': 30.0,
            'quantity': 80.0,
            'unit': 'kg',
            'expiry_days': 2,  # 2 days
            'discount': 40  # 40% off
        },
        {
            'name': 'Spinach (3 Days Left)',
            'category': 'Vegetables',
            'price': 50.0,
            'quantity': 60.0,
            'unit': 'kg',
            'expiry_days': 3,  # 3 days
            'discount': 35  # 35% off
        },
        {
            'name': 'Green Beans (Expiring Soon)',
            'category': 'Vegetables',
            'price': 45.0,
            'quantity': 70.0,
            'unit': 'kg',
            'expiry_days': 2,
            'discount': 45
        },
        {
            'name': 'Bell Peppers (Limited Time)',
            'category': 'Vegetables',
            'price': 60.0,
            'quantity': 50.0,
            'unit': 'kg',
            'expiry_days': 3,
            'discount': 30
        },
        {
            'name': 'Cucumbers (Urgent Sale)',
            'category': 'Vegetables',
            'price': 25.0,
            'quantity': 90.0,
            'unit': 'kg',
            'expiry_days': 1,
            'discount': 55
        },
        {
            'name': 'Cabbages (Clearance)',
            'category': 'Vegetables',
            'price': 20.0,
            'quantity': 120.0,
            'unit': 'kg',
            'expiry_days': 2,
            'discount': 42
        }
    ]
    
    created_count = 0
    
    for prod_data in emergency_products:
        # Check if product already exists
        existing = Product.query.filter_by(
            vendor_id=vendor.id,
            product_name=prod_data['name']
        ).first()
        
        if existing:
            print(f"  Product '{prod_data['name']}' already exists, skipping...")
            continue
        
        # Create product
        expiry_date = date.today() + timedelta(days=prod_data['expiry_days'])
        
        product = Product(
            vendor_id=vendor.id,
            product_name=prod_data['name'],
            category=prod_data['category'],
            description=f"Emergency sale! {prod_data['discount']}% off. Limited quantity available.",
            price=prod_data['price'],
            quantity=prod_data['quantity'],
            unit=prod_data['unit'],
            expiry_date=expiry_date,
            is_active=True,
            moq_enabled=False
        )
        
        db.session.add(product)
        db.session.flush()  # Get product ID
        
        # Mark as emergency
        product.mark_as_emergency(prod_data['discount'])
        
        print(f"  ✓ Created: {prod_data['name']}")
        print(f"    - Original: ₹{prod_data['price']}/kg → Emergency: ₹{product.price:.2f}/kg")
        print(f"    - Discount: {prod_data['discount']}%, Expires: {expiry_date.strftime('%d-%m-%Y')}")
        
        created_count += 1
    
    db.session.commit()
    
    print(f"\n✓ Created {created_count} emergency products")
    return created_count


def run_auto_flag():
    """Run auto-flag to mark additional expiring products"""
    
    print("\n" + "="*60)
    print("Running Auto-Flag for Expiring Products")
    print("="*60)
    
    result = EmergencyMarketplaceService.auto_flag_expiring_products()
    
    print(f"\n{result['message']}")
    print(f"Auto-flagged: {result['auto_flagged']} products")
    
    return result


def calculate_initial_metrics():
    """Calculate initial metrics"""
    
    print("\n" + "="*60)
    print("Calculating Metrics")
    print("="*60)
    
    metrics = EmergencyMarketplaceService.calculate_and_update_metrics()
    
    if metrics:
        print(f"\n✓ Metrics calculated for {metrics.date}")
        print(f"  - Emergency products: {metrics.total_emergency_products}")
        print(f"  - Waste prevented: {metrics.estimated_waste_prevented_kg:.2f} kg")
        print(f"  - Retailer savings: ₹{metrics.total_discount_given:,.2f}")
    else:
        print("✗ Error calculating metrics")
    
    return metrics


def display_summary():
    """Display summary of emergency marketplace"""
    
    print("\n" + "="*60)
    print("Emergency Marketplace Summary")
    print("="*60)
    
    # Get all emergency products
    emergency_products = Product.query.filter_by(is_emergency=True).all()
    
    if not emergency_products:
        print("\nNo emergency products found.")
        return
    
    print(f"\nTotal Emergency Products: {len(emergency_products)}")
    print("\nBreakdown by Urgency:")
    
    today = 0
    tomorrow = 0
    two_days = 0
    three_plus = 0
    
    for product in emergency_products:
        if product.days_until_expiry == 0:
            today += 1
        elif product.days_until_expiry == 1:
            tomorrow += 1
        elif product.days_until_expiry == 2:
            two_days += 1
        else:
            three_plus += 1
    
    print(f"  - Expiring TODAY: {today}")
    print(f"  - Expiring TOMORROW: {tomorrow}")
    print(f"  - 2 days left: {two_days}")
    print(f"  - 3+ days left: {three_plus}")
    
    # Financial summary
    total_original = sum((p.original_price_backup or p.price) * p.quantity for p in emergency_products)
    total_emergency = sum(p.price * p.quantity for p in emergency_products)
    total_discount = total_original - total_emergency
    
    print(f"\nFinancial Impact:")
    print(f"  - Original value: ₹{total_original:,.2f}")
    print(f"  - Emergency value: ₹{total_emergency:,.2f}")
    print(f"  - Total discount: ₹{total_discount:,.2f}")
    print(f"  - Average discount: {(total_discount/total_original*100):.1f}%")
    
    # Waste prevention estimate
    waste_prevented = sum(p.quantity * 0.5 for p in emergency_products)
    print(f"\nWaste Prevention:")
    print(f"  - Estimated waste prevented: {waste_prevented:.2f} kg")
    print(f"  - Equivalent to: {waste_prevented/1000:.2f} tonnes")


def main():
    """Main execution"""
    
    app = create_app()
    
    with app.app_context():
        # Create database tables
        db.create_all()
        print("✓ Database tables verified")
        
        # Create sample emergency products
        created = create_sample_emergency_products()
        
        # Run auto-flag
        auto_result = run_auto_flag()
        
        # Calculate metrics
        metrics = calculate_initial_metrics()
        
        # Display summary
        display_summary()
        
        print("\n" + "="*60)
        print("Emergency Marketplace Initialization Complete!")
        print("="*60)
        print("\n🔥 NEXT STEPS:")
        print("\n1. Login as Vendor:")
        print("   - Email: vendor1@freshconnect.com")
        print("   - Password: vendor123")
        print("   - Go to: Emergency Sales Dashboard")
        print("   - See your emergency products and mark more")
        
        print("\n2. Login as Retailer:")
        print("   - Email: retailer1@freshconnect.com")
        print("   - Password: retailer123")
        print("   - Go to: Emergency Deals (red HOT badge in navbar)")
        print("   - Browse discounted products and save money!")
        
        print("\n3. Login as Admin:")
        print("   - Email: admin@freshconnect.com")
        print("   - Password: admin123")
        print("   - Go to: Emergency Analytics")
        print("   - See waste reduction metrics and impact")
        
        print("\n📊 URLs:")
        print("   - Vendor: http://localhost:5000/emergency/vendor/dashboard")
        print("   - Retailer: http://localhost:5000/emergency/marketplace")
        print("   - Admin: http://localhost:5000/emergency/admin/analytics")
        
        print("\n" + "="*60)


if __name__ == '__main__':
    main()
