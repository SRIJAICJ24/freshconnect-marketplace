"""
FEATURE 1: Smart Location-Based Driver Assignment
MOCK Implementation for College Project
"""

import random
from datetime import datetime, timedelta
from app import db
from app.models import Driver, DriverRoute, Order, OrderLocationDetail, DeliveryStep

class LocationBasedAssignmentService:
    """
    MOCK Location-based driver assignment
    
    Logic:
    1. Get available drivers
    2. Check if their route passes near retailer location
    3. Calculate detour distance
    4. Calculate pricing (volume + weight + detour)
    5. Assign driver and update payment
    """
    
    # MOCK Fixed routes for demo (Koyambedu to various destinations)
    MOCK_DRIVER_ROUTES = [
        {
            'start': 'Koyambedu Market',
            'end': 'Chromepet',
            'start_lat': '13.0827',
            'start_lng': '80.2707',
            'end_lat': '12.9716',
            'end_lng': '80.2202',
            'distance_km': 25,
            'time_hours': 1.5
        },
        {
            'start': 'Koyambedu Market',
            'end': 'Velachery',
            'start_lat': '13.0827',
            'start_lng': '80.2707',
            'end_lat': '12.9689',
            'end_lng': '80.2350',
            'distance_km': 22,
            'time_hours': 1.2
        },
        {
            'start': 'Koyambedu Market',
            'end': 'Guindy',
            'start_lat': '13.0827',
            'start_lng': '80.2707',
            'end_lat': '13.0012',
            'end_lng': '80.2175',
            'distance_km': 10,
            'time_hours': 0.7
        },
        {
            'start': 'Koyambedu Market',
            'end': 'Adyar',
            'start_lat': '13.0827',
            'start_lng': '80.2707',
            'end_lat': '12.9971',
            'end_lng': '80.2421',
            'distance_km': 15,
            'time_hours': 1.0
        },
        {
            'start': 'Koyambedu Market',
            'end': 'Tambaram',
            'start_lat': '13.0827',
            'start_lng': '80.2707',
            'end_lat': '12.9250',
            'end_lng': '80.1450',
            'distance_km': 28,
            'time_hours': 1.8
        }
    ]
    
    # MOCK Retailer locations for demo
    MOCK_RETAILER_LOCATIONS = {
        'Chromepet': {'lat': '12.9750', 'lng': '80.2150'},
        'Velachery': {'lat': '12.9700', 'lng': '80.2300'},
        'Guindy': {'lat': '13.0050', 'lng': '80.2100'},
        'Adyar': {'lat': '13.0000', 'lng': '80.2400'},
        'Tambaram': {'lat': '12.9250', 'lng': '80.1450'},
        'Porur': {'lat': '13.0358', 'lng': '80.1559'},
        'T.Nagar': {'lat': '13.0417', 'lng': '80.2341'},
    }
    
    @staticmethod
    def calculate_volume_from_products(order_items):
        """
        Calculate volume from order items
        
        MOCK Formula:
        Volume (m³) = (weight_kg × quantity) × 0.001
        
        Real: Would use product dimensions
        """
        
        total_volume = 0
        total_weight = 0
        
        for item in order_items:
            # MOCK: Each kg ≈ 0.001 m³ (varies by product density)
            volume = (item.quantity * 0.001)
            total_volume += volume
            total_weight += item.quantity
        
        return round(total_volume, 3), round(total_weight, 2)
    
    @staticmethod
    def calculate_distance_between_points(lat1, lng1, lat2, lng2):
        """
        MOCK: Calculate distance between two coordinates
        
        Real: Would use Haversine formula or Google Maps API
        
        MOCK: Random distance 3-8 km
        """
        
        # Simple MOCK: Just generate random distance
        distance = random.uniform(3, 8)
        return round(distance, 2)
    
    @staticmethod
    def find_optimal_driver(order_location, volume_m3, total_weight_kg):
        """
        Find best driver based on:
        1. Route passes near retailer location
        2. Has available capacity
        3. Minimize detour distance
        """
        
        try:
            available_drivers = Driver.query.filter_by(
                status='available',
                is_active=True
            ).all()
            
            if not available_drivers:
                return None, "No drivers available"
            
            candidates = []
            
            for driver in available_drivers:
                # Check if driver has capacity
                available_capacity = driver.vehicle_capacity_kg - driver.current_load_kg
                
                if available_capacity < total_weight_kg:
                    continue  # Skip - no capacity
                
                # MOCK: Get random route for this driver
                route = random.choice(LocationBasedAssignmentService.MOCK_DRIVER_ROUTES)
                
                # Calculate detour distance (MOCK)
                detour_distance = LocationBasedAssignmentService.calculate_distance_between_points(
                    route['start_lat'], route['start_lng'],
                    route['end_lat'], route['end_lng']
                )
                
                candidates.append({
                    'driver': driver,
                    'route': route,
                    'detour_distance': detour_distance,
                    'score': 100 - (detour_distance * 2)  # Prefer shorter detours
                })
            
            if not candidates:
                return None, "No drivers with sufficient capacity"
            
            # Sort by score (highest first = best)
            candidates.sort(key=lambda x: x['score'], reverse=True)
            
            return candidates[0], "Driver found"
        
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def calculate_pricing(volume_m3, total_weight_kg, detour_distance_km, product_cost):
        """
        Calculate total logistics cost
        
        Breakdown:
        - Base: product_cost
        - Volume charge: ₹10 per 0.1 m³
        - Driver rate: ₹10 per kg
        - Detour charge: ₹5 per extra km
        """
        
        volume_charge = (volume_m3 / 0.1) * 10  # ₹10 per 0.1m³
        driver_rate = total_weight_kg * 10  # ₹10 per kg
        detour_charge = detour_distance_km * 5  # ₹5 per extra km
        
        total_logistics = volume_charge + driver_rate + detour_charge
        final_amount = product_cost + total_logistics
        
        return {
            'product_cost': round(product_cost, 2),
            'volume_charge': round(volume_charge, 2),
            'driver_rate': round(driver_rate, 2),
            'detour_charge': round(detour_charge, 2),
            'total_logistics': round(total_logistics, 2),
            'final_amount': round(final_amount, 2)
        }
    
    @staticmethod
    def create_order_with_location_assignment(order_id, retailer_location, delivery_items):
        """
        Complete flow:
        1. Calculate volume/weight
        2. Find optimal driver
        3. Calculate pricing
        4. Create delivery steps (4 stages)
        5. Update order with details
        """
        
        try:
            order = Order.query.get_or_404(order_id)
            
            # Step 1: Calculate volume and weight
            volume_m3, total_weight_kg = LocationBasedAssignmentService.calculate_volume_from_products(
                order.items
            )
            
            # Step 2: Find optimal driver
            driver_result, message = LocationBasedAssignmentService.find_optimal_driver(
                retailer_location, volume_m3, total_weight_kg
            )
            
            if not driver_result:
                return False, message
            
            driver_info = driver_result
            selected_driver = driver_info['driver']
            route = driver_info['route']
            
            # Step 3: Calculate pricing
            pricing = LocationBasedAssignmentService.calculate_pricing(
                volume_m3,
                total_weight_kg,
                driver_info['detour_distance'],
                order.total_amount
            )
            
            # Get or create retailer location coordinates
            location_coords = LocationBasedAssignmentService.MOCK_RETAILER_LOCATIONS.get(
                retailer_location,
                {'lat': str(round(random.uniform(12.9, 13.1), 4)), 
                 'lng': str(round(random.uniform(80.1, 80.3), 4))}
            )
            
            # Create location detail record
            location_detail = OrderLocationDetail(
                order_id=order_id,
                retailer_location=retailer_location,
                retailer_lat=location_coords['lat'],
                retailer_lng=location_coords['lng'],
                volume_m3=volume_m3,
                total_weight_kg=total_weight_kg,
                distance_from_vendor_km=round(random.uniform(5, 25), 2),
                detour_distance_km=driver_info['detour_distance'],
                product_cost=order.total_amount,
                volume_charge=pricing['volume_charge'],
                driver_rate=pricing['driver_rate'],
                detour_charge=pricing['detour_charge'],
                total_logistics_cost=pricing['total_logistics'],
                final_amount=pricing['final_amount']
            )
            
            db.session.add(location_detail)
            db.session.flush()
            
            # Update order
            order.total_amount = pricing['final_amount']
            order.logistics_cost = pricing['total_logistics']
            order.assigned_driver_id = selected_driver.id
            
            # Step 4: Create 4 delivery steps
            steps = [
                {
                    'number': 1,
                    'name': 'Order Confirmed',
                    'status': 'completed',
                    'details': {
                        'product_name': order.items[0].product.product_name if order.items else 'Products',
                        'quantity': sum(item.quantity for item in order.items),
                        'price': f"₹{order.total_amount}",
                        'volume': f"{volume_m3:.3f} m³",
                        'weight': f"{total_weight_kg} kg"
                    }
                },
                {
                    'number': 2,
                    'name': 'Payment Done',
                    'status': 'pending',
                    'details': {
                        'payment_status': 'Awaiting Payment',
                        'driver_name': selected_driver.user.name,
                        'vehicle': f"{selected_driver.vehicle_type} - {selected_driver.vehicle_registration}",
                        'parking_location': selected_driver.parking_location,
                        'route': f"{route['start']} → {route['end']}",
                        'estimated_time': f"{route['time_hours']:.1f} hours",
                        'distance': f"{route['distance_km']} km"
                    }
                },
                {
                    'number': 3,
                    'name': 'Product Shipped',
                    'status': 'pending',
                    'details': {
                        'location': 'Waiting for vendor to confirm pickup',
                        'vendor': order.seller.business_name,
                        'time': 'Pending'
                    }
                },
                {
                    'number': 4,
                    'name': 'Order Delivered',
                    'status': 'pending',
                    'details': {
                        'location': retailer_location,
                        'time': 'Pending Delivery',
                        'driver_rating': 'Pending'
                    }
                }
            ]
            
            for step in steps:
                delivery_step = DeliveryStep(
                    order_id=order_id,
                    step_number=step['number'],
                    step_name=step['name'],
                    status=step['status'],
                    details=step['details'],
                    completed_at=datetime.utcnow() if step['status'] == 'completed' else None
                )
                db.session.add(delivery_step)
            
            # Update driver
            selected_driver.current_load_kg += total_weight_kg
            selected_driver.status = 'assigned'
            
            db.session.commit()
            
            print(f"[LOCATION ASSIGNMENT] Order {order_id} assigned to driver {selected_driver.user.name}")
            print(f"[PRICING] Product: ₹{pricing['product_cost']} + Logistics: ₹{pricing['total_logistics']} = ₹{pricing['final_amount']}")
            print(f"[ROUTE] {route['start']} → {route['end']} ({route['distance_km']} km)")
            
            return True, {
                'success': True,
                'driver': selected_driver.user.name,
                'vehicle': selected_driver.vehicle_registration,
                'route': f"{route['start']} → {route['end']}",
                'pricing': pricing,
                'volume': volume_m3,
                'weight': total_weight_kg,
                'route_details': route
            }
        
        except Exception as e:
            db.session.rollback()
            print(f"[LOCATION ERROR] {str(e)}")
            return False, str(e)
