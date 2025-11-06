from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15))
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    
    user_type = db.Column(db.String(20), nullable=False)
    business_name = db.Column(db.String(100))
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Rating fields (for vendors and drivers)
    average_rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    rating_quality_avg = db.Column(db.Float, default=0.0)
    rating_delay_avg = db.Column(db.Float, default=0.0)
    rating_communication_avg = db.Column(db.Float, default=0.0)
    
    products = db.relationship('Product', backref='vendor', lazy=True, foreign_keys='Product.vendor_id')
    orders_as_buyer = db.relationship('Order', backref='buyer', lazy=True, foreign_keys='Order.buyer_id')
    orders_as_seller = db.relationship('Order', backref='seller', lazy=True, foreign_keys='Order.seller_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.name} ({self.user_type})>'


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    product_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='kg')
    
    expiry_date = db.Column(db.Date)
    
    # EMERGENCY MARKETPLACE FIELDS
    is_emergency = db.Column(db.Boolean, default=False, index=True)
    emergency_discount = db.Column(db.Float, default=0)  # Discount % (0-100)
    original_price_backup = db.Column(db.Float)  # Store original price before discount
    emergency_marked_at = db.Column(db.DateTime)  # When vendor marked as emergency
    days_until_expiry = db.Column(db.Integer)  # Auto-calculated days remaining
    
    image_filename = db.Column(db.String(255))
    
    moq_enabled = db.Column(db.Boolean, default=False)
    moq_type = db.Column(db.String(20))
    minimum_quantity = db.Column(db.Float)
    minimum_weight = db.Column(db.Float)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # EMERGENCY MARKETPLACE METHODS
    def mark_as_emergency(self, discount_percentage):
        """Mark product as emergency sale"""
        from datetime import datetime, date
        
        self.is_emergency = True
        self.emergency_discount = discount_percentage
        self.original_price_backup = self.price
        self.emergency_marked_at = datetime.utcnow()
        self.price = self.original_price_backup * (1 - discount_percentage / 100)
        
        if self.expiry_date:
            days_diff = (self.expiry_date - date.today()).days
            self.days_until_expiry = max(0, days_diff)
    
    def remove_emergency(self):
        """Remove emergency flag and restore original price"""
        self.is_emergency = False
        if self.original_price_backup:
            self.price = self.original_price_backup
        self.emergency_discount = 0
        self.emergency_marked_at = None
    
    def get_emergency_status(self):
        """Get urgency status for display"""
        if not self.is_emergency:
            return None
        
        if self.days_until_expiry == 0:
            return {'status': 'URGENT', 'color': 'danger', 'icon': '⚠️', 'message': 'Expires TODAY'}
        elif self.days_until_expiry == 1:
            return {'status': 'VERY URGENT', 'color': 'danger', 'icon': '🔥', 'message': 'Expires TOMORROW'}
        elif self.days_until_expiry <= 3:
            return {'status': 'URGENT', 'color': 'warning', 'icon': '⏰', 'message': f'Expires in {self.days_until_expiry} days'}
        else:
            return {'status': 'LIMITED TIME', 'color': 'info', 'icon': '⏳', 'message': f'Expires in {self.days_until_expiry} days'}
    
    def __repr__(self):
        return f'<Product {self.product_name}>'


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    total_amount = db.Column(db.Float, nullable=False)
    order_status = db.Column(db.String(50), default='pending', index=True)
    payment_status = db.Column(db.String(50), default='pending')
    
    delivery_address = db.Column(db.String(255), nullable=False)
    logistics_cost = db.Column(db.Float, default=0)
    
    assigned_driver_id = db.Column(db.Integer)
    transaction_id = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Order tracking timestamps (4-step process)
    payment_confirmed_at = db.Column(db.DateTime)
    shipped_in_truck_at = db.Column(db.DateTime)
    ready_for_delivery_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    payment = db.relationship('Payment', backref='order', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.id}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)
    
    product = db.relationship('Product', backref='order_items')


