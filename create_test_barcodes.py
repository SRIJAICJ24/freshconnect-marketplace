"""
Create Test Barcodes for Vendors
Run this to generate 10 pre-built barcodes for testing
"""

from app import create_app, db
from app.models import AdminGeneratedStock
from datetime import datetime, timedelta

app = create_app()

# Test products
test_products = [
    {"name": "Fresh Tomatoes", "category": "Vegetables", "weight": 50, "unit": "kg", "price": 30},
    {"name": "Fresh Onions", "category": "Vegetables", "weight": 40, "unit": "kg", "price": 25},
    {"name": "Fresh Potatoes", "category": "Vegetables", "weight": 100, "unit": "kg", "price": 20},
    {"name": "Fresh Apples", "category": "Fruits", "weight": 30, "unit": "kg", "price": 80},
    {"name": "Fresh Bananas", "category": "Fruits", "weight": 50, "unit": "dozen", "price": 40},
    {"name": "Fresh Carrots", "category": "Vegetables", "weight": 25, "unit": "kg", "price": 35},
    {"name": "Fresh Mangoes", "category": "Fruits", "weight": 20, "unit": "kg", "price": 100},
    {"name": "Fresh Spinach", "category": "Vegetables", "weight": 15, "unit": "kg", "price": 40},
    {"name": "Fresh Grapes", "category": "Fruits", "weight": 10, "unit": "kg", "price": 120},
    {"name": "Fresh Cauliflower", "category": "Vegetables", "weight": 30, "unit": "kg", "price": 45},
]

with app.app_context():
    print("=" * 60)
    print("  Creating Test Barcodes for FreshConnect")
    print("=" * 60)
    print()
    
    created_barcodes = []
    
    for i, product in enumerate(test_products, 1):
        # Generate barcode
        barcode = f"FC20251104{str(i).zfill(3)}"
        
        # Check if already exists
        existing = AdminGeneratedStock.query.filter_by(admin_generated_code=barcode).first()
        if existing:
            print(f"[SKIP] Barcode {barcode} already exists")
            continue
        
        # Create stock
        stock = AdminGeneratedStock(
            admin_generated_code=barcode,
            product_name=product["name"],
            category=product["category"],
            weight=product["weight"],
            unit=product["unit"],
            price=product["price"],
            expiry_date=datetime.now().date() + timedelta(days=7),
            created_by_admin_id=1,  # Assuming admin user ID is 1
            is_claimed_by_vendor=False
        )
        
        db.session.add(stock)
        created_barcodes.append({
            'barcode': barcode,
            'product': product["name"],
            'quantity': f"{product['weight']} {product['unit']}",
            'price': product["price"]
        })
        
        print(f"[OK] Created: {barcode} - {product['name']}")
    
    db.session.commit()
    
    print()
    print("=" * 60)
    print(f"  ✅ Successfully created {len(created_barcodes)} barcodes!")
    print("=" * 60)
    print()
    
    if created_barcodes:
        print("📋 BARCODES FOR VENDORS TO SCAN:")
        print()
        print("-" * 60)
        for item in created_barcodes:
            print(f"Barcode: {item['barcode']}")
            print(f"Product: {item['product']}")
            print(f"Quantity: {item['quantity']}")
            print(f"Price: ₹{item['price']}")
            print("-" * 60)
        
        print()
        print("🎯 HOW TO USE:")
        print("1. Login as vendor: vendor1@freshconnect.com / vendor123")
        print("2. Go to: Vendor Dashboard → Scan Barcode")
        print("3. Enter any barcode from above (e.g., FC20251104001)")
        print("4. Click 'Claim Stock'")
        print("5. Product will be added to your inventory!")
        print()
        print("📊 VIEW IN ADMIN:")
        print("1. Login as admin: admin@freshconnect.com / admin123")
        print("2. Go to: Admin Dashboard → Inventory Management")
        print("3. See all barcodes and their status")
        print()
    else:
        print("ℹ️  All barcodes already exist. No new barcodes created.")
    
    print("=" * 60)
