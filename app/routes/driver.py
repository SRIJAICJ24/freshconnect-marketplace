from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Driver, DriverAssignment, Order, DriverRoute, DeliveryStep, OrderLocationDetail, OrderItem, Product, User
from app.decorators import driver_required
from app.driver_service import MockDriverService
from datetime import datetime

bp = Blueprint('driver', __name__, url_prefix='/driver')

@bp.route('/dashboard')
@driver_required
def dashboard():
    try:
        # Get or create driver profile
        driver = Driver.query.filter_by(user_id=current_user.id).first()
        
        # If no driver profile exists, create one with proper field names
        if not driver:
            driver = Driver(
                user_id=current_user.id,
                vehicle_type='bike',
                vehicle_registration='PENDING',
                status='available',
                current_load_kg=0,
                vehicle_capacity_kg=50,
                total_deliveries=0,
                rating=5.0,
                is_active=True
            )
            db.session.add(driver)
            db.session.commit()
            print(f"✅ Created driver profile for user {current_user.id}")
        else:
            # Ensure all required fields have default values (for old drivers)
            updated = False
            if not driver.vehicle_type:
                driver.vehicle_type = 'bike'
                updated = True
            if not driver.vehicle_registration:
                driver.vehicle_registration = f'TN-00-XX-{str(driver.id).zfill(4)}'
                updated = True
            if driver.vehicle_capacity_kg is None:
                driver.vehicle_capacity_kg = 50
                updated = True
            if driver.current_load_kg is None:
                driver.current_load_kg = 0
                updated = True
            if not driver.status:
                driver.status = 'available'
                updated = True
            if driver.rating is None:
                driver.rating = 5.0
                updated = True
            if driver.total_deliveries is None:
                driver.total_deliveries = 0
                updated = True
            
            if updated:
                db.session.commit()
                print(f"✅ Updated driver profile with missing fields for user {current_user.id}")
        
        # Get pending assignments count
        pending = DriverAssignment.query.filter_by(
            driver_id=driver.id,
            assignment_status='assigned'
        ).count()
        
        # Get active deliveries count
        active = DriverAssignment.query.filter_by(
            driver_id=driver.id,
            assignment_status='in_transit'
        ).count()
        
        return render_template('driver/dashboard.html',
                             driver=driver,
                             pending=pending,
                             active=active)
                             
    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        print(f"❌ Driver dashboard error for user {current_user.id}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Show detailed error message
        error_msg = f'Dashboard error: {str(e)[:100]}'
        flash(error_msg, 'danger')
        flash('Try using one of the new comprehensive driver accounts instead!', 'info')
        
        # Return a simple error page
        return render_template('error.html', 
                             code=500,
                             message='Driver dashboard could not load. Please try logging in with a comprehensive driver account (e.g., rajesh.bike@freshconnect.com).'), 500

@bp.route('/assignments')
@driver_required
def assignments():
    try:
        # Get driver profile
        driver = Driver.query.filter_by(user_id=current_user.id).first()
        
        # If no driver profile exists, create one
        if not driver:
            driver = Driver(
                user_id=current_user.id,
                vehicle_type='bike',
                vehicle_registration='PENDING',
                status='available',
                current_load_kg=0,
                vehicle_capacity_kg=50,
                total_deliveries=0,
                rating=5.0,
                is_active=True
            )
            db.session.add(driver)
            db.session.commit()
            print(f"✅ Created driver profile for user {current_user.id}")
        
        # Get pending assignments
        pending_assignments = DriverAssignment.query.filter_by(
            driver_id=driver.id,
            assignment_status='assigned'
        ).all()
        
        return render_template('driver/assignments.html', 
                             assignments=pending_assignments,
                             driver=driver)
                             
    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        print(f"❌ Error in assignments route: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('Error loading assignments. Please try again or contact support.', 'danger')
        return redirect(url_for('driver.dashboard'))

@bp.route('/delivery/<int:assignment_id>')
@driver_required
def delivery(assignment_id):
    try:
        # Get driver profile
        driver = Driver.query.filter_by(user_id=current_user.id).first()
        if not driver:
            flash('Driver profile not found. Please contact admin.', 'danger')
            return redirect(url_for('driver.dashboard'))
        
        # Get assignment
        assignment = DriverAssignment.query.get_or_404(assignment_id)
        
        # Verify driver authorization
        if assignment.driver_id != driver.id:
            flash('You are not authorized to view this delivery.', 'danger')
            return redirect(url_for('driver.dashboard'))
        
        # Get order
        order = Order.query.get(assignment.order_id)
        
        # Get vendor
        vendor = User.query.get(order.seller_id) if order else None
        
        # Get order items
        order_items = OrderItem.query.filter_by(order_id=order.id).all() if order else []
        
        # Get delivery steps
        delivery_steps = DeliveryStep.query.filter_by(
            order_id=order.id
        ).order_by(
            DeliveryStep.step_number
        ).all() if order else []
        
        return render_template('driver/delivery.html',
                            assignment=assignment,
                            order=order,
                            order_items=order_items,
                            vendor=vendor,
                            delivery_steps=delivery_steps,
                            driver=driver)
                            
    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        print(f"❌ Error in delivery route: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('Error loading delivery details. Please try again or contact support.', 'danger')
        return redirect(url_for('driver.assignments'))

@bp.route('/delivery/<int:assignment_id>/pickup', methods=['POST'])
@driver_required
def mark_pickup(assignment_id):
    try:
        # Get driver profile
        driver = Driver.query.filter_by(user_id=current_user.id).first()
        if not driver:
            flash('Driver profile not found. Please contact admin.', 'danger')
            return redirect(url_for('driver.dashboard'))
        
        # Get assignment
        assignment = DriverAssignment.query.get_or_404(assignment_id)
        
        # Verify driver authorization
        if assignment.driver_id != driver.id:
            flash('You are not authorized to update this delivery.', 'danger')
            return redirect(url_for('driver.dashboard'))
        
        # Get order
        order = assignment.order_rel
        
        # Update assignment and order status
        assignment.assignment_status = 'in_transit'
        assignment.actual_pickup_time = datetime.utcnow()
        order.order_status = 'in_transit'
        
        # Update driver status
        driver.status = 'on_delivery'
        driver.current_load_kg += assignment.weight_assigned_kg or 0
        
        # Create/update delivery step
        pickup_step = DeliveryStep.query.filter_by(
            order_id=order.id,
            step_number=2
        ).first()
        
        if not pickup_step:
            pickup_step = DeliveryStep(
                order_id=order.id,
                step_number=2,
                step_name='Picked Up',
                status='completed',
                completed_at=datetime.utcnow()
            )
            db.session.add(pickup_step)
        else:
            pickup_step.status = 'completed'
            pickup_step.completed_at = datetime.utcnow()
        
        # Commit transaction
        db.session.commit()
        
        # Log the status change
        print(f"[PICKUP] Order {order.id} picked up by driver {driver.id}")
        
        flash('Order picked up successfully!', 'success')
        return redirect(url_for('driver.delivery', assignment_id=assignment_id))
        
    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        print(f"❌ Error in pickup route: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('Error updating pickup status. Please try again or contact support.', 'danger')
        return redirect(url_for('driver.delivery', assignment_id=assignment_id))

@bp.route('/delivery/<int:assignment_id>/deliver', methods=['POST'])
@driver_required
def mark_delivery(assignment_id):
    try:
        # Get driver profile
        driver = Driver.query.filter_by(user_id=current_user.id).first()
        if not driver:
            flash('Driver profile not found. Please contact admin.', 'danger')
            return redirect(url_for('driver.dashboard'))
        
        # Get assignment
        assignment = DriverAssignment.query.get_or_404(assignment_id)
        
        # Verify driver authorization
        if assignment.driver_id != driver.id:
            flash('You are not authorized to complete this delivery.', 'danger')
            return redirect(url_for('driver.dashboard'))
        
        # Get order
        order = assignment.order_rel
        
        # Update assignment and order status
        assignment.assignment_status = 'delivered'
        assignment.actual_delivery_time = datetime.utcnow()
        order.order_status = 'delivered'
        
        # Update driver status and metrics
        driver.current_load_kg -= assignment.weight_assigned_kg or 0
        driver.status = 'available'
        driver.total_deliveries = (driver.total_deliveries or 0) + 1
        
        # Create/update delivery step for delivery completion
        delivery_step = DeliveryStep.query.filter_by(
            order_id=order.id,
            step_number=4
        ).first()
        
        if not delivery_step:
            delivery_step = DeliveryStep(
                order_id=order.id,
                step_number=4,
                step_name='Delivered',
                status='completed',
                completed_at=datetime.utcnow()
            )
            db.session.add(delivery_step)
        else:
            delivery_step.status = 'completed'
            delivery_step.completed_at = datetime.utcnow()
        
        # Commit transaction
        db.session.commit()
        
        # Log the delivery completion
        print(f"[DELIVERY] Order {order.id} delivered by driver {driver.id}")
        print(f"[EARNINGS] Driver {driver.user.name} earned ₹{assignment.weight_assigned_kg * 10 if assignment.weight_assigned_kg else 0}")
        
        flash('Delivery marked as complete successfully!', 'success')
        return redirect(url_for('driver.dashboard'))
        
    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        print(f"❌ Error in delivery completion route: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('Error completing delivery. Please try again or contact support.', 'danger')
        return redirect(url_for('driver.delivery', assignment_id=assignment_id))


# ============ NEW LOCATION-BASED FEATURES ============

@bp.route('/routes')
@driver_required
def routes():
    """Show driver's planned routes with location details"""
    driver = Driver.query.filter_by(user_id=current_user.id).first()
    
    if not driver:
        flash('Driver profile not found.', 'danger')
        return redirect(url_for('driver.dashboard'))
    
    # Get planned routes
    planned_routes = DriverRoute.query.filter_by(driver_id=driver.id).all()
    
    return render_template('driver/routes.html', 
                         driver=driver,
                         routes=planned_routes)


@bp.route('/deliveries')
@driver_required
def deliveries():
    """Show all deliveries with location and logistics details"""
    driver = Driver.query.filter_by(user_id=current_user.id).first()
    
    if not driver:
        flash('Driver profile not found.', 'danger')
        return redirect(url_for('driver.dashboard'))
    
    # Get orders assigned to this driver
    assigned_orders = Order.query.filter_by(assigned_driver_id=driver.id).all()
    
    # Get location details for each order
    deliveries_with_details = []
    for order in assigned_orders:
        location_detail = OrderLocationDetail.query.filter_by(order_id=order.id).first()
        delivery_steps = DeliveryStep.query.filter_by(order_id=order.id).order_by(DeliveryStep.step_number).all()
        
        deliveries_with_details.append({
            'order': order,
            'location': location_detail,
            'steps': delivery_steps
        })
    
    return render_template('driver/deliveries.html',
                         driver=driver,
                         deliveries=deliveries_with_details)


@bp.route('/delivery-detail/<int:order_id>')
@driver_required
def delivery_detail(order_id):
    """Show detailed delivery information with route and pricing"""
    driver = Driver.query.filter_by(user_id=current_user.id).first()
    
    if not driver:
        flash('Driver profile not found.', 'danger')
        return redirect(url_for('driver.dashboard'))
    
    order = Order.query.get_or_404(order_id)
    
    # Verify this is driver's order
    if order.assigned_driver_id != driver.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('driver.deliveries'))
    
    # Get driver assignment for this order
    assignment = DriverAssignment.query.filter_by(
        driver_id=driver.id,
        order_id=order_id
    ).first()
    
    # Get location and step details
    location_detail = OrderLocationDetail.query.filter_by(order_id=order_id).first()
    delivery_steps = DeliveryStep.query.filter_by(order_id=order_id).order_by(DeliveryStep.step_number).all()
    
    return render_template('driver/delivery_detail.html',
                         driver=driver,
                         order=order,
                         assignment=assignment,
                         location=location_detail,
                         steps=delivery_steps)
