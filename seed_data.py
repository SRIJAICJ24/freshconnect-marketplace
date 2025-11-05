from app import create_app, db
from app.models import User, Product, Driver, RetailerCredit
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from dotenv import load_dotenv

def seed_database():
    """
    Seed the database with sample data
    Creates test users, products, and drivers
    """
    load_dotenv()
    
    app = create_app()
    with app.app_context():
        print("Seeding database...")
        
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create Admin
        print("Creating admin user...")
        admin = User(
            name='Admin',
            email='admin@freshconnect.com',
            user_type='admin',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create Vendors
        print("Creating vendors...")
        vendors = []
        for i in range(3):
            vendor = User(
                name=f'Vendor {i+1}',
                email=f'vendor{i+1}@freshconnect.com',
                user_type='vendor',
                business_name=f'Fresh Shop {i+1}',
                phone=f'9876543{i}10',
                address=f'Koyambedu Market, Shop {i+1}',
                city='Chennai',
                is_active=True
            )
            vendor.set_password('vendor123')
            db.session.add(vendor)
            vendors.append(vendor)
        
        # Create Retailers
        print("Creating retailers...")
        retailers = []
        for i in range(5):
            retailer = User(
                name=f'Retailer {i+1}',
                email=f'retailer{i+1}@freshconnect.com',
                user_type='retailer',
                business_name=f'Retail Store {i+1}',
                phone=f'9876543{i}20',
                address=f'T Nagar, Store {i+1}',
                city='Chennai',
                is_active=True
            )
            retailer.set_password('retailer123')
            db.session.add(retailer)
            retailers.append(retailer)
        
        # Create Drivers
        print("Creating drivers...")
        driver_users = []
        for i in range(3):
            driver_user = User(
                name=f'Driver {i+1}',
                email=f'driver{i+1}@freshconnect.com',
                user_type='driver',
                phone=f'9876543{i}30',
                address=f'Koyambedu Parking Area {i+1}',
                city='Chennai',
                is_active=True
            )
            driver_user.set_password('driver123')
            db.session.add(driver_user)
            driver_users.append(driver_user)
        
        db.session.flush()
        
        # Create Driver profiles
        print("Creating driver profiles...")
        vehicle_types = ['van', 'truck', 'auto']
        for i, driver_user in enumerate(driver_users):
            driver = Driver(
                user_id=driver_user.id,
                vehicle_type=vehicle_types[i],
                vehicle_capacity_kg=100 * (i + 1),
                vehicle_registration=f'TN01AB{1000+i}',
                parking_location='Koyambedu Market',
                status='available'
            )
            db.session.add(driver)
        
        # Create Products
        print("Creating products...")
        products_data = [
            ('Fresh Tomato', 'Vegetables', 25, 500, 'kg', 7),
            ('Red Onion', 'Vegetables', 45, 800, 'kg', 14),
            ('Carrot', 'Vegetables', 30, 300, 'kg', 7),
            ('Fresh Rose', 'Flowers', 200, 100, 'bunch', 3),
            ('Jasmine', 'Flowers', 150, 50, 'bunch', 2),
            ('Fresh Banana', 'Fruits', 40, 200, 'dozen', 5),
            ('Fresh Mango', 'Fruits', 80, 150, 'kg', 7),
            ('Fresh Potato', 'Vegetables', 20, 600, 'kg', 21),
            ('Fresh Cauliflower', 'Vegetables', 35, 200, 'kg', 7),
            ('Fresh Spinach', 'Vegetables', 15, 100, 'kg', 3),
            ('Marigold', 'Flowers', 100, 80, 'bunch', 2),
            ('Fresh Apple', 'Fruits', 120, 100, 'kg', 10),
        ]
        
        for idx, (name, category, price, qty, unit, expiry_days) in enumerate(products_data):
            vendor = vendors[idx % len(vendors)]
            product = Product(
                vendor_id=vendor.id,
                product_name=name,
                category=category,
                price=price,
                quantity=qty,
                unit=unit,
                expiry_date=datetime.now().date() + timedelta(days=expiry_days),
                moq_enabled=True if category == 'Vegetables' else False,
                moq_type='quantity',
                minimum_quantity=50 if category == 'Vegetables' else 20,
                description=f'Fresh {name} directly from farm',
                is_active=True
            )
            db.session.add(product)
        
        # Create Retailer Credits
        print("Creating retailer credits...")
        for retailer in retailers:
            credit = RetailerCredit(
                retailer_id=retailer.id,
                credit_score=150,
                credit_tier='bronze',
                total_orders=0,
                successful_orders=0
            )
            db.session.add(credit)
        
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ Database seeded successfully!")
        print("="*60)
        print("\n📋 TEST CREDENTIALS:\n")
        print("Admin:")
        print("  Email: admin@freshconnect.com")
        print("  Password: admin123\n")
        print("Vendor:")
        print("  Email: vendor1@freshconnect.com")
        print("  Password: vendor123\n")
        print("Retailer:")
        print("  Email: retailer1@freshconnect.com")
        print("  Password: retailer123\n")
        print("Driver:")
        print("  Email: driver1@freshconnect.com")
        print("  Password: driver123\n")
        print("="*60)
        print("\n🚀 Run the app: python run.py")
        print("🌐 Open: http://localhost:5000")
        print("="*60 + "\n")

if __name__ == '__main__':
    seed_database()
