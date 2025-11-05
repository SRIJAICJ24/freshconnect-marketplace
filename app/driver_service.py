import random
from datetime import datetime, timedelta
from app import db
from app.models import Driver, DriverAssignment, Order

class MockDriverService:
    """
    MOCK DRIVER ASSIGNMENT - NOT REAL GPS
    FOR COLLEGE PROJECT DEMONSTRATION
    """
    
    @staticmethod
    def find_available_drivers():
        """Get mock available drivers"""
        
        drivers = Driver.query.filter_by(
            status='available',
            is_active=True
        ).all()
        
        return drivers
    
    @staticmethod
    def assign_driver_to_order(order_id, weight_kg, delivery_area):
        """
        MOCK DRIVER ASSIGNMENT
        Randomly selects available driver
        """
        
        try:
            order = Order.query.get_or_404(order_id)
            available_drivers = MockDriverService.find_available_drivers()
            
            if not available_drivers:
                return False, "No drivers available"
            
            # MOCK: Random selection
            selected_driver = random.choice(available_drivers)
            
            assignment = DriverAssignment(
                order_id=order_id,
                driver_id=selected_driver.id,
                assignment_status='assigned',
                assigned_at=datetime.utcnow(),
                pickup_location=order.seller.address,
                delivery_location=order.delivery_address,
                weight_assigned_kg=weight_kg,
                estimated_delivery_time=datetime.utcnow() + timedelta(
                    minutes=random.randint(30, 60)
                )
            )
            
            order.assigned_driver_id = selected_driver.id
            order.order_status = 'driver_assigned'
            
            selected_driver.status = 'on_delivery'
            selected_driver.current_load_kg += weight_kg
            
            db.session.add(assignment)
            db.session.commit()
            
            print(f"[MOCK DRIVER] {selected_driver.user.name} assigned to order {order_id}")
            
            return True, f"Driver assigned"
        
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_mock_driver_location(assignment_id):
        """
        MOCK GPS LOCATION
        Returns random coordinates in Chennai
        """
        
        assignment = DriverAssignment.query.get_or_404(assignment_id)
        
        lat = 13.0827 + random.uniform(-0.01, 0.01)
        lng = 80.2707 + random.uniform(-0.01, 0.01)
        
        eta_minutes = max(0, int(
            (assignment.estimated_delivery_time - datetime.utcnow()).total_seconds() / 60
        ))
        
        return {
            'driver': assignment.driver.user.name,
            'lat': round(lat, 6),
            'lng': round(lng, 6),
            'eta_minutes': eta_minutes,
            'mock': True
        }
