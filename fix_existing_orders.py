"""
Quick script to update existing orders with payment confirmation timestamps
Run this once to fix orders created before the tracking fix
"""

from app import create_app, db
from app.models import Order, OrderStatusLog
from datetime import datetime

app = create_app()

with app.app_context():
    # Find all paid orders without payment_confirmed_at timestamp
    orders = Order.query.filter(
        Order.payment_status == 'paid',
        Order.payment_confirmed_at == None
    ).all()
    
    if not orders:
        print("✓ No orders need updating. All orders are properly configured!")
    else:
        print(f"Found {len(orders)} orders to update...")
        
        for order in orders:
            print(f"\nUpdating Order #{order.id}...")
            
            # Set payment confirmation timestamp
            order.payment_confirmed_at = order.created_at  # Use creation time
            
            # Update order status if still pending
            if order.order_status == 'pending':
                old_status = order.order_status
                order.order_status = 'payment_confirmed'
                
                # Create status log
                log = OrderStatusLog(
                    order_id=order.id,
                    status_from=old_status,
                    status_to='payment_confirmed',
                    changed_by_id=order.buyer_id,
                    changed_at=datetime.utcnow()
                )
                db.session.add(log)
                
                print(f"  ✓ Status updated: {old_status} → payment_confirmed")
            
            print(f"  ✓ Set payment_confirmed_at timestamp")
        
        db.session.commit()
        print(f"\n✓ Successfully updated {len(orders)} orders!")
        print("✓ Tracking timeline will now show progress for these orders")
        print("\nNext: Restart Flask and refresh the tracking page!")