class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    transaction_id = db.Column(db.String(100), unique=True)
    amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(50), default='pending')
    
    card_last_4 = db.Column(db.String(4))
    payment_method = db.Column(db.String(50), default='card')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)


class Driver(db.Model):
    __tablename__ = 'drivers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    
    vehicle_type = db.Column(db.String(50))
    vehicle_capacity_kg = db.Column(db.Float)
    vehicle_registration = db.Column(db.String(50), unique=True)
    parking_location = db.Column(db.String(100))
    
    current_location = db.Column(db.String(100))
    current_load_kg = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default='available', index=True)
    
    rating = db.Column(db.Float, default=5.0)
    total_deliveries = db.Column(db.Integer, default=0)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='driver_profile')
    
    def __repr__(self):
        return f'<Driver {self.user.name if self.user else "N/A"}>'


class DriverAssignment(db.Model):
    __tablename__ = 'driver_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), unique=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'))
    
    assignment_status = db.Column(db.String(50), default='assigned')
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    actual_pickup_time = db.Column(db.DateTime)
    actual_delivery_time = db.Column(db.DateTime)
    estimated_delivery_time = db.Column(db.DateTime)
    
    pickup_location = db.Column(db.String(255))
    delivery_location = db.Column(db.String(255))
    weight_assigned_kg = db.Column(db.Float)
    
    retailer_rating_to_driver = db.Column(db.Integer)
    driver_rating_to_retailer = db.Column(db.Integer)
    
    driver = db.relationship('Driver', backref='assignments')
    order_rel = db.relationship('Order', backref='assignment')


class RetailerCredit(db.Model):
    __tablename__ = 'retailer_credits'
    
    id = db.Column(db.Integer, primary_key=True)
    retailer_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    
    credit_score = db.Column(db.Integer, default=150)
    credit_tier = db.Column(db.String(50), default='bronze')
    
    total_purchases = db.Column(db.Float, default=0)
    total_orders = db.Column(db.Integer, default=0)
    successful_orders = db.Column(db.Integer, default=0)
    
    credit_limit = db.Column(db.Float, default=0)
    available_credit = db.Column(db.Float, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatLog(db.Model):
    __tablename__ = 'chat_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# ============ ADVANCED FEATURES MODELS ============

# FEATURE 1: Smart Location-Based Driver Assignment
class DriverRoute(db.Model):
    """Driver's planned route for deliveries"""
    __tablename__ = 'driver_routes'
    
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    
    # MOCK Route (fixed for demo)
    starting_location = db.Column(db.String(100))  # e.g., "Koyambedu"
    ending_location = db.Column(db.String(100))    # e.g., "Chromepet"
    
    # MOCK Coordinates (stored as strings for simplicity)
    start_lat = db.Column(db.String(20))
    start_lng = db.Column(db.String(20))
    end_lat = db.Column(db.String(20))
    end_lng = db.Column(db.String(20))
    
    # Route details
    total_distance_km = db.Column(db.Float)  # e.g., 25 km
    estimated_time_hours = db.Column(db.Float)
    
    status = db.Column(db.String(50), default='available')  # available, on_route, completed
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    driver = db.relationship('Driver', backref='routes')


class DeliveryStep(db.Model):
    """4-step order tracking (Amazon-style)"""
    __tablename__ = 'delivery_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    
    # Steps: 1=ordered, 2=payment_done, 3=shipped, 4=delivered
    step_number = db.Column(db.Integer)  # 1, 2, 3, 4
    step_name = db.Column(db.String(100))  # "Order Confirmed", "Payment Done", etc.
    
    status = db.Column(db.String(50))  # completed, pending
    completed_at = db.Column(db.DateTime)
    
    # Details for each step (JSON for flexibility)
    details = db.Column(db.JSON)
    # For step 1: {'product_name': 'Tomato', 'quantity': 50, 'price': '₹1250'}
    # For step 2: {'payment_id': 'MOCK123', 'driver': 'Ravi', 'vehicle': 'Truck'}
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class OrderLocationDetail(db.Model):
    """Detailed location and pricing breakdown for orders"""
    __tablename__ = 'order_location_details'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), unique=True)
    
    # Retailer location (destination)
    retailer_location = db.Column(db.String(100))
    retailer_lat = db.Column(db.String(20))
    retailer_lng = db.Column(db.String(20))
    
    # Driver route
    assigned_driver_route_id = db.Column(db.Integer, db.ForeignKey('driver_routes.id'))
    
    # Calculation data
    volume_m3 = db.Column(db.Float)  # Cubic meters
    total_weight_kg = db.Column(db.Float)
    distance_from_vendor_km = db.Column(db.Float)
    detour_distance_km = db.Column(db.Float)  # Extra distance if driver detours
    
    # Pricing breakdown
    product_cost = db.Column(db.Float)
    volume_charge = db.Column(db.Float)  # ₹10 per 0.1 m³
    driver_rate = db.Column(db.Float)  # ₹10/kg × total_weight
    detour_charge = db.Column(db.Float)  # ₹5 per extra km
    total_logistics_cost = db.Column(db.Float)
    
    final_amount = db.Column(db.Float)  # product_cost + total_logistics_cost
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# FEATURE 2: Barcode-Based Inventory Management
class BarcodeTrack(db.Model):
    """Track barcodes for inventory management"""
    __tablename__ = 'barcode_tracks'
    
    id = db.Column(db.Integer, primary_key=True)
    barcode_number = db.Column(db.String(100), unique=True, index=True)
    
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Who sent (Vendor/Supplier)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Who will receive (Vendor/Retailer)
    
    status = db.Column(db.String(50), default='in_transit')  # in_transit, scanned, added_to_stock, delivered
    
    quantity = db.Column(db.Float)
    unit = db.Column(db.String(20))
    
    scanned_at = db.Column(db.DateTime)
    added_to_stock_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    order = db.relationship('Order', backref='barcodes')
    product = db.relationship('Product', backref='barcodes')
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_barcodes')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_barcodes')


