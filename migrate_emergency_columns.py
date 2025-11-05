"""
Database Migration: Add Emergency Marketplace Columns

This script adds the new emergency marketplace columns to the existing products table
"""

import sqlite3
import os

def migrate_database():
    """Add emergency marketplace columns to products table"""
    
    db_path = 'instance/marketplace.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        print("Run 'python run.py' first to create the database")
        return False
    
    print("="*60)
    print("Database Migration: Emergency Marketplace Columns")
    print("="*60)
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"\n✓ Connected to {db_path}")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(products)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        print(f"\nExisting columns in products table: {len(existing_columns)}")
        
        # Columns to add
        new_columns = [
            ('emergency_discount', 'REAL DEFAULT 0'),
            ('original_price_backup', 'REAL'),
            ('emergency_marked_at', 'DATETIME'),
            ('days_until_expiry', 'INTEGER')
        ]
        
        added_count = 0
        
        for column_name, column_type in new_columns:
            if column_name in existing_columns:
                print(f"  ⏭️  Column '{column_name}' already exists, skipping...")
            else:
                try:
                    sql = f"ALTER TABLE products ADD COLUMN {column_name} {column_type}"
                    cursor.execute(sql)
                    print(f"  ✓ Added column: {column_name} ({column_type})")
                    added_count += 1
                except sqlite3.OperationalError as e:
                    print(f"  ⚠️  Error adding {column_name}: {e}")
        
        # Note: is_emergency column already exists in the original schema
        # Just verify it exists
        if 'is_emergency' in existing_columns:
            print(f"  ✓ Column 'is_emergency' already exists")
        else:
            cursor.execute("ALTER TABLE products ADD COLUMN is_emergency BOOLEAN DEFAULT 0")
            print(f"  ✓ Added column: is_emergency (BOOLEAN)")
            added_count += 1
        
        # Create emergency_marketplace_metrics table if it doesn't exist
        print("\nCreating emergency_marketplace_metrics table...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emergency_marketplace_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE NOT NULL,
                
                total_emergency_products INTEGER DEFAULT 0,
                total_emergency_items_sold INTEGER DEFAULT 0,
                
                original_value_at_risk REAL DEFAULT 0,
                emergency_sale_value REAL DEFAULT 0,
                total_discount_given REAL DEFAULT 0,
                vendor_recovery_value REAL DEFAULT 0,
                
                estimated_waste_prevented_kg REAL DEFAULT 0,
                
                unique_vendors INTEGER DEFAULT 0,
                unique_retailers INTEGER DEFAULT 0,
                
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        print("  ✓ Created emergency_marketplace_metrics table")
        
        # Commit changes
        conn.commit()
        print(f"\n✓ Migration complete! Added {added_count} new columns")
        
        # Verify
        cursor.execute("PRAGMA table_info(products)")
        all_columns = [row[1] for row in cursor.fetchall()]
        
        print(f"\nTotal columns in products table: {len(all_columns)}")
        print("\nEmergency marketplace columns:")
        emergency_cols = ['is_emergency', 'emergency_discount', 'original_price_backup', 
                         'emergency_marked_at', 'days_until_expiry']
        
        for col in emergency_cols:
            status = "✓" if col in all_columns else "❌"
            print(f"  {status} {col}")
        
        conn.close()
        
        print("\n" + "="*60)
        print("Migration Successful!")
        print("="*60)
        print("\nYou can now run: python init_emergency_marketplace.py")
        print("to create sample emergency products.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = migrate_database()
    
    if success:
        print("\n✅ Database ready for Emergency Marketplace!")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
