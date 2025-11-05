from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Driver, DriverAssignment, Order, DriverRoute, DeliveryStep, OrderLocationDetail
from app.decorators import driver_required
from app.driver_service import MockDriverService
from datetime import datetime

bp = Blueprint('driver', __name__, url_prefix='/driver')

@bp.route('/dashboard')
@driver_required
def dashboard():
    driver = Driver.query.filter_by(user_id=current_user.id).first()
    
    pending = DriverAssignment.query.filter_by(
        driver_id=driver.id,
        assignment_status='assigned'
    ).count()
    
    active = DriverAssignment.query.filter_by(
        driver_id=driver.id,
        assignment_status='in_transit'
    ).count()
    
    return render_template('driver/dashboard.html',
                         driver=driver,
                         pending=pending,
                         active=active)

@bp.route('/assignments')
@driver_required
def assignments():
    driver = Driver.query.filter_by(user_id=current_user.id).first()
    
    pending = DriverAssignment.query.filter_by(
        driver_id=driver.id,
        assignment_status='assigned'
    ).all()
    
    return render_template('driver/assignments.html', assignments=pending)

@bp.route('/delivery/<int:assignment_id>')
@driver_required
def delivery(assignment_id):
    assignment = DriverAssignment.query.get_or_404(assignment_id)
    
    driver = Driver.query.filter_by(user_id=current_user.id).first()
    if assignment.driver_id != driver.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('driver.dashboard'))
    
    return render_template('driver/delivery.html', assignment=assignment)

@bp.route('/delivery/<int:assignment_id>/pickup', methods=['POST'])
@driver_required
def mark_pickup(assignment_id):
    assignment = DriverAssignment.query.get_or_404(assignment_id)
    
    assignment.assignment_status = 'picked_up'
    assignment.actual_pickup_time = datetime.utcnow()
    assignment.order_rel.order_status = 'in_transit'
    
    db.session.commit()
    
    print(f"[MOCK SMS] Order picked up: {assignment.order_id}")
    
    return redirect(url_for('driver.delivery', assignment_id=assignment_id))

@bp.route('/delivery/<int:assignment_id>/deliver', methods=['POST'])
@driver_required
def mark_delivery(assignment_id):
    assignment = DriverAssignment.query.get_or_404(assignment_id)
    
    assignment.assignment_status = 'delivered'
    assignment.actual_delivery_time = datetime.utcnow()
    assignment.order_rel.order_status = 'delivered'
    
    driver = assignment.driver
    driver.current_load_kg -= assignment.weight_assigned_kg
    driver.status = 'available'
    driver.total_deliveries += 1
    
    db.session.commit()
    
    print(f"[MOCK EARNINGS] Driver {driver.user.name} earned ₹{assignment.weight_assigned_kg * 10}")
    
    flash('Delivery marked complete!', 'success')
    return redirect(url_for('driver.dashboard'))


# ============ NEW LOCATION-BASED FEATURES ============

@bp.route('/routes')
@driver_required
def routes():
    """Show driver's planned routes with location details"""
    driver = Driver.query.filter_by(user_id=current_user.id).first()
    
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
    
    order = Order.query.get_or_404(order_id)
    
    # Verify this is driver's order
    if order.assigned_driver_id != driver.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('driver.deliveries'))
    
    # Get location and step details
    location_detail = OrderLocationDetail.query.filter_by(order_id=order_id).first()
    delivery_steps = DeliveryStep.query.filter_by(order_id=order_id).order_by(DeliveryStep.step_number).all()
    
    return render_template('driver/delivery_detail.html',
                         driver=driver,
                         order=order,
                         location=location_detail,
                         steps=delivery_steps)
