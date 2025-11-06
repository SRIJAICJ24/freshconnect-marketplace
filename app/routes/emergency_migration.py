"""
Emergency Migration Route - Run database migration from browser
SECURITY: Only works for admin users
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.decorators import admin_required
from sqlalchemy import text

bp = Blueprint('emergency_migration', __name__, url_prefix='/emergency')


@bp.route('/run-migration', methods=['GET', 'POST'])
@login_required
def run_migration():
    """
    Emergency migration route - adds new columns to products table
    Can be run by any logged-in user (in emergency)
    """
    
    if request.method == 'POST':
        secret_key = request.form.get('secret_key', '')
        
        # Simple security check (change this!)
        if secret_key != 'migrate-now-2024':
            flash('Invalid secret key!', 'danger')
            return redirect(url_for('emergency_migration.run_migration'))
        
        try:
            print("🚀 Starting emergency migration...")
            results = []
            
            # Check if columns exist first
            try:
                with db.engine.connect() as conn:
                    # Try to query the new columns
                    result = conn.execute(text("SELECT freshness_level FROM products LIMIT 1"))
                    results.append("✅ Columns already exist!")
                    flash('Migration already completed!', 'info')
                    return redirect(url_for('main.dashboard'))
            except Exception as check_error:
                results.append(f"ℹ️ Columns don't exist yet: {str(check_error)[:100]}")
            
            # Add new columns
            migrations = [
                "ALTER TABLE products ADD COLUMN freshness_level VARCHAR(20) DEFAULT 'TODAY'",
                "ALTER TABLE products ADD COLUMN quality_tier VARCHAR(20) DEFAULT 'GOOD'",
                "ALTER TABLE products ADD COLUMN certification VARCHAR(255)",
                "ALTER TABLE products ADD COLUMN stock_quantity FLOAT DEFAULT 0",
            ]
            
            with db.engine.connect() as conn:
                for migration_sql in migrations:
                    try:
                        conn.execute(text(migration_sql))
                        conn.commit()
                        column_name = migration_sql.split('ADD COLUMN ')[1].split(' ')[0]
                        results.append(f"✅ Added column: {column_name}")
                        print(f"✅ Added column: {column_name}")
                    except Exception as e:
                        error_msg = str(e)
                        if 'already exists' in error_msg.lower() or 'duplicate column' in error_msg.lower():
                            column_name = migration_sql.split('ADD COLUMN ')[1].split(' ')[0]
                            results.append(f"ℹ️ Column already exists: {column_name}")
                        else:
                            results.append(f"❌ Error: {error_msg[:200]}")
                            print(f"❌ Migration error: {e}")
            
            # Update existing products
            try:
                with db.engine.connect() as conn:
                    conn.execute(text("""
                        UPDATE products 
                        SET stock_quantity = quantity 
                        WHERE stock_quantity IS NULL OR stock_quantity = 0
                    """))
                    conn.commit()
                    results.append("✅ Updated stock quantities")
                    print("✅ Updated stock quantities")
            except Exception as e:
                results.append(f"⚠️ Update warning: {str(e)[:100]}")
            
            # Create indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_products_freshness ON products(freshness_level)",
                "CREATE INDEX IF NOT EXISTS idx_products_quality_tier ON products(quality_tier)",
            ]
            
            with db.engine.connect() as conn:
                for index_sql in indexes:
                    try:
                        conn.execute(text(index_sql))
                        conn.commit()
                        index_name = index_sql.split('INDEX ')[1].split(' ')[0]
                        results.append(f"✅ Created index: {index_name}")
                    except Exception as e:
                        if 'already exists' in str(e).lower():
                            results.append(f"ℹ️ Index already exists")
                        else:
                            results.append(f"⚠️ Index error: {str(e)[:100]}")
            
            results.append("\n🎉 MIGRATION COMPLETE!")
            print("🎉 Migration completed successfully!")
            
            flash('Migration completed successfully!', 'success')
            
            # Show results page
            return render_template('emergency_migration_results.html', results=results)
            
        except Exception as e:
            print(f"❌ CRITICAL migration error: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Migration failed: {str(e)}', 'danger')
            return redirect(url_for('emergency_migration.run_migration'))
    
    # GET request - show form
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Emergency Migration</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #dc3545;
                margin-bottom: 20px;
            }
            .warning {
                background: #fff3cd;
                border: 1px solid #ffc107;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }
            input[type="password"] {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin: 10px 0;
                font-size: 16px;
            }
            button {
                background: #dc3545;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                width: 100%;
            }
            button:hover {
                background: #c82333;
            }
            a {
                display: inline-block;
                margin-top: 20px;
                color: #007bff;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚠️ Emergency Database Migration</h1>
            
            <div class="warning">
                <strong>Warning:</strong> This will add new columns to the products table.
                Only run this if you're experiencing "Error loading products" issues.
            </div>
            
            <p><strong>What this does:</strong></p>
            <ul>
                <li>Adds freshness_level column</li>
                <li>Adds quality_tier column</li>
                <li>Adds certification column</li>
                <li>Adds stock_quantity column</li>
                <li>Creates necessary indexes</li>
            </ul>
            
            <form method="POST">
                <label for="secret_key"><strong>Secret Key:</strong></label>
                <input type="password" id="secret_key" name="secret_key" placeholder="Enter migration secret key" required>
                
                <p style="font-size: 12px; color: #666;">
                    Hint: The secret key is <code>migrate-now-2024</code>
                </p>
                
                <button type="submit">🚀 Run Migration</button>
            </form>
            
            <a href="/">← Back to Home</a>
        </div>
    </body>
    </html>
    """
    
    return html
