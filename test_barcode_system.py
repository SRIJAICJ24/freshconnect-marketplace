"""
Test and Troubleshoot Barcode System
Run this to check if everything is working and create test data
"""

from app import create_app, db
from app.models import AdminGeneratedStock, Product, User
from datetime import datetime, timedelta

app = create_app()

def test_barcode_system():
    with app.app_context():
        print("=" * 60)
        print("  BARCODE SYSTEM DIAGNOSTIC")
        print("=" * 60)
        print()
        
        # 1. Check if admin user exists
        print("[1] Checking Admin User...")
        admin = User.query.filter_by(email='admin@freshconnect.com').first()
        if admin:
            print(f"   [OK] Admin exists: {admin.name} (ID: {admin.id})")
        else:
            print("   [WARN] Admin not found! Creating admin...")
            admin = User(
                name='Admin',
                email='admin@freshconnect.com',
                password='admin123',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print(f"   [OK] Admin created (ID: {admin.id})")
        
        # 2. Check if vendor user exists
        print("\n[2] Checking Vendor User...")
        vendor = User.query.filter_by(email='vendor1@freshconnect.com').first()
        if vendor:
            print(f"   [OK] Vendor exists: {vendor.name} (ID: {vendor.id})")
        else:
            print("   [WARN] Vendor not found! Please create vendor account")
        
        # 3. Check existing stocks
        print("\n[3] Checking Existing Stocks...")
        total_stocks = AdminGeneratedStock.query.count()
        unclaimed = AdminGeneratedStock.query.filter_by(is_claimed_by_vendor=False).count()
        claimed = AdminGeneratedStock.query.filter_by(is_claimed_by_vendor=True).count()
        
        print(f"   Total Stocks: {total_stocks}")
        print(f"   Unclaimed: {unclaimed}")
        print(f"   Claimed: {claimed}")
        
        # 4. Create test stocks if none exist
        if unclaimed == 0:
            print("\n[4] Creating Test Stocks...")
            test_products = [
                {"name": "Fresh Tomatoes", "category": "Vegetables", "weight": 50, "unit": "kg", "price": 30},
                {"name": "Fresh Onions", "category": "Vegetables", "weight": 40, "unit": "kg", "price": 25},
                {"name": "Fresh Potatoes", "category": "Vegetables", "weight": 100, "unit": "kg", "price": 20},
            ]
            
            created_codes = []
            for i, product in enumerate(test_products, 1):
                barcode = f"FC20251104{str(i).zfill(3)}"
                
                # Check if exists
                existing = AdminGeneratedStock.query.filter_by(admin_generated_code=barcode).first()
                if existing:
                    print(f"   - {barcode} already exists")
                    continue
                
                stock = AdminGeneratedStock(
                    admin_generated_code=barcode,
                    product_name=product["name"],
                    category=product["category"],
                    weight=product["weight"],
                    unit=product["unit"],
                    price=product["price"],
                    expiry_date=datetime.now().date() + timedelta(days=7),
                    created_by_admin_id=admin.id,
                    is_claimed_by_vendor=False
                )
                
                db.session.add(stock)
                created_codes.append(barcode)
                print(f"   [OK] Created: {barcode} - {product['name']}")
            
            db.session.commit()
            print(f"\n   Created {len(created_codes)} test stocks")
        else:
            print(f"\n[4] Test stocks already exist ({unclaimed} available)")
        
        # 5. List available barcodes
        print("\n[5] Available Barcodes for Testing:")
        print("-" * 60)
        available = AdminGeneratedStock.query.filter_by(is_claimed_by_vendor=False).limit(10).all()
        
        if available:
            for stock in available:
                print(f"   Barcode: {stock.admin_generated_code}")
                print(f"   Product: {stock.product_name}")
                print(f"   Quantity: {stock.weight} {stock.unit}")
                print(f"   Price: Rs.{stock.price}")
                print("-" * 60)
        else:
            print("   No available stocks! Create some first.")
        
        # 6. Check vendor's products
        if vendor:
            print("\n[6] Vendor's Current Products:")
            vendor_products = Product.query.filter_by(vendor_id=vendor.id).all()
            print(f"   Total Products: {len(vendor_products)}")
            for p in vendor_products[:5]:
                print(f"   - {p.product_name} ({p.quantity} {p.unit}) - Rs.{p.price}")
        
        # 7. Test URLs
        print("\n[7] Important URLs:")
        print(f"   Admin Create: http://127.0.0.1:5000/admin/inventory/create")
        print(f"   Admin View: http://127.0.0.1:5000/admin/inventory/stocks")
        print(f"   Vendor Scan: http://127.0.0.1:5000/vendor/barcode/scan")
        
        # 8. Summary
        print("\n" + "=" * 60)
        print("  SUMMARY")
        print("=" * 60)
        print(f"  Admin User: {'[OK]' if admin else '[WARN]'}")
        print(f"  Vendor User: {'[OK]' if vendor else '[WARN]'}")
        print(f"  Available Stocks: {unclaimed}")
        print(f"  Claimed Stocks: {claimed}")
        print("=" * 60)
        
        if unclaimed > 0 and vendor:
            print("\n[SUCCESS] SYSTEM READY!")
            print("\nQUICK TEST:")
            print("1. Login as vendor: vendor1@freshconnect.com / vendor123")
            print("2. Go to: /vendor/barcode/scan")
            print(f"3. Copy any barcode from above (e.g., {available[0].admin_generated_code})")
            print("4. Click 'Add to Inventory'")
            print("5. Confirm in popup")
            print("6. Check /vendor/products")
        else:
            print("\n[WARN] SETUP NEEDED:")
            if unclaimed == 0:
                print("- Create stocks as admin")
            if not vendor:
                print("- Create vendor account")
        
        print()

if __name__ == "__main__":
    test_barcode_system()
