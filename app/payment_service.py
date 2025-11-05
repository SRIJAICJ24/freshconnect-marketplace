import random
import uuid
from datetime import datetime
from app import db
from app.models import Payment, Order

class MockPaymentGateway:
    """
    MOCK PAYMENT GATEWAY - NOT REAL
    FOR COLLEGE PROJECT DEMONSTRATION
    """
    
    @staticmethod
    def generate_transaction_id():
        """Generate mock transaction ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_code = str(uuid.uuid4())[:8].upper()
        return f"MOCKTXN{timestamp}{unique_code}"
    
    @staticmethod
    def validate_card(card_number, expiry, cvv):
        """Mock card validation - format only"""
        
        if not card_number or len(card_number) != 16:
            return False, "Card number must be 16 digits"
        
        if not card_number.isdigit():
            return False, "Card number must be digits"
        
        if not expiry or len(expiry) != 5 or '/' not in expiry:
            return False, "Expiry must be MM/YY"
        
        if not cvv or len(cvv) != 3 or not cvv.isdigit():
            return False, "CVV must be 3 digits"
        
        return True, "Valid"
    
    @staticmethod
    def process_payment(order_id, card_number, expiry, cvv, amount):
        """
        MOCK PAYMENT PROCESSING
        70% success rate (for demo)
        """
        
        try:
            is_valid, message = MockPaymentGateway.validate_card(card_number, expiry, cvv)
            
            if not is_valid:
                return {'success': False, 'message': message}
            
            transaction_id = MockPaymentGateway.generate_transaction_id()
            order = Order.query.get_or_404(order_id)
            
            # MOCK: 70% success
            is_success = random.random() < 0.7
            
            payment = Payment(
                order_id=order_id,
                transaction_id=transaction_id,
                amount=amount,
                payment_status='success' if is_success else 'failed',
                card_last_4=card_number[-4:],
                processed_at=datetime.utcnow()
            )
            
            db.session.add(payment)
            
            if is_success:
                order.payment_status = 'paid'
                order.order_status = 'payment_confirmed'
                order.transaction_id = transaction_id
                
                for item in order.items:
                    item.product.quantity -= item.quantity
                
                print(f"[MOCK PAYMENT] SUCCESS - Transaction: {transaction_id}")
            else:
                order.payment_status = 'failed'
                order.order_status = 'payment_failed'
                print(f"[MOCK PAYMENT] FAILED - Transaction: {transaction_id}")
            
            db.session.commit()
            
            return {
                'success': is_success,
                'transaction_id': transaction_id,
                'message': 'Payment successful!' if is_success else 'Payment failed. Retry?',
                'can_retry': True
            }
        
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
