"""
Initialize Advanced Features Data
Creates sample data for:
- Driver Routes (FEATURE 1)
- Sample Barcodes (FEATURE 2)
"""

from app import create_app, db
from app.models import Driver, DriverRoute, BarcodeTrack, Product, User
from datetime import datetime
import random

def init_driver_routes():
    """Create sample driver routes for location-based assignment"""
    
    print("Creating driver routes...")
    
    # Get all drivers
    drivers = Driver.query.all()
    
    if not drivers:
        print("No drivers found. Run seed_data.py first!")
        return
    
    # Sample routes from Koyambedu Market to various locations
    routes = [
        {
            'start': 'Koyambedu Market',
            'end': 'Chromepet',
            'start_lat': '13.0827',
            'start_lng': '80.2707',
            'end_lat': '12.9716',
            'end_lng': '80.2202',
            'distance_km': 25.0,
            'time_hours': 1.5
        },
        {
            'start': 'Koyambedu Market',
            'end': 'Velachery',
            'start_lat': '13.0827',
            'start_lng': '80.2707',
            'end_lat': '12.9689',
            'end_lng': '80.2350',
            'distance_km': 22.0,
            'time_hours': 1.2
        },
        {
            'start': 'Koyambedu Market',
            'end': 'Guindy',
            'start_lat': '13.0827',
            'start_lng': '80.2707',
            'end_lat': '13.0012',
            'end_lng': '80.2175',
            'distance_km': 10.0,
            'time_hours': 0.7
        },
        {
            'start': 'Koyambedu Market',
            'end': 'Adyar',
            'start_lat': '13.0827',
            'start_lng': '80.2707',
            'end_lat': '12.9971',
            'end_lng': '80.2421',
            'distance_km': 15.0,
            'time_hours': 1.0
        },
        {
            'start': 'Koyambedu Market',
            'end': 'Tambaram',
            'start_lat': '13.0827',
            'start_lng': '80.2707',
            'end_lat': '12.9250',
            'end_lng': '80.1450',
            'distance_km': 28.0,
            'time_hours': 1.8
        }
    ]
    
    # Assign routes to drivers
    for i, driver in enumerate(drivers):
        route_data = routes[i % len(routes)]  # Cycle through routes
        
        route = DriverRoute(
            driver_id=driver.id,
            starting_location=route_data['start'],
            ending_location=route_data['end'],
            start_lat=route_data['start_lat'],
            start_lng=route_data['start_lng'],
            end_lat=route_data['end_lat'],
            end_lng=route_data['end_lng'],
            total_distance_km=route_data['distance_km'],
            estimated_time_hours=route_data['time_hours'],
            status='available'
        )
        
        db.session.add(route)
        print(f"  Created route for {driver.user.name}: {route_data['start']} → {route_data['end']}")
    
    db.session.commit()
    print(f"✓ Created {len(drivers)} driver routes")


def create_sample_barcodes():
    """Create sample barcodes for demonstration"""
    
    print("\nCreating sample barcodes...")
    
    # Get users
    vendors = User.query.filter_by(user_type='vendor').all()
    retailers = User.query.filter_by(user_type='retailer').all()
    products = Product.query.limit(3).all()
    
    if not vendors or not retailers or not products:
        print("Insufficient data. Run seed_data.py first!")
        return
    
    # Create a few sample barcodes
    for i in range(3):
        barcode = BarcodeTrack(
            barcode_number=f'BC{random.randint(100000000000, 999999999999)}',
            product_id=products[i % len(products)].id,
            sender_id=vendors[0].id,
            receiver_id=retailers[0].id,
            status='in_transit',
            quantity=50.0 + (i * 10),
            unit='kg'
        )
        db.session.add(barcode)
        print(f"  Created barcode: {barcode.barcode_number} - {products[i % len(products)].product_name}")
    
    db.session.commit()
    print(f"✓ Created 3 sample barcodes")


def main():
    """Main initialization function"""
    
    print("="*60)
    print("Initializing Advanced Features Data")
    print("="*60)
    
    app = create_app()
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        print("✓ Database tables verified")
        
        # Initialize driver routes
        init_driver_routes()
        
        # Create sample barcodes
        create_sample_barcodes()
        
        print("\n" + "="*60)
        print("Advanced Features Initialization Complete!")
        print("="*60)
        print("\nYou can now:")
        print("1. Test location-based driver assignment")
        print("2. Scan barcodes at /barcode/scan")
        print("3. Use AI commands in chatbot")
        print("\nRun the app: python run.py")


if __name__ == '__main__':
    main()
