#!/usr/bin/env python3
"""
Check MOQ (Minimum Order Quantity) Product Settings
"""

from app import create_app, db
from app.models import Product

app = create_app()

with app.app_context():
    print("=" * 70)
    print("CHECKING MOQ PRODUCTS")
    print("=" * 70)
    
    # Find all products with MOQ enabled
    moq_products = Product.query.filter_by(moq_enabled=True).all()
    
    if not moq_products:
        print("\n❌ No MOQ products found in database!")
        print("\nCreating sample MOQ products...")
        
        # Create sample MOQ products
        samples = [
            {
                'product_name': 'Bulk Rice',
                'category': 'Grains',
                'price': 45.00,
                'unit': 'kg',
                'quantity': 1000,
                'moq_enabled': True,
                'moq_type': 'quantity',
                'minimum_quantity': 50,
                'vendor_id': 1
            },
            {
                'product_name': 'Wholesale Onions',
                'category': 'Vegetables',
                'price': 30.00,
                'unit': 'kg',
                'quantity': 500,
                'moq_enabled': True,
                'moq_type': 'quantity',
                'minimum_quantity': 100,
                'vendor_id': 1
            }
        ]
        
        for data in samples:
            product = Product(**data)
            db.session.add(product)
        
        db.session.commit()
        print("✅ Created 2 sample MOQ products!")
        
        # Re-fetch
        moq_products = Product.query.filter_by(moq_enabled=True).all()
    
    print(f"\n📦 Found {len(moq_products)} products with MOQ enabled:\n")
    
    for product in moq_products:
        print(f"{'='*70}")
        print(f"ID: {product.id}")
        print(f"Name: {product.product_name}")
        print(f"Category: {product.category}")
        print(f"Price: ₹{product.price}/{product.unit}")
        print(f"Stock: {product.quantity} {product.unit}")
        print(f"MOQ Enabled: {product.moq_enabled}")
        print(f"MOQ Type: {product.moq_type}")
        print(f"Minimum Quantity: {product.minimum_quantity} {product.unit}")
        print(f"Active: {product.is_active}")
        print()
        
        # Validation check
        if product.moq_enabled and product.moq_type == 'quantity':
            print(f"✅ MOQ Validation: Must order at least {product.minimum_quantity} {product.unit}")
            print(f"   Example: Adding 100 {product.unit} -> ", end="")
            if 100 >= product.minimum_quantity:
                print("✅ ALLOWED")
            else:
                print(f"❌ REJECTED (need {product.minimum_quantity})")
            
            print(f"   Example: Adding 10 {product.unit} -> ", end="")
            if 10 >= product.minimum_quantity:
                print("✅ ALLOWED")
            else:
                print(f"❌ REJECTED (need {product.minimum_quantity})")
    
    print("\n" + "="*70)
    print("TESTING ADD TO CART LOGIC")
    print("="*70)
    
    if moq_products:
        test_product = moq_products[0]
        print(f"\nTest Product: {test_product.product_name}")
        print(f"MOQ: {test_product.minimum_quantity} {test_product.unit}")
        
        test_quantities = [1, 10, 25, 50, 100, 200]
        
        for qty in test_quantities:
            # Simulate the validation logic
            quantity = int(qty)  # Convert to int like in the fix
            
            if test_product.moq_enabled and test_product.moq_type == 'quantity':
                if quantity < test_product.minimum_quantity:
                    status = f"❌ REJECTED - Min: {test_product.minimum_quantity}"
                else:
                    status = "✅ ALLOWED"
            else:
                status = "✅ ALLOWED (No MOQ)"
            
            print(f"  Quantity {qty:3d} -> {status}")
    
    print("\n" + "="*70)
    print("TEST COMMANDS")
    print("="*70)
    print("\nTest in browser console after fixing:")
    
    if moq_products:
        for product in moq_products[:2]:  # Show first 2
            print(f"\n// Test: {product.product_name} (MOQ: {product.minimum_quantity})")
            print(f"addToCart({product.id}, 10);  // Should FAIL - below MOQ")
            print(f"addToCart({product.id}, {product.minimum_quantity});  // Should PASS - exact MOQ")
            print(f"addToCart({product.id}, {product.minimum_quantity + 50});  // Should PASS - above MOQ")
    
    print("\n" + "="*70)
