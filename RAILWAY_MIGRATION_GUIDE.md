# Railway Database Migration Guide
## Vendor Comparison System Setup

---

## 📋 **Overview**

This guide shows you how to update the Railway PostgreSQL database with the new Vendor Comparison System tables.

---

## 🎯 **Option 1: Python Migration Script (RECOMMENDED)**

### **Step-by-Step:**

#### **1. Access Railway Shell**

**Method A: Railway Dashboard**
```
1. Go to: https://railway.app
2. Login
3. Click your "FreshConnect" project
4. Click "Settings" → "Open Shell"
   OR
   Click "Deployments" → Latest deployment → "Open Shell"
```

**Method B: Railway CLI** (if installed)
```bash
railway login
railway link
railway shell
```

#### **2. Run Migration Script**

In the Railway shell, run:

```python
# Import and run migration
exec(open('migrate_vendor_comparison.py').read())
```

OR if that doesn't work:

```python
from migrate_vendor_comparison import run_migration
run_migration()
```

#### **3. Expected Output**

You should see:
```
============================================================
🚀 VENDOR COMPARISON SYSTEM - DATABASE MIGRATION
============================================================

📋 Step 1: Creating database tables...
   ✅ All tables created successfully!

📋 Step 2: Updating existing products...
   ✅ Updated 45 products with default values

📋 Step 3: Creating vendor rating caches...
   Found 10 vendors
   ✅ Created 10 new vendor rating caches
   ✅ Updated ratings from existing reviews

📋 Step 4: Creating vendor delivery metrics...
   ✅ Created 10 new vendor delivery metrics

📋 Step 5: Verifying migration...
   ✅ Vendors in system: 10
   ✅ Vendor rating caches: 10
   ✅ Vendor delivery metrics: 10
   
   🎉 All vendors have caches and metrics!

📋 Step 6: Testing comparison service...
   ✅ Search test: Found 3 vendors for 'tomato'
   ✅ Recommendation test: Recommended vendor 5

============================================================
✅ MIGRATION COMPLETE!
============================================================

📊 Summary:
   • Database tables: Created/Updated
   • Vendor caches: 10
   • Delivery metrics: 10
   • Products updated: Yes

🎯 Next Steps:
   1. Test API endpoints
   2. Verify data in Railway dashboard
   3. Test frontend integration

============================================================
```

---

## 🎯 **Option 2: SQL Migration (Alternative)**

If Python script doesn't work, use SQL directly.

#### **1. Access Railway PostgreSQL Database**

**Method A: Railway Dashboard**
```
1. Go to Railway project
2. Click "PostgreSQL" service
3. Click "Data" tab
4. Click "Query" button
5. Paste SQL and run
```

**Method B: psql Client**
```bash
# Get database URL from Railway:
# Project → PostgreSQL → Connect → Copy DATABASE_URL

psql <your-database-url>
```

#### **2. Run SQL Migration**

Copy and paste the entire contents of `database_migration_vendor_comparison.sql`:

```sql
-- Run the SQL file
\i database_migration_vendor_comparison.sql
```

OR copy-paste each section manually.

#### **3. Verify Tables Created**

```sql
-- Check tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('vendor_ratings_cache', 'vendor_delivery_metrics', 'product_comparison');

-- Should return 3 rows

-- Check data
SELECT COUNT(*) FROM vendor_ratings_cache;
SELECT COUNT(*) FROM vendor_delivery_metrics;
```

---

## 🎯 **Option 3: Flask Shell (Manual)**

#### **1. Open Railway Python Shell**

```bash
railway shell
```

#### **2. Run Commands Manually**

```python
from app import create_app, db
from app.models import User, VendorRatingsCache, VendorDeliveryMetrics
from app.comparison_service import ProductComparisonService

# Create app context
app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    print("✅ Tables created")
    
    # Get all vendors
    vendors = User.query.filter_by(user_type='vendor').all()
    print(f"Found {len(vendors)} vendors")
    
    # Create caches for each vendor
    for vendor in vendors:
        # Create rating cache
        cache = VendorRatingsCache.query.filter_by(vendor_id=vendor.id).first()
        if not cache:
            cache = VendorRatingsCache(
                vendor_id=vendor.id,
                avg_quality_rating=4.0,
                avg_punctuality_rating=4.0,
                avg_communication_rating=4.0,
                overall_rating=4.0,
                total_reviews=0,
                success_rate=95.0,
                on_time_rate=90.0
            )
            db.session.add(cache)
        
        # Create delivery metrics
        metrics = VendorDeliveryMetrics.query.filter_by(vendor_id=vendor.id).first()
        if not metrics:
            metrics = VendorDeliveryMetrics(
                vendor_id=vendor.id,
                avg_delivery_time=240,
                min_delivery_time=120,
                max_delivery_time=360
            )
            db.session.add(metrics)
        
        # Update cache with real data
        ProductComparisonService.update_vendor_ratings_cache(vendor.id)
    
    # Commit all changes
    db.session.commit()
    print("✅ All vendor caches created!")
    
    # Verify
    cache_count = VendorRatingsCache.query.count()
    metrics_count = VendorDeliveryMetrics.query.count()
    print(f"✅ Created {cache_count} caches and {metrics_count} metrics")
```

---

## 🧪 **Verification & Testing**

### **1. Verify Tables Exist**

