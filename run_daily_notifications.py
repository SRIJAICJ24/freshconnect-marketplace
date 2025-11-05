"""
Daily Notification Task
Run this script once per day to check for expiring products and send notifications

For production, set up as a cron job:
- Linux/Mac: Add to crontab
  0 9 * * * /path/to/python /path/to/run_daily_notifications.py
  
- Windows: Use Task Scheduler
  Daily at 9:00 AM
"""

from app import create_app
from app.notification_service import NotificationService

app = create_app()

with app.app_context():
    print("\n🚀 Starting Daily Notification Task...")
    print(f"Time: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run the notification check
    results = NotificationService.send_bulk_expiry_notifications()
    
    print(f"\n✅ Daily Notification Task Complete!")
    print(f"Results: {results}")
