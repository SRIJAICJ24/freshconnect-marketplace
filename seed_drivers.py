"""
Comprehensive Driver Seed Data
Creates drivers with different vehicle types (Bike, Tempo, Mini Truck, Truck)
Run with: python seed_drivers.py
"""

from app import create_app, db
from app.models import User, Driver
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

app = create_app()

# Driver data with different vehicle types
DRIVER_DATA = [
    # BIKE DRIVERS (Small capacity, quick delivery)
    {
        'name': 'Rajesh Kumar',
        'email': 'rajesh.bike@freshconnect.com',
        'phone': '9876543210',
        'vehicle_type': 'bike',
        'vehicle_registration': 'TN-01-AB-1234',
        'vehicle_capacity_kg': 25.0,
        'current_load_kg': 5.0,
        'rating': 4.8,
        'total_deliveries': 150,
        'status': 'available'
    },
    {
        'name': 'Arjun Singh',
        'email': 'arjun.bike@freshconnect.com',
        'phone': '9876543211',
        'vehicle_type': 'bike',
        'vehicle_registration': 'TN-02-CD-5678',
        'vehicle_capacity_kg': 20.0,
        'current_load_kg': 0.0,
        'rating': 4.9,
        'total_deliveries': 200,
        'status': 'available'
    },
    {
        'name': 'Karthik M',
        'email': 'karthik.bike@freshconnect.com',
        'phone': '9876543212',
        'vehicle_type': 'bike',
        'vehicle_registration': 'TN-03-EF-9012',
        'vehicle_capacity_kg': 30.0,
        'current_load_kg': 15.0,
        'rating': 4.7,
        'total_deliveries': 180,
        'status': 'on_delivery'
    },
    
    # TEMPO DRIVERS (Medium capacity, standard delivery)
    {
        'name': 'Murugan S',
        'email': 'murugan.tempo@freshconnect.com',
        'phone': '9876543220',
        'vehicle_type': 'tempo',
        'vehicle_registration': 'TN-04-GH-3456',
        'vehicle_capacity_kg': 500.0,
        'current_load_kg': 200.0,
        'rating': 4.6,
        'total_deliveries': 120,
        'status': 'available'
    },
    {
        'name': 'Ravi Chandran',
        'email': 'ravi.tempo@freshconnect.com',
        'phone': '9876543221',
        'vehicle_type': 'tempo',
        'vehicle_registration': 'TN-05-IJ-7890',
        'vehicle_capacity_kg': 600.0,
        'current_load_kg': 350.0,
        'rating': 4.8,
        'total_deliveries': 140,
        'status': 'on_delivery'
    },
    {
        'name': 'Senthil Kumar',
        'email': 'senthil.tempo@freshconnect.com',
        'phone': '9876543222',
        'vehicle_type': 'tempo',
        'vehicle_registration': 'TN-06-KL-2345',
        'vehicle_capacity_kg': 550.0,
        'current_load_kg': 100.0,
        'rating': 4.7,
        'total_deliveries': 130,
        'status': 'available'
    },
    {
        'name': 'Vinay Prakash',
        'email': 'vinay.tempo@freshconnect.com',
        'phone': '9876543223',
        'vehicle_type': 'tempo',
        'vehicle_registration': 'TN-07-MN-6789',
        'vehicle_capacity_kg': 500.0,
        'current_load_kg': 0.0,
        'rating': 4.9,
        'total_deliveries': 160,
        'status': 'available'
    },
    
    # MINI TRUCK DRIVERS (Good capacity, efficient)
    {
        'name': 'Kumar Selvam',
        'email': 'kumar.minitruck@freshconnect.com',
        'phone': '9876543230',
        'vehicle_type': 'mini_truck',
        'vehicle_registration': 'TN-08-OP-1234',
        'vehicle_capacity_kg': 1000.0,
        'current_load_kg': 450.0,
        'rating': 4.7,
        'total_deliveries': 90,
        'status': 'available'
    },
    {
        'name': 'Anand Raj',
        'email': 'anand.minitruck@freshconnect.com',
        'phone': '9876543231',
        'vehicle_type': 'mini_truck',
        'vehicle_registration': 'TN-09-QR-5678',
        'vehicle_capacity_kg': 1200.0,
        'current_load_kg': 600.0,
        'rating': 4.8,
        'total_deliveries': 100,
        'status': 'on_delivery'
    },
    {
        'name': 'Dinesh Babu',
        'email': 'dinesh.minitruck@freshconnect.com',
        'phone': '9876543232',
        'vehicle_type': 'mini_truck',
        'vehicle_registration': 'TN-10-ST-9012',
        'vehicle_capacity_kg': 1100.0,
        'current_load_kg': 200.0,
        'rating': 4.6,
        'total_deliveries': 85,
        'status': 'available'
    },
    
    # TRUCK DRIVERS (Large capacity, bulk delivery)
    {
        'name': 'Manikandan T',
        'email': 'mani.truck@freshconnect.com',
        'phone': '9876543240',
        'vehicle_type': 'truck',
        'vehicle_registration': 'TN-11-UV-3456',
        'vehicle_capacity_kg': 3000.0,
        'current_load_kg': 1500.0,
        'rating': 4.9,
        'total_deliveries': 75,
        'status': 'available'
    },
    {
        'name': 'Prakash Reddy',
        'email': 'prakash.truck@freshconnect.com',
        'phone': '9876543241',
        'vehicle_type': 'truck',
        'vehicle_registration': 'TN-12-WX-7890',
        'vehicle_capacity_kg': 3500.0,
        'current_load_kg': 2000.0,
        'rating': 4.8,
        'total_deliveries': 80,
        'status': 'on_delivery'
    },
    {
        'name': 'Suresh Babu',
        'email': 'suresh.truck@freshconnect.com',
        'phone': '9876543242',
        'vehicle_type': 'truck',
        'vehicle_registration': 'TN-13-YZ-2345',
        'vehicle_capacity_kg': 2800.0,
        'current_load_kg': 800.0,
        'rating': 4.7,
        'total_deliveries': 70,
        'status': 'available'
    },
    {
        'name': 'Venkatesh P',
        'email': 'venkat.truck@freshconnect.com',
        'phone': '9876543243',
        'vehicle_type': 'truck',
        'vehicle_registration': 'TN-14-AB-6789',
        'vehicle_capacity_kg': 3200.0,
        'current_load_kg': 0.0,
        'rating': 5.0,
        'total_deliveries': 95,
        'status': 'available'
    },
    {
        'name': 'Gokul Krishna',
        'email': 'gokul.truck@freshconnect.com',
        'phone': '9876543244',
        'vehicle_type': 'truck',
        'vehicle_registration': 'TN-15-CD-0123',
        'vehicle_capacity_kg': 3000.0,
        'current_load_kg': 500.0,
        'rating': 4.8,
        'total_deliveries': 88,
        'status': 'available'
    },
    
    # ADDITIONAL VARIED DRIVERS
    {
        'name': 'Balaji R',
        'email': 'balaji.bike@freshconnect.com',
        'phone': '9876543250',
        'vehicle_type': 'bike',
        'vehicle_registration': 'TN-16-EF-4567',
        'vehicle_capacity_kg': 25.0,
        'current_load_kg': 10.0,
        'rating': 4.6,
        'total_deliveries': 170,
        'status': 'available'
    },
    {
        'name': 'Ramesh Naidu',
        'email': 'ramesh.tempo@freshconnect.com',
        'phone': '9876543251',
        'vehicle_type': 'tempo',
        'vehicle_registration': 'TN-17-GH-8901',
        'vehicle_capacity_kg': 580.0,
        'current_load_kg': 300.0,
        'rating': 4.7,
        'total_deliveries': 125,
        'status': 'on_delivery'
    },
    {
        'name': 'Sathish Kumar',
        'email': 'sathish.minitruck@freshconnect.com',
        'phone': '9876543252',
        'vehicle_type': 'mini_truck',
        'vehicle_registration': 'TN-18-IJ-2345',
        'vehicle_capacity_kg': 1150.0,
        'current_load_kg': 400.0,
        'rating': 4.8,
        'total_deliveries': 92,
        'status': 'available'
    },
    {
        'name': 'Ganesh Moorthy',
        'email': 'ganesh.truck@freshconnect.com',
        'phone': '9876543253',
        'vehicle_type': 'truck',
        'vehicle_registration': 'TN-19-KL-6789',
        'vehicle_capacity_kg': 3100.0,
        'current_load_kg': 1200.0,
        'rating': 4.9,
        'total_deliveries': 82,
        'status': 'available'
    },
]