```python
from app import create_app, db
from app.models import VendorRatingsCache, VendorDeliveryMetrics, ProductComparison

app = create_app()
with app.app_context():
    print(f"Vendor caches: {VendorRatingsCache.query.count()}")
    print(f"Delivery metrics: {VendorDeliveryMetrics.query.count()}")
    print(f"Comparisons logged: {ProductComparison.query.count()}")
```

### **2. Test API Endpoints**

```bash
# Test search endpoint
curl -X POST https://your-app.up.railway.app/api/comparison/products/search \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "tomato",
    "sort_by": "value"
  }'

# Expected: JSON with vendors list

# Test vendor profile
curl https://your-app.up.railway.app/api/comparison/vendors/1/profile

# Expected: JSON with vendor details

# Test recommendation
curl -X POST https://your-app.up.railway.app/api/comparison/recommendations/personalized \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Tomato",
    "vendors_available": [1, 2, 3]
  }'

# Expected: JSON with recommendation
```

### **3. Check Database in Railway Dashboard**

```
1. Go to Railway project
2. Click "PostgreSQL" service  
3. Click "Data" tab
4. Browse tables:
   - vendor_ratings_cache
   - vendor_delivery_metrics
   - product_comparison
5. Verify data exists
```

---

## ❌ **Troubleshooting**

### **Problem: "Table already exists"**

**Solution:** This is normal if tables were auto-created. Skip to seeding data:

```python
from app.comparison_service import ProductComparisonService
from app.models import User

vendors = User.query.filter_by(user_type='vendor').all()
for v in vendors:
    ProductComparisonService.update_vendor_ratings_cache(v.id)
```

### **Problem: "ImportError: cannot import ProductComparisonService"**

**Solution:** Code may not be deployed yet. Wait for Railway deployment to complete (check deployment logs).

### **Problem: "No module named 'comparison_service'"**

**Solution:** 
```bash
# Restart Railway deployment
railway up
```

### **Problem: "OperationalError: no such table"**

**Solution:** Tables not created. Run:
```python
from app import db
db.create_all()
```

### **Problem: "UNIQUE constraint failed: vendor_ratings_cache.vendor_id"**

**Solution:** Cache already exists. Use `ON CONFLICT DO NOTHING` or query first:
```python
existing = VendorRatingsCache.query.filter_by(vendor_id=vendor_id).first()
if not existing:
    # Create new
```

---

## 📊 **Migration Checklist**

Use this to track your progress:

### **Pre-Migration:**
- [ ] Code deployed to Railway (commit 738c282)
- [ ] Railway build completed successfully
- [ ] Can access Railway shell/PostgreSQL

### **Migration Steps:**
- [ ] Run migration script OR SQL
- [ ] Verify 3 new tables created
- [ ] Seed vendor rating caches
- [ ] Seed vendor delivery metrics
- [ ] Update existing products

### **Post-Migration:**
- [ ] Test search API endpoint
- [ ] Test vendor profile API
- [ ] Test recommendation API
- [ ] Verify data in Railway dashboard
- [ ] Check deployment logs for errors

### **Final Verification:**
- [ ] All vendors have rating caches
- [ ] All vendors have delivery metrics
- [ ] Products have comparison fields
- [ ] API endpoints return data
- [ ] No errors in logs

---

## 🎯 **Quick Start (5 Minutes)**

**Fastest way to migrate:**

```bash
# 1. Open Railway shell (railway.app → project → shell)

# 2. Run this one command:
python migrate_vendor_comparison.py

# 3. Verify it worked:
curl -X POST https://your-app.up.railway.app/api/comparison/products/search \
  -H "Content-Type: application/json" \
  -d '{"product_name": "tomato", "sort_by": "value"}'

# 4. If you see JSON response with vendors → SUCCESS! ✅
```

---

## 📞 **Need Help?**

### **Check These First:**

1. **Railway Deployment Logs**
   ```
   Railway Dashboard → Deployments → Latest → View Logs
   Look for errors or "ImportError"
   ```

2. **Database Connection**
   ```python
   from app import db
   print(db.engine.url)  # Should show PostgreSQL URL
   ```

3. **Tables Created?**
   ```sql
   SELECT table_name FROM information_schema.tables 
   WHERE table_schema = 'public';
   ```

---

## ✅ **Success Indicators**

You know migration worked when:

1. ✅ No errors in Railway logs
2. ✅ `VendorRatingsCache.query.count()` > 0
3. ✅ `VendorDeliveryMetrics.query.count()` > 0
4. ✅ API returns vendor comparison data
5. ✅ Railway dashboard shows new tables

---

## 🎉 **After Migration**

Your system now has:

- ✅ **Fast vendor comparison** (cached ratings)
- ✅ **Delivery metrics tracking**
- ✅ **Comparison analytics** (logged actions)
- ✅ **AI recommendations** (personalized)
- ✅ **Value scoring algorithm** (quality/price/speed)

**Next:** Test the API endpoints and integrate with frontend!

---

## 📁 **Files Provided**

1. **`migrate_vendor_comparison.py`** - Python migration script (RECOMMENDED)
2. **`database_migration_vendor_comparison.sql`** - SQL migration (Alternative)
3. **`RAILWAY_MIGRATION_GUIDE.md`** - This guide
4. **`VENDOR_COMPARISON_SYSTEM.md`** - Full documentation

**All files are in your project root directory.** ✅
