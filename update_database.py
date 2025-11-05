"""
Database Update Script
Adds new columns to existing tables without losing data
"""

import sqlite3
import os

# Path to database
DB_PATH = 'instance/marketplace.db'

def update_database():
    """Add new columns to existing tables"""
    
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database not found at {DB_PATH}")
        return
    
    print(f"[*] Updating database: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Add rating columns to users table
        print("\n[1] Adding rating columns to users table...")
        
        columns_to_add = [
            ("average_rating", "REAL DEFAULT 0.0"),
            ("total_reviews", "INTEGER DEFAULT 0"),
            ("rating_quality_avg", "REAL DEFAULT 0.0"),
            ("rating_delay_avg", "REAL DEFAULT 0.0"),
            ("rating_communication_avg", "REAL DEFAULT 0.0"),
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                print(f"   [OK] Added column: {col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"   [SKIP] Column already exists: {col_name}")
                else:
                    print(f"   [WARN] Error adding {col_name}: {e}")
        
        # Add tracking columns to orders table
        print("\n[2] Adding tracking columns to orders table...")
        
        tracking_columns = [
            ("payment_confirmed_at", "DATETIME"),
            ("shipped_in_truck_at", "DATETIME"),
            ("ready_for_delivery_at", "DATETIME"),
            ("delivered_at", "DATETIME"),
        ]
        
        for col_name, col_type in tracking_columns:
            try:
                cursor.execute(f"ALTER TABLE orders ADD COLUMN {col_name} {col_type}")
                print(f"   [OK] Added column: {col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"   [SKIP] Column already exists: {col_name}")
                else:
                    print(f"   [WARN] Error adding {col_name}: {e}")
        
        # Create new tables
        print("\n[3] Creating new tables...")
        
        # AdminGeneratedStock table
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_generated_stock (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_generated_code VARCHAR(50) UNIQUE NOT NULL,
                    product_name VARCHAR(100) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    weight REAL NOT NULL,
                    unit VARCHAR(20) DEFAULT 'kg',
                    price REAL NOT NULL,
                    expiry_date DATE,
                    barcode_image_path VARCHAR(255),
                    qr_code_image_path VARCHAR(255),
                    created_by_admin_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_claimed_by_vendor BOOLEAN DEFAULT 0,
                    claimed_by_vendor_id INTEGER,
                    claimed_at DATETIME,
                    product_id INTEGER,
                    FOREIGN KEY (created_by_admin_id) REFERENCES users(id),
                    FOREIGN KEY (claimed_by_vendor_id) REFERENCES users(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)
            print("   [OK] Created table: admin_generated_stock")
        except sqlite3.OperationalError as e:
            print(f"   [SKIP] Table already exists: admin_generated_stock")
        
        # OrderStatusLog table
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_status_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    status_from VARCHAR(50),
                    status_to VARCHAR(50) NOT NULL,
                    changed_by_id INTEGER NOT NULL,
                    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (order_id) REFERENCES orders(id),
                    FOREIGN KEY (changed_by_id) REFERENCES users(id)
                )
            """)
            print("   [OK] Created table: order_status_log")
        except sqlite3.OperationalError as e:
            print(f"   [SKIP] Table already exists: order_status_log")
        
        # ProductReview table
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS product_reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    retailer_id INTEGER NOT NULL,
                    vendor_id INTEGER NOT NULL,
                    driver_id INTEGER,
                    rating_quality INTEGER,
                    rating_delay INTEGER,
                    rating_communication INTEGER,
                    driver_rating_handling INTEGER,
                    driver_rating_punctuality INTEGER,
                    driver_rating_communication INTEGER,
                    comment TEXT,
                    driver_comment TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    edited_at DATETIME,
                    FOREIGN KEY (order_id) REFERENCES orders(id),
                    FOREIGN KEY (product_id) REFERENCES products(id),
                    FOREIGN KEY (retailer_id) REFERENCES users(id),
                    FOREIGN KEY (vendor_id) REFERENCES users(id),
                    FOREIGN KEY (driver_id) REFERENCES users(id)
                )
            """)
            print("   [OK] Created table: product_reviews")
        except sqlite3.OperationalError as e:
            print(f"   [SKIP] Table already exists: product_reviews")
        
        # UserReport table
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_from_id INTEGER NOT NULL,
                    report_against_id INTEGER NOT NULL,
                    report_type VARCHAR(50) NOT NULL,
                    report_text TEXT NOT NULL,
                    evidence_attachment VARCHAR(255),
                    status VARCHAR(50) DEFAULT 'pending',
                    admin_response TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    resolved_at DATETIME,
                    FOREIGN KEY (report_from_id) REFERENCES users(id),
                    FOREIGN KEY (report_against_id) REFERENCES users(id)
                )
            """)
            print("   [OK] Created table: user_reports")
        except sqlite3.OperationalError as e:
            print(f"   [SKIP] Table already exists: user_reports")
        
        # Commit changes
        conn.commit()
        print("\n[SUCCESS] Database update completed successfully!")
        
        # Show table info
        print("\n[INFO] Current tables in database:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        for table in tables:
            print(f"   • {table[0]}")
        
    except Exception as e:
        print(f"\n[ERROR] Error updating database: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("  FreshConnect Database Update Script")
    print("=" * 60)
    update_database()
    print("\n" + "=" * 60)
    print("  Done! You can now restart your Flask app.")
    print("=" * 60)
