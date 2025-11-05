"""
Quick script to check vendor's products after claiming barcode
"""

from app import create_app, db
from app.models import Product, User, AdminGeneratedStock

app = create_app()

def check_products():
    with app.app_context():
        print("=" * 60)
        print("  VENDOR PRODUCTS CHECK")
        print("=" * 60)
        print()
        
        # Get vendor
        vendor = User.query.filter_by(email='vendor1@freshconnect.com').first()
        if not vendor:
            print("[ERROR] Vendor not found!")
            return
        
        print(f"Vendor: {vendor.name} (ID: {vendor.id})")
        print()
        
        # Get all vendor's products
        products = Product.query.filter_by(vendor_id=vendor.id).order_by(Product.created_at.desc()).all()
        
        print(f"Total Products: {len(products)}")
        print("-" * 60)
        
        if products:
            print("\nALL PRODUCTS:")
            for i, p in enumerate(products, 1):
                print(f"\n{i}. {p.product_name}")
                print(f"   Category: {p.category}")
                print(f"   Quantity: {p.quantity} {p.unit}")
                print(f"   Price: Rs.{p.price}")
                print(f"   Active: {'Yes' if p.is_active else 'No'}")
                print(f"   Created: {p.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Check if this came from barcode
                stock = AdminGeneratedStock.query.filter_by(product_id=p.id).first()
                if stock:
                    print(f"   [BARCODE] From: {stock.admin_generated_code}")
        else:
            print("\n[WARN] No products found!")
        
        print("\n" + "=" * 60)
        
        # Check claimed stocks
        claimed = AdminGeneratedStock.query.filter_by(
            claimed_by_vendor_id=vendor.id,
            is_claimed_by_vendor=True
        ).all()
        
        print(f"\nClaimed Barcodes: {len(claimed)}")
        if claimed:
            for stock in claimed:
                print(f"  - {stock.admin_generated_code}: {stock.product_name}")
                print(f"    Product ID: {stock.product_id}")
                print(f"    Claimed at: {stock.claimed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n" + "=" * 60)
        print("\nTo view in browser:")
        print("1. Login: vendor1@freshconnect.com / vendor123")
        print("2. Go to: http://127.0.0.1:5000/vendor/products")
        print("3. You should see all products listed above")
        print()

if __name__ == "__main__":
    check_products()
