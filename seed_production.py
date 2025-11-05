"""Quick seed script for Railway production database"""
import os
os.environ['FLASK_ENV'] = 'production'

from app import create_app, db
from app.models import User, Product, Category
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app('production')

with app.app_context():
    try:
        # Create sample vendor if doesn't exist
        vendor = User.query.filter_by(email='vendor@test.com').first()
        if not vendor:
            vendor = User(
                name='Sample Vendor',
                email='vendor@test.com',
                password_hash=generate_password_hash('password123'),
                user_type='vendor',
                phone='9876543210',
                address='Koyambedu Market',
                city='Chennai'
            )
            db.session.add(vendor)
            db.session.commit()
            print("✅ Created sample vendor")
        
        # Create sample products
        products_data = [
            {'name': 'Tomatoes', 'category': 'vegetable', 'price': 40, 'stock': 100, 'moq': 5},
            {'name': 'Onions', 'category': 'vegetable', 'price': 30, 'stock': 150, 'moq': 10},
            {'name': 'Potatoes', 'category': 'vegetable', 'price': 25, 'stock': 200, 'moq': 10},
            {'name': 'Carrots', 'category': 'vegetable', 'price': 35, 'stock': 80, 'moq': 5},
            {'name': 'Apples', 'category': 'fruit', 'price': 120, 'stock': 60, 'moq': 5},
            {'name': 'Bananas', 'category': 'fruit', 'price': 60, 'stock': 100, 'moq': 12},
            {'name': 'Oranges', 'category': 'fruit', 'price': 80, 'stock': 70, 'moq': 6},
            {'name': 'Rice', 'category': 'grain', 'price': 50, 'stock': 500, 'moq': 25},
        ]
        
        for data in products_data:
            existing = Product.query.filter_by(name=data['name'], vendor_id=vendor.id).first()
            if not existing:
                product = Product(
                    name=data['name'],
                    description=f'Fresh {data["name"]} from Koyambedu',
                    category=data['category'],
                    price=data['price'],
                    stock_quantity=data['stock'],
                    moq=data['moq'],
                    unit='kg',
                    vendor_id=vendor.id,
                    created_at=datetime.utcnow()
                )
                db.session.add(product)
        
        db.session.commit()
        print("✅ Sample products added!")
        print(f"Total products: {Product.query.count()}")
        print(f"Total users: {User.query.count()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.session.rollback()
