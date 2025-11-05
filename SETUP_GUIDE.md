# 🚀 Quick Setup Guide - FreshConnect

## Step-by-Step Setup Instructions

### 1️⃣ Install Python Dependencies

Open terminal in the `freshconnect-app` folder and run:

```bash
pip install -r requirements.txt
```

### 2️⃣ Configure Environment Variables

Create a `.env` file in the root directory:

```bash
# Copy from example
copy .env.example .env
```

Edit the `.env` file and add your **Gemini API Key**:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

**Get Gemini API Key:**
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Create API key
4. Copy and paste into `.env` file

### 3️⃣ Initialize Database

```bash
python init_db.py
```

You should see: ✅ Database initialized successfully!

### 4️⃣ Seed Sample Data

```bash
python seed_data.py
```

This creates test users and products.

### 5️⃣ Run the Application

```bash
python run.py
```

You should see:
```
* Running on http://0.0.0.0:5000
* Running on http://127.0.0.1:5000
```

### 6️⃣ Open in Browser

Open your browser and visit:
```
http://localhost:5000
```

---

## 🔑 Test Login Credentials

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@freshconnect.com | admin123 |
| **Vendor** | vendor1@freshconnect.com | vendor123 |
| **Retailer** | retailer1@freshconnect.com | retailer123 |
| **Driver** | driver1@freshconnect.com | driver123 |

---

## 🧪 Testing the Application

### As Retailer:
1. Login with retailer1@freshconnect.com
2. Browse products
3. Add items to cart (respects MOQ)
4. Checkout and create order
5. Make payment (use any 16-digit number like: 1234567890123456)
6. Track order delivery

### As Vendor:
1. Login with vendor1@freshconnect.com
2. Add new products
3. View orders
4. Manage inventory

### As Driver:
1. Login with driver1@freshconnect.com
2. View assigned deliveries
3. Mark as picked up
4. Mark as delivered

### As Admin:
1. Login with admin@freshconnect.com
2. View all users
3. Monitor all orders
4. Check system stats

---

## ⚠️ Common Issues

### Issue: "Module not found"
**Solution:** Install requirements
```bash
pip install -r requirements.txt
```

### Issue: "GEMINI_API_KEY not set"
**Solution:** Add API key to `.env` file
```env
GEMINI_API_KEY=your_key_here
```

### Issue: "Port already in use"
**Solution:** Change port in `run.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Issue: Database error
**Solution:** Re-initialize database
```bash
python init_db.py
python seed_data.py
```

---

## 📋 Project Features Checklist

✅ **Real Features:**
- User authentication
- Product management
- Shopping cart
- Order system
- Gemini AI chatbot

🔶 **Mock Features (Simulated):**
- Payment gateway (70% success rate)
- SMS notifications (console logs)
- GPS tracking (random coordinates)
- Email service (console logs)

---

## 🎯 Demo Flow

1. **Register** as Retailer
2. **Browse** products from vendors
3. **Add to Cart** (test MOQ validation)
4. **Checkout** and enter address
5. **Pay** with mock card (any 16 digits)
6. **Track** delivery (mock GPS)
7. **Check** credit score dashboard

---

## 📞 Need Help?

- Check `README.md` for detailed documentation
- Review code comments for implementation details
- All mock services are clearly labeled

---

**Remember:** Only Gemini API is REAL. All other features are MOCKED for college project demonstration! 🎓

**Good luck with your project! 🌱**
