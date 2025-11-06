"""Admin route to seed complete database with all local data"""
from flask import Blueprint, jsonify
from app import db
from app.models import User, Product, Driver, RetailerCredit
from werkzeug.security import generate_password_hash
from datetime import datetime

bp = Blueprint('admin_seed', __name__, url_prefix='/admin-seed')

@bp.route('/full-import')
def full_import():
    """Import all users and products from local development data"""
    try:
        # Default password for all demo accounts
        DEFAULT_PASSWORD = 'password123'
        
        # Import Users
        users_to_create = [
            {'name': 'Admin', 'email': 'admin@freshconnect.com', 'user_type': 'admin', 'phone': '9999999999', 'city': 'Chennai'},
            {'name': 'Vendor 1', 'email': 'vendor1@freshconnect.com', 'user_type': 'vendor', 'phone': '9876543210', 'city': 'Chennai', 'business_name': 'Fresh Veggies Co'},
            {'name': 'Vendor 2', 'email': 'vendor2@freshconnect.com', 'user_type': 'vendor', 'phone': '9876543211', 'city': 'Chennai', 'business_name': 'Fruit Paradise'},
            {'name': 'Vendor 3', 'email': 'vendor3@freshconnect.com', 'user_type': 'vendor', 'phone': '9876543212', 'city': 'Chennai', 'business_name': 'Grain Masters'},
            {'name': 'Retailer 1', 'email': 'retailer1@freshconnect.com', 'user_type': 'retailer', 'phone': '9123456780', 'city': 'Chennai'},
            {'name': 'Retailer 2', 'email': 'retailer2@freshconnect.com', 'user_type': 'retailer', 'phone': '9123456781', 'city': 'Chennai'},
            {'name': 'Retailer 3', 'email': 'retailer3@freshconnect.com', 'user_type': 'retailer', 'phone': '9123456782', 'city': 'Chennai'},
            {'name': 'Retailer 4', 'email': 'retailer4@freshconnect.com', 'user_type': 'retailer', 'phone': '9123456783', 'city': 'Chennai'},
            {'name': 'Retailer 5', 'email': 'retailer5@freshconnect.com', 'user_type': 'retailer', 'phone': '9123456784', 'city': 'Chennai'},
            {'name': 'Driver 1', 'email': 'driver1@freshconnect.com', 'user_type': 'driver', 'phone': '9111111111', 'city': 'Chennai'},
            {'name': 'Driver 2', 'email': 'driver2@freshconnect.com', 'user_type': 'driver', 'phone': '9111111112', 'city': 'Chennai'},
            {'name': 'Driver 3', 'email': 'driver3@freshconnect.com', 'user_type': 'driver', 'phone': '9111111113', 'city': 'Chennai'},
        ]
        
        users_created = 0
        vendor_map = {}  # email -> user_id mapping
        
        for user_data in users_to_create:
            existing = User.query.filter_by(email=user_data['email']).first()
            if not existing:
                user = User(
                    name=user_data['name'],
                    email=user_data['email'],
                    password_hash=generate_password_hash(DEFAULT_PASSWORD),
                    user_type=user_data['user_type'],
                    phone=user_data.get('phone'),
                    address='Koyambedu Market',
                    city=user_data.get('city', 'Chennai'),
                    business_name=user_data.get('business_name')
                )
                db.session.add(user)
                db.session.flush()  # Get the ID
                users_created += 1
                
                # Create role-specific profiles
                if user_data['user_type'] == 'vendor':
                    vendor_map[user_data['email']] = user.id
                    
                elif user_data['user_type'] == 'retailer':
                    # Create retailer credit record
                    credit = RetailerCredit(
                        retailer_id=user.id,
                        credit_score=500,
                        tier='silver',
                        credit_limit=50000,
                        credit_available=50000,
                        credit_utilized=0
                    )
                    db.session.add(credit)
                    
                elif user_data['user_type'] == 'driver':
                    # Create driver profile
                    driver = Driver(
                        user_id=user.id,
                        vehicle_type='bike',
                        vehicle_registration=f'TN01AB{str(user.id).zfill(4)}',
                        status='available',
                        current_load_kg=0,
                        vehicle_capacity_kg=50,
                        total_deliveries=0,
                        rating=5.0,
                        is_active=True
                    )
                    db.session.add(driver)
            else:
                if existing.user_type == 'vendor':
                    vendor_map[user_data['email']] = existing.id
        
        db.session.commit()
        
        # Import Products (linked to vendors)
        products_to_create = [
            # Vendor 1 - Vegetables
            {'product_name': 'Tomatoes', 'category': 'vegetable', 'price': 40, 'quantity': 100, 'minimum_quantity': 5, 'vendor_email': 'vendor1@freshconnect.com'},
            {'product_name': 'Onions', 'category': 'vegetable', 'price': 30, 'quantity': 150, 'minimum_quantity': 10, 'vendor_email': 'vendor1@freshconnect.com'},
            {'product_name': 'Potatoes', 'category': 'vegetable', 'price': 25, 'quantity': 200, 'minimum_quantity': 10, 'vendor_email': 'vendor1@freshconnect.com'},
            {'product_name': 'Carrots', 'category': 'vegetable', 'price': 35, 'quantity': 80, 'minimum_quantity': 5, 'vendor_email': 'vendor1@freshconnect.com'},
            {'product_name': 'Cabbage', 'category': 'vegetable', 'price': 20, 'quantity': 60, 'minimum_quantity': 5, 'vendor_email': 'vendor1@freshconnect.com'},
            {'product_name': 'Cauliflower', 'category': 'vegetable', 'price': 45, 'quantity': 40, 'minimum_quantity': 5, 'vendor_email': 'vendor1@freshconnect.com'},
            {'product_name': 'Green Beans', 'category': 'vegetable', 'price': 60, 'quantity': 50, 'minimum_quantity': 3, 'vendor_email': 'vendor1@freshconnect.com'},
            
            # Vendor 2 - Fruits
            {'product_name': 'Apples', 'category': 'fruit', 'price': 120, 'quantity': 60, 'minimum_quantity': 5, 'vendor_email': 'vendor2@freshconnect.com'},
            {'product_name': 'Bananas', 'category': 'fruit', 'price': 60, 'quantity': 100, 'minimum_quantity': 12, 'vendor_email': 'vendor2@freshconnect.com'},
            {'product_name': 'Oranges', 'category': 'fruit', 'price': 80, 'quantity': 70, 'minimum_quantity': 6, 'vendor_email': 'vendor2@freshconnect.com'},
            {'product_name': 'Mangoes', 'category': 'fruit', 'price': 150, 'quantity': 50, 'minimum_quantity': 12, 'vendor_email': 'vendor2@freshconnect.com'},
            {'product_name': 'Grapes', 'category': 'fruit', 'price': 100, 'quantity': 40, 'minimum_quantity': 5, 'vendor_email': 'vendor2@freshconnect.com'},
            {'product_name': 'Watermelon', 'category': 'fruit', 'price': 30, 'quantity': 30, 'minimum_quantity': 1, 'vendor_email': 'vendor2@freshconnect.com'},
            
            # Vendor 3 - Grains
            {'product_name': 'Rice', 'category': 'grain', 'price': 50, 'quantity': 500, 'minimum_quantity': 25, 'vendor_email': 'vendor3@freshconnect.com'},
            {'product_name': 'Wheat', 'category': 'grain', 'price': 45, 'quantity': 400, 'minimum_quantity': 25, 'vendor_email': 'vendor3@freshconnect.com'},
            {'product_name': 'Lentils (Dal)', 'category': 'grain', 'price': 80, 'quantity': 200, 'minimum_quantity': 10, 'vendor_email': 'vendor3@freshconnect.com'},
            {'product_name': 'Chickpeas', 'category': 'grain', 'price': 90, 'quantity': 150, 'minimum_quantity': 10, 'vendor_email': 'vendor3@freshconnect.com'},
            {'product_name': 'Kidney Beans', 'category': 'grain', 'price': 100, 'quantity': 100, 'minimum_quantity': 5, 'vendor_email': 'vendor3@freshconnect.com'},
            
            # Additional items
            {'product_name': 'Spinach', 'category': 'vegetable', 'price': 25, 'quantity': 40, 'minimum_quantity': 2, 'vendor_email': 'vendor1@freshconnect.com'},
            {'product_name': 'Pineapple', 'category': 'fruit', 'price': 50, 'quantity': 25, 'minimum_quantity': 1, 'vendor_email': 'vendor2@freshconnect.com'},
            {'product_name': 'Corn', 'category': 'vegetable', 'price': 40, 'quantity': 80, 'minimum_quantity': 10, 'vendor_email': 'vendor1@freshconnect.com'},
            {'product_name': 'Papaya', 'category': 'fruit', 'price': 40, 'quantity': 30, 'minimum_quantity': 1, 'vendor_email': 'vendor2@freshconnect.com'},
        ]
        
        products_created = 0
        for prod_data in products_to_create:
            vendor_email = prod_data['vendor_email']
            if vendor_email not in vendor_map:
                continue  # Skip if vendor doesn't exist
                
            existing = Product.query.filter_by(
                product_name=prod_data['product_name'],
                vendor_id=vendor_map[vendor_email]
            ).first()
            
            if not existing:
                product = Product(
                    product_name=prod_data['product_name'],
                    description=f"Fresh {prod_data['product_name']} from Koyambedu Market",
                    category=prod_data['category'],
                    price=prod_data['price'],
                    quantity=prod_data['quantity'],
                    moq_enabled=True,
                    minimum_quantity=prod_data.get('minimum_quantity', 1),
                    unit='kg',
                    vendor_id=vendor_map[vendor_email],
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.session.add(product)
                products_created += 1
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Complete database imported!',
            'users_created': users_created,
            'products_created': products_created,
            'total_users': User.query.count(),
            'total_products': Product.query.count(),
            'login_info': {
                'admin': 'admin@freshconnect.com / password123',
                'vendor': 'vendor1@freshconnect.com / password123',
                'retailer': 'retailer1@freshconnect.com / password123',
                'driver': 'driver1@freshconnect.com / password123'
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