def seed_drivers():
    """Seed driver data into database"""
    with app.app_context():
        print("🚚 Starting Driver Seed Process...")
        print("=" * 60)
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for driver_data in DRIVER_DATA:
            try:
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
                        created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365))
                    )
                    db.session.add(user)
                    db.session.flush()  # Get user ID
                    
                    # Create driver profile
                    driver = Driver(
                        user_id=user.id,
                        vehicle_type=driver_data['vehicle_type'],
                        vehicle_registration=driver_data['vehicle_registration'],
                        vehicle_capacity_kg=driver_data['vehicle_capacity_kg'],
                        current_load_kg=driver_data['current_load_kg'],
                        status=driver_data['status'],
                        rating=driver_data['rating'],
                        total_deliveries=driver_data['total_deliveries']
                    )
                    db.session.add(driver)
                    
                    created_count += 1
                    print(f"✅ Created: {driver_data['name']} ({driver_data['vehicle_type']})")
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
                        print(f"🔄 Updated: {driver_data['name']} ({driver_data['vehicle_type']})")
                    else:
                        skipped_count += 1
                        print(f"⚠️  Skipped: {driver_data['name']} (User exists but no driver profile)")
                
            except Exception as e:
                print(f"❌ Error with {driver_data['name']}: {str(e)}")
                db.session.rollback()
                continue
        
        try:
            db.session.commit()
            print("\n" + "=" * 60)
            print("✅ DRIVER SEED COMPLETED!")
            print(f"📊 Summary:")
            print(f"   Created: {created_count} drivers")
            print(f"   Updated: {updated_count} drivers")
            print(f"   Skipped: {skipped_count} drivers")
            print(f"   Total: {created_count + updated_count} drivers in database")
            print("\n📋 Driver Types Breakdown:")
            
            # Count by vehicle type
            bike_count = len([d for d in DRIVER_DATA if d['vehicle_type'] == 'bike'])
            tempo_count = len([d for d in DRIVER_DATA if d['vehicle_type'] == 'tempo'])
            mini_truck_count = len([d for d in DRIVER_DATA if d['vehicle_type'] == 'mini_truck'])
            truck_count = len([d for d in DRIVER_DATA if d['vehicle_type'] == 'truck'])
            
            print(f"   🏍️  Bike: {bike_count} drivers (20-30 kg capacity)")
            print(f"   🚚 Tempo: {tempo_count} drivers (500-600 kg capacity)")
            print(f"   🚙 Mini Truck: {mini_truck_count} drivers (1000-1200 kg capacity)")
            print(f"   🚛 Truck: {truck_count} drivers (2800-3500 kg capacity)")
            
            print("\n🔑 Login Credentials:")
            print("   Email: [any_driver_email]@freshconnect.com")
            print("   Password: driver123")
            print("\n✨ All drivers are now available in the system!")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Failed to commit: {str(e)}")
            raise

if __name__ == '__main__':
    seed_drivers()