# FEATURE 4: AI Chatbot Command Processing
class ChatbotCommand(db.Model):
    """Track AI chatbot commands and results"""
    __tablename__ = 'chatbot_commands'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    command_text = db.Column(db.Text)  # What user said
    command_intent = db.Column(db.String(100))  # What the app understood (search, check_orders, etc.)
    
    parameters = db.Column(db.JSON)  # Extracted parameters
    # {'product': 'tomato', 'price_max': 50, 'unit': 'kg'}
    
    result_type = db.Column(db.String(50))  # search_results, order_details, credit_info
    result_url = db.Column(db.String(255))  # Where to show results
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# EMERGENCY MARKETPLACE METRICS
class EmergencyMarketplaceMetrics(db.Model):
    """Track daily metrics for emergency marketplace impact"""
    __tablename__ = 'emergency_marketplace_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Date tracking
    date = db.Column(db.Date, default=datetime.utcnow, unique=True, index=True)
    
    # Product metrics
    total_emergency_products = db.Column(db.Integer, default=0)
    total_emergency_items_sold = db.Column(db.Integer, default=0)
    
    # Financial metrics
    original_value_at_risk = db.Column(db.Float, default=0)  # Original price × quantity
    emergency_sale_value = db.Column(db.Float, default=0)  # Discounted price × quantity sold
    total_discount_given = db.Column(db.Float, default=0)  # Money saved for retailers
    vendor_recovery_value = db.Column(db.Float, default=0)  # Money vendors recovered
    
    # Waste metrics
    estimated_waste_prevented_kg = db.Column(db.Float, default=0)
    
    # Unique metrics
    unique_vendors = db.Column(db.Integer, default=0)  # # of vendors with emergency items
    unique_retailers = db.Column(db.Integer, default=0)  # # of retailers buying emergency
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AdminGeneratedStock(db.Model):
    """Admin-created inventory with unique barcodes for vendors to scan and claim"""
    __tablename__ = 'admin_generated_stock'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_generated_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Product details
    product_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='kg')
    price = db.Column(db.Float, nullable=False)
    expiry_date = db.Column(db.Date)
    
    # Barcode/QR code
    barcode_image_path = db.Column(db.String(255))
    qr_code_image_path = db.Column(db.String(255))
    
    # Admin tracking
    created_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Vendor claim tracking
    is_claimed_by_vendor = db.Column(db.Boolean, default=False, index=True)
    claimed_by_vendor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    claimed_at = db.Column(db.DateTime, nullable=True)
    
    # Product ID after vendor claims it
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    
    # Relationships
    created_by_admin = db.relationship('User', foreign_keys=[created_by_admin_id], backref='created_stocks')
    claimed_by_vendor = db.relationship('User', foreign_keys=[claimed_by_vendor_id], backref='claimed_stocks')
    product = db.relationship('Product', backref='admin_stock_source')
    
    def __repr__(self):
        return f'<AdminStock {self.admin_generated_code} - {self.product_name}>'


