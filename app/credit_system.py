from app import db
from app.models import RetailerCredit

class CreditSystem:
    """
    MOCK CREDIT SYSTEM - Uses FORMULA
    NOT REAL CALCULATIONS
    """
    
    @staticmethod
    def calculate_credit_score(retailer_id):
        """
        Calculate credit score using formula
        """
        try:
            credit = RetailerCredit.query.filter_by(retailer_id=retailer_id).first()
            
            if not credit:
                return {
                    'score': 500,
                    'tier': 'silver',
                    'tier_name': 'வெள்ளி (Silver)',
                    'limit': 50000,
                    'available': 50000,
                    'utilized': 0
                }
            
            orders = credit.total_orders if hasattr(credit, 'total_orders') and credit.total_orders else 0
            successful = credit.successful_orders if hasattr(credit, 'successful_orders') and credit.successful_orders else 0
            
            # MOCK FORMULA
            purchase_score = min(orders * 10, 250)
            frequency_score = min(successful * 5, 200)
            punctuality_score = 200
            completion_score = min((successful / max(orders, 1)) * 150, 150)
            base_score = 150
            
            total_score = int(purchase_score + frequency_score + punctuality_score + completion_score + base_score)
            total_score = min(total_score, 1000)
        except Exception as e:
            print(f"⚠️ Credit calculation error: {e}")
            # Return default values
            total_score = 500
        
        if total_score >= 751:
            tier = 'platinum'
            tier_name = 'வைரம் (Platinum)'
        elif total_score >= 501:
            tier = 'gold'
            tier_name = 'தங்கம் (Gold)'
        elif total_score >= 251:
            tier = 'silver'
            tier_name = 'வெள்ளி (Silver)'
        else:
            tier = 'bronze'
            tier_name = 'வெண்கல (Bronze)'
        
        # Update credit object if it exists
        try:
            if credit:
                credit.credit_score = total_score
                credit.credit_tier = tier
                db.session.commit()
        except Exception as e:
            print(f"⚠️ Credit update error: {e}")
            db.session.rollback()
        
        return {
            'score': total_score,
            'tier': tier,
            'tier_name': tier_name,
            'limit': 50000,
            'available': 50000,
            'utilized': 0
        }
    
    @staticmethod
    def get_tier_benefits(tier):
        """Get tier benefits"""
        
        benefits = {
            'bronze': {'discount': 0, 'early_access': 0, 'payment_terms': 'Prepay'},
            'silver': {'discount': 5, 'early_access': 5, 'payment_terms': 'Net 7'},
            'gold': {'discount': 10, 'early_access': 15, 'payment_terms': 'Net 15/30'},
            'platinum': {'discount': 15, 'early_access': 30, 'payment_terms': 'Net 30/60'}
        }
        
        return benefits.get(tier, benefits['bronze'])
