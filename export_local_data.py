"""Export local database data to JSON for Railway import"""
import json
from app import create_app, db
from app.models import User, Product
from datetime import datetime

app = create_app()

with app.app_context():
    # Export Users
    users = User.query.all()
    users_data = []
    for u in users:
        users_data.append({
            'name': u.name,
            'email': u.email,
            'user_type': u.user_type,
            'phone': u.phone,
            'address': u.address,
            'city': u.city,
            'business_name': u.business_name
        })
    
    # Export Products
    products = Product.query.all()
    products_data = []
    for p in products:
        products_data.append({
            'product_name': p.product_name,
            'description': p.description,
            'category': p.category,
            'price': p.price,
            'quantity': p.quantity,
            'unit': p.unit,
            'moq': p.moq if hasattr(p, 'moq') else None,
            'vendor_email': p.vendor.email  # We'll link by email
        })
    
    # Save to JSON file
    export_data = {
        'users': users_data,
        'products': products_data,
        'export_date': datetime.now().isoformat()
    }
    
    with open('local_data_export.json', 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"✅ Exported {len(users_data)} users and {len(products_data)} products")
    print(f"📄 Saved to: local_data_export.json")
    print(f"\n📊 Summary:")
    print(f"  Users: {len(users_data)}")
    print(f"  Products: {len(products_data)}")
    print(f"\n🔑 Sample Login Credentials:")
    for u in users[:5]:
        print(f"  {u.user_type}: {u.email} (password: password123)")