class OrderStatusLog(db.Model):
    """Track all order status changes for auditing"""
    __tablename__ = 'order_status_log'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    
    status_from = db.Column(db.String(50))
    status_to = db.Column(db.String(50), nullable=False)
    
    changed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    notes = db.Column(db.Text)  # Optional notes about the status change
    
    # Relationships
    order = db.relationship('Order', backref='status_logs')
    changed_by = db.relationship('User', backref='order_status_changes')
    
    def __repr__(self):
        return f'<StatusLog Order#{self.order_id}: {self.status_from} → {self.status_to}>'


class ProductReview(db.Model):
    """Reviews and ratings for vendors and drivers after delivery"""
    __tablename__ = 'product_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Who is reviewing
    retailer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Who is being reviewed
    vendor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    
    # Ratings (1-5 stars)
    rating_quality = db.Column(db.Integer)  # Product quality
    rating_delay = db.Column(db.Integer)  # Timeliness (5=on-time, 1=very late)
    rating_communication = db.Column(db.Integer)  # Communication quality
    
    # Driver-specific ratings
    driver_rating = db.Column(db.Integer)  # Overall driver rating (simplified)
    driver_rating_handling = db.Column(db.Integer)  # Careful handling
    driver_rating_punctuality = db.Column(db.Integer)  # On-time delivery
    driver_rating_communication = db.Column(db.Integer)  # Communication
    
    # Comments
    comment = db.Column(db.Text)
    driver_comment = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    edited_at = db.Column(db.DateTime)
    
    # Relationships
    order = db.relationship('Order', backref='reviews')
    product = db.relationship('Product', backref='reviews')
    retailer = db.relationship('User', foreign_keys=[retailer_id], backref='reviews_given')
    vendor = db.relationship('User', foreign_keys=[vendor_id], backref='reviews_received')
    driver = db.relationship('User', foreign_keys=[driver_id], backref='driver_reviews_received')
    
    def __repr__(self):
        return f'<Review Order#{self.order_id} by Retailer#{self.retailer_id}>'


class UserReport(db.Model):
    """Reports submitted by retailers against vendors/drivers"""
    __tablename__ = 'user_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Who is reporting
    report_from_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)  # Alias for consistency
    
    # Who is being reported
    report_against_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)  # Alias for consistency
    
    # Order reference (optional)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), index=True)
    
    # Report details
    report_type = db.Column(db.String(50), nullable=False)  # vendor, driver, fraud, poor_quality, etc.
    subject = db.Column(db.String(200))  # Report subject/title
    report_text = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)  # Alias for report_text
    severity = db.Column(db.String(20), default='medium')  # low, medium, high
    evidence_attachment = db.Column(db.String(255))  # Image/file path
    
    # Status tracking
    status = db.Column(db.String(50), default='pending', index=True)  # pending, investigating, resolved, dismissed
    admin_response = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    resolved_at = db.Column(db.DateTime)
    
    # Relationships
    reporter = db.relationship('User', foreign_keys=[report_from_id], backref='reports_submitted')
    reported_user = db.relationship('User', foreign_keys=[report_against_id], backref='reports_against')
    
    def __repr__(self):
        return f'<Report #{self.id}: {self.report_type} - {self.status}>'
