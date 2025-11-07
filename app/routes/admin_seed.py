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


@bp.route('/seed-comprehensive-drivers')
def seed_comprehensive_drivers():
    """Seed 20 comprehensive drivers with all vehicle types"""
    try:
        # Comprehensive driver data
        DRIVER_DATA = [
            # BIKE DRIVERS (Small capacity, quick delivery)
            {'name': 'Rajesh Kumar', 'email': 'rajesh.bike@freshconnect.com', 'phone': '9876543210', 'vehicle_type': 'bike', 'vehicle_registration': 'TN-01-AB-1234', 'vehicle_capacity_kg': 25.0, 'current_load_kg': 5.0, 'rating': 4.8, 'total_deliveries': 150, 'status': 'available'},
            {'name': 'Arjun Singh', 'email': 'arjun.bike@freshconnect.com', 'phone': '9876543211', 'vehicle_type': 'bike', 'vehicle_registration': 'TN-02-CD-5678', 'vehicle_capacity_kg': 20.0, 'current_load_kg': 0.0, 'rating': 4.9, 'total_deliveries': 200, 'status': 'available'},
            {'name': 'Karthik M', 'email': 'karthik.bike@freshconnect.com', 'phone': '9876543212', 'vehicle_type': 'bike', 'vehicle_registration': 'TN-03-EF-9012', 'vehicle_capacity_kg': 30.0, 'current_load_kg': 15.0, 'rating': 4.7, 'total_deliveries': 180, 'status': 'on_delivery'},
            {'name': 'Balaji R', 'email': 'balaji.bike@freshconnect.com', 'phone': '9876543250', 'vehicle_type': 'bike', 'vehicle_registration': 'TN-16-EF-4567', 'vehicle_capacity_kg': 25.0, 'current_load_kg': 10.0, 'rating': 4.6, 'total_deliveries': 170, 'status': 'available'},
            
            # TEMPO DRIVERS (Medium capacity, standard delivery)
            {'name': 'Murugan S', 'email': 'murugan.tempo@freshconnect.com', 'phone': '9876543220', 'vehicle_type': 'tempo', 'vehicle_registration': 'TN-04-GH-3456', 'vehicle_capacity_kg': 500.0, 'current_load_kg': 200.0, 'rating': 4.6, 'total_deliveries': 120, 'status': 'available'},
            {'name': 'Ravi Chandran', 'email': 'ravi.tempo@freshconnect.com', 'phone': '9876543221', 'vehicle_type': 'tempo', 'vehicle_registration': 'TN-05-IJ-7890', 'vehicle_capacity_kg': 600.0, 'current_load_kg': 350.0, 'rating': 4.8, 'total_deliveries': 140, 'status': 'on_delivery'},
            {'name': 'Senthil Kumar', 'email': 'senthil.tempo@freshconnect.com', 'phone': '9876543222', 'vehicle_type': 'tempo', 'vehicle_registration': 'TN-06-KL-2345', 'vehicle_capacity_kg': 550.0, 'current_load_kg': 100.0, 'rating': 4.7, 'total_deliveries': 130, 'status': 'available'},
            {'name': 'Vinay Prakash', 'email': 'vinay.tempo@freshconnect.com', 'phone': '9876543223', 'vehicle_type': 'tempo', 'vehicle_registration': 'TN-07-MN-6789', 'vehicle_capacity_kg': 500.0, 'current_load_kg': 0.0, 'rating': 4.9, 'total_deliveries': 160, 'status': 'available'},
            {'name': 'Ramesh Naidu', 'email': 'ramesh.tempo@freshconnect.com', 'phone': '9876543251', 'vehicle_type': 'tempo', 'vehicle_registration': 'TN-17-GH-8901', 'vehicle_capacity_kg': 580.0, 'current_load_kg': 300.0, 'rating': 4.7, 'total_deliveries': 125, 'status': 'on_delivery'},
            
            # MINI TRUCK DRIVERS (Good capacity, efficient)
            {'name': 'Kumar Selvam', 'email': 'kumar.minitruck@freshconnect.com', 'phone': '9876543230', 'vehicle_type': 'mini_truck', 'vehicle_registration': 'TN-08-OP-1234', 'vehicle_capacity_kg': 1000.0, 'current_load_kg': 450.0, 'rating': 4.7, 'total_deliveries': 90, 'status': 'available'},
            {'name': 'Anand Raj', 'email': 'anand.minitruck@freshconnect.com', 'phone': '9876543231', 'vehicle_type': 'mini_truck', 'vehicle_registration': 'TN-09-QR-5678', 'vehicle_capacity_kg': 1200.0, 'current_load_kg': 600.0, 'rating': 4.8, 'total_deliveries': 100, 'status': 'on_delivery'},
            {'name': 'Dinesh Babu', 'email': 'dinesh.minitruck@freshconnect.com', 'phone': '9876543232', 'vehicle_type': 'mini_truck', 'vehicle_registration': 'TN-10-ST-9012', 'vehicle_capacity_kg': 1100.0, 'current_load_kg': 200.0, 'rating': 4.6, 'total_deliveries': 85, 'status': 'available'},
            {'name': 'Sathish Kumar', 'email': 'sathish.minitruck@freshconnect.com', 'phone': '9876543252', 'vehicle_type': 'mini_truck', 'vehicle_registration': 'TN-18-IJ-2345', 'vehicle_capacity_kg': 1150.0, 'current_load_kg': 400.0, 'rating': 4.8, 'total_deliveries': 92, 'status': 'available'},
            
            # TRUCK DRIVERS (Large capacity, bulk delivery)
            {'name': 'Manikandan T', 'email': 'mani.truck@freshconnect.com', 'phone': '9876543240', 'vehicle_type': 'truck', 'vehicle_registration': 'TN-11-UV-3456', 'vehicle_capacity_kg': 3000.0, 'current_load_kg': 1500.0, 'rating': 4.9, 'total_deliveries': 75, 'status': 'available'},
            {'name': 'Prakash Reddy', 'email': 'prakash.truck@freshconnect.com', 'phone': '9876543241', 'vehicle_type': 'truck', 'vehicle_registration': 'TN-12-WX-7890', 'vehicle_capacity_kg': 3500.0, 'current_load_kg': 2000.0, 'rating': 4.8, 'total_deliveries': 80, 'status': 'on_delivery'},
            {'name': 'Suresh Babu', 'email': 'suresh.truck@freshconnect.com', 'phone': '9876543242', 'vehicle_type': 'truck', 'vehicle_registration': 'TN-13-YZ-2345', 'vehicle_capacity_kg': 2800.0, 'current_load_kg': 800.0, 'rating': 4.7, 'total_deliveries': 70, 'status': 'available'},
            {'name': 'Venkatesh P', 'email': 'venkat.truck@freshconnect.com', 'phone': '9876543243', 'vehicle_type': 'truck', 'vehicle_registration': 'TN-14-AB-6789', 'vehicle_capacity_kg': 3200.0, 'current_load_kg': 0.0, 'rating': 5.0, 'total_deliveries': 95, 'status': 'available'},
            {'name': 'Gokul Krishna', 'email': 'gokul.truck@freshconnect.com', 'phone': '9876543244', 'vehicle_type': 'truck', 'vehicle_registration': 'TN-15-CD-0123', 'vehicle_capacity_kg': 3000.0, 'current_load_kg': 500.0, 'rating': 4.8, 'total_deliveries': 88, 'status': 'available'},
            {'name': 'Ganesh Moorthy', 'email': 'ganesh.truck@freshconnect.com', 'phone': '9876543253', 'vehicle_type': 'truck', 'vehicle_registration': 'TN-19-KL-6789', 'vehicle_capacity_kg': 3100.0, 'current_load_kg': 1200.0, 'rating': 4.9, 'total_deliveries': 82, 'status': 'available'},
        ]
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for driver_data in DRIVER_DATA:
            # Check if user exists
            user = User.query.filter_by(email=driver_data['email']).first()
            
            if not user:
                # Create new user
                user = User(
                    name=driver_data['name'],
                    email=driver_data['email'],
                    phone=driver_data['phone'],
                    user_type='driver',
                    password_hash=generate_password_hash('driver123'),
                    is_verified=True,
                    address='Koyambedu Market, Chennai',
                    city='Chennai'
                )
                db.session.add(user)
                db.session.flush()
                
                # Create driver profile
                driver = Driver(
                    user_id=user.id,
                    vehicle_type=driver_data['vehicle_type'],
                    vehicle_registration=driver_data['vehicle_registration'],
                    vehicle_capacity_kg=driver_data['vehicle_capacity_kg'],
                    current_load_kg=driver_data['current_load_kg'],
                    status=driver_data['status'],
                    rating=driver_data['rating'],
                    total_deliveries=driver_data['total_deliveries'],
                    is_active=True
                )
                db.session.add(driver)
                created_count += 1
            else:
                # Update existing driver
                driver = Driver.query.filter_by(user_id=user.id).first()
                if driver:
                    driver.vehicle_type = driver_data['vehicle_type']
                    driver.vehicle_registration = driver_data['vehicle_registration']
                    driver.vehicle_capacity_kg = driver_data['vehicle_capacity_kg']
                    driver.current_load_kg = driver_data['current_load_kg']
                    driver.status = driver_data['status']
                    driver.rating = driver_data['rating']
                    driver.total_deliveries = driver_data['total_deliveries']
                    updated_count += 1
                else:
                    skipped_count += 1
        
        db.session.commit()
        
        # Count by vehicle type
        bike_count = len([d for d in DRIVER_DATA if d['vehicle_type'] == 'bike'])
        tempo_count = len([d for d in DRIVER_DATA if d['vehicle_type'] == 'tempo'])
        mini_truck_count = len([d for d in DRIVER_DATA if d['vehicle_type'] == 'mini_truck'])
        truck_count = len([d for d in DRIVER_DATA if d['vehicle_type'] == 'truck'])
        
        return jsonify({
            'status': 'success',
            'message': '20 Comprehensive Drivers Seeded Successfully!',
            'summary': {
                'created': created_count,
                'updated': updated_count,
                'skipped': skipped_count,
                'total': created_count + updated_count
            },
            'breakdown': {
                'bike_drivers': f'{bike_count} drivers (20-30 kg capacity)',
                'tempo_drivers': f'{tempo_count} drivers (500-600 kg capacity)',
                'mini_truck_drivers': f'{mini_truck_count} drivers (1000-1200 kg capacity)',
                'truck_drivers': f'{truck_count} drivers (2800-3500 kg capacity)'
            },
            'sample_logins': {
                'bike': 'rajesh.bike@freshconnect.com / driver123',
                'tempo': 'murugan.tempo@freshconnect.com / driver123',
                'mini_truck': 'kumar.minitruck@freshconnect.com / driver123',
                'truck': 'mani.truck@freshconnect.com / driver123'
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
