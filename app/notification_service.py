"""
Notification Service for FreshConnect
Handles email notifications for expiring products and other alerts
"""

from datetime import datetime, timedelta
from app.models import Product, User
from app import db
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class NotificationService:
    """
    Service for sending notifications to users
    Currently using mock email for development
    In production, configure with real SMTP settings
    """
    
    # Mock email configuration (for development)
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL_ADDRESS = "noreply@freshconnect.com"
    EMAIL_PASSWORD = ""  # Set in production
    
    @staticmethod
    def check_expiring_products(days_threshold=7):
        """
        Check for products expiring within specified days
        Returns list of vendors with their expiring products
        """
        cutoff_date = datetime.now().date() + timedelta(days=days_threshold)
        
        # Find products expiring soon that are not in emergency sale
        expiring_products = Product.query.filter(
            Product.expiry_date <= cutoff_date,
            Product.expiry_date >= datetime.now().date(),
            Product.is_active == True,
            Product.is_emergency == False
        ).all()
        
        # Group by vendor
        vendors_products = {}
        for product in expiring_products:
            vendor_id = product.vendor_id
            if vendor_id not in vendors_products:
                vendors_products[vendor_id] = []
            vendors_products[vendor_id].append(product)
        
        return vendors_products
    
    @staticmethod
    def send_expiry_notification(vendor_id, products):
        """
        Send email notification to vendor about expiring products
        """
        vendor = User.query.get(vendor_id)
        if not vendor or vendor.user_type != 'vendor':
            return False
        
        # In development, just print the notification
        # In production, send actual email
        
        print(f"\n{'='*60}")
        print(f"📧 EMAIL NOTIFICATION")
        print(f"{'='*60}")
        print(f"To: {vendor.email}")
        print(f"Subject: ⚠️ Products Expiring Soon - Action Required")
        print(f"\nDear {vendor.business_name or vendor.name},")
        print(f"\nYou have {len(products)} product(s) expiring soon:\n")
        
        for product in products:
            days_left = (product.expiry_date - datetime.now().date()).days
            print(f"  • {product.product_name}")
            print(f"    Expiry: {product.expiry_date.strftime('%d-%m-%Y')} ({days_left} days left)")
            print(f"    Quantity: {product.quantity} {product.unit}")
            print(f"    Current Price: ₹{product.price}")
            print()
        
        print(f"💡 RECOMMENDED ACTIONS:")
        print(f"  1. Mark products for emergency sale (up to 50% discount)")
        print(f"  2. Reduce prices to sell quickly")
        print(f"  3. Update inventory if products are sold elsewhere")
        print(f"\nLogin to FreshConnect: http://127.0.0.1:5000/auth/login")
        print(f"Go to: Vendor → Emergency Dashboard")
        print(f"\n{'='*60}\n")
        
        # For production: send actual email
        # NotificationService._send_email(vendor.email, subject, body)
        
        return True
    
    @staticmethod
    def _send_email(to_email, subject, body):
        """
        Send actual email (for production)
        Requires SMTP configuration
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = NotificationService.EMAIL_ADDRESS
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'html'))
            
            # Send via SMTP
            # Uncomment for production use
            # server = smtplib.SMTP(NotificationService.SMTP_SERVER, NotificationService.SMTP_PORT)
            # server.starttls()
            # server.login(NotificationService.EMAIL_ADDRESS, NotificationService.EMAIL_PASSWORD)
            # text = msg.as_string()
            # server.sendmail(NotificationService.EMAIL_ADDRESS, to_email, text)
            # server.quit()
            
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    @staticmethod
    def generate_email_body(vendor, products):
        """
        Generate HTML email body for expiry notification
        """
        products_html = ""
        for product in products:
            days_left = (product.expiry_date - datetime.now().date()).days
            products_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{product.product_name}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{product.expiry_date.strftime('%d-%m-%Y')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd; color: {'red' if days_left <= 3 else 'orange'};">{days_left} days</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{product.quantity} {product.unit}</td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #28a745; margin: 0;">🍃 FreshConnect</h1>
                </div>
                
                <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin-bottom: 20px;">
                    <h2 style="color: #856404; margin-top: 0;">⚠️ Products Expiring Soon</h2>
                </div>
                
                <p>Dear <strong>{vendor.business_name or vendor.name}</strong>,</p>
                
                <p>You have <strong>{len(products)}</strong> product(s) that will expire soon. Immediate action is recommended to minimize losses.</p>
                
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #f8f9fa;">
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">Product</th>
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">Expiry Date</th>
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">Days Left</th>
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">Quantity</th>
                        </tr>
                    </thead>
                    <tbody>
                        {products_html}
                    </tbody>
                </table>
                
                <div style="background-color: #d1ecf1; border-left: 4px solid #17a2b8; padding: 15px; margin: 20px 0;">
                    <h3 style="color: #0c5460; margin-top: 0;">💡 Recommended Actions:</h3>
                    <ol style="color: #0c5460; margin: 10px 0;">
                        <li>Mark products for <strong>Emergency Sale</strong> (up to 50% discount)</li>
                        <li>Reduce prices to sell quickly before expiry</li>
                        <li>Update inventory if products sold elsewhere</li>
                    </ol>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://127.0.0.1:5000/auth/login" 
                       style="display: inline-block; background-color: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Login to FreshConnect
                    </a>
                </div>
                
                <p style="color: #6c757d; font-size: 12px; text-align: center; margin-top: 30px;">
                    This is an automated notification from FreshConnect.<br>
                    Please do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    @staticmethod
    def auto_hide_expired_products():
        """
        Automatically hide products that have already expired
        """
        expired_products = Product.query.filter(
            Product.expiry_date < datetime.now().date(),
            Product.is_active == True
        ).all()
        
        count = 0
        for product in expired_products:
            product.is_active = False
            count += 1
        
        if count > 0:
            db.session.commit()
            print(f"✓ Auto-hidden {count} expired products")
        
        return count
    
    @staticmethod
    def send_bulk_expiry_notifications():
        """
        Send notifications to all vendors with expiring products
        This should be run daily via cron job
        """
        print("\n" + "="*60)
        print("🔔 RUNNING DAILY EXPIRY CHECK")
        print("="*60)
        
        # Auto-hide expired products first
        hidden_count = NotificationService.auto_hide_expired_products()
        
        # Check for products expiring in next 7 days
        vendors_products = NotificationService.check_expiring_products(days_threshold=7)
        
        notifications_sent = 0
        for vendor_id, products in vendors_products.items():
            if NotificationService.send_expiry_notification(vendor_id, products):
                notifications_sent += 1
        
        print(f"\n📊 SUMMARY:")
        print(f"  • Expired products hidden: {hidden_count}")
        print(f"  • Vendors notified: {notifications_sent}")
        print(f"  • Total expiring products: {sum(len(p) for p in vendors_products.values())}")
        print("="*60 + "\n")
        
        return {
            'hidden': hidden_count,
            'notified': notifications_sent,
            'total_expiring': sum(len(p) for p in vendors_products.values())
        }
