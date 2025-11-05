# 🔑 Test Credentials - FreshConnect

## Login Credentials

After running `seed_data.py`, use these credentials to test different user roles:

---

### 👨‍💼 Admin Account

**Email:** `admin@freshconnect.com`  
**Password:** `admin123`

**Access:**
- View all users
- Monitor all orders
- System statistics
- Full system access

---

### 🏪 Vendor Account (Seller)

**Email:** `vendor1@freshconnect.com`  
**Password:** `vendor123`

**Alternative Accounts:**
- `vendor2@freshconnect.com` / `vendor123`
- `vendor3@freshconnect.com` / `vendor123`

**Access:**
- Add/manage products
- Set MOQ (Minimum Order Quantity)
- View orders
- Manage inventory

---

### 🛒 Retailer Account (Buyer)

**Email:** `retailer1@freshconnect.com`  
**Password:** `retailer123`

**Alternative Accounts:**
- `retailer2@freshconnect.com` / `retailer123`
- `retailer3@freshconnect.com` / `retailer123`
- `retailer4@freshconnect.com` / `retailer123`
- `retailer5@freshconnect.com` / `retailer123`

**Access:**
- Browse products
- Shopping cart
- Place orders
- Track deliveries
- Credit score dashboard

---

### 🚚 Driver Account (Delivery)

**Email:** `driver1@freshconnect.com`  
**Password:** `driver123`

**Alternative Accounts:**
- `driver2@freshconnect.com` / `driver123`
- `driver3@freshconnect.com` / `driver123`

**Access:**
- View delivery assignments
- Mark pickup/delivery
- Track earnings
- Manage vehicle details

---

## 💳 Mock Payment Details

For testing payment checkout (Mock Gateway):

**Card Number:** Any 16 digits (e.g., `1234567890123456`)  
**Expiry:** Any future date in MM/YY format (e.g., `12/25`)  
**CVV:** Any 3 digits (e.g., `123`)

**Note:** Payment has 70% success rate for testing both success and failure scenarios.

---

## 🧪 Test Scenarios

### Scenario 1: Complete Purchase Flow (Retailer)
1. Login as `retailer1@freshconnect.com`
2. Browse products
3. Add items (min 50kg for vegetables due to MOQ)
4. Go to cart
5. Checkout
6. Enter delivery address
7. Pay with mock card: `1234567890123456`
8. Track order

### Scenario 2: Product Management (Vendor)
1. Login as `vendor1@freshconnect.com`
2. Click "Add Product"
3. Fill product details
4. Set MOQ requirement
5. View in products list

### Scenario 3: Delivery (Driver)
1. Login as `driver1@freshconnect.com`
2. View assignments
3. Click on delivery
4. Mark as "Picked Up"
5. Mark as "Delivered"

### Scenario 4: System Monitoring (Admin)
1. Login as `admin@freshconnect.com`
2. View all users
3. Monitor all orders
4. Check statistics

---

## 📊 Sample Products Available

After seeding, you'll have:
- Fresh Tomato (Vegetables) - ₹25/kg
- Red Onion (Vegetables) - ₹45/kg
- Carrot (Vegetables) - ₹30/kg
- Fresh Rose (Flowers) - ₹200/bunch
- Jasmine (Flowers) - ₹150/bunch
- Fresh Banana (Fruits) - ₹40/dozen
- And more...

**Note:** Vegetables have MOQ of 50kg minimum.

---

## 🏅 Credit Score Testing

### Initial Credit Score
All retailers start with:
- Score: 150
- Tier: Bronze (வெண்கல)

### Increase Credit Score
Complete orders to increase score:
- Each order: +10 points
- Successful delivery: +5 points
- Tier upgrades at: 251 (Silver), 501 (Gold), 751 (Platinum)

---

## 🤖 AI Chatbot Testing

The Gemini AI chatbot responds to queries in Tamil + English mix.

**Try asking:**
- "How do I place an order?"
- "எனக்கு எப்படி order போடுவது?"
- "What products are available?"
- "Credit score எப்படி increase பண்ணுவது?"

**Note:** Requires valid GEMINI_API_KEY in .env file

---

## ⚠️ Important Notes

### Real Services
- ✅ Gemini AI Chatbot (requires API key)
- ✅ Database operations
- ✅ User authentication

### Mock Services (Simulated)
- 🔶 Payment Gateway (70% success rate)
- 🔶 SMS Notifications (console logs only)
- 🔶 GPS Tracking (random coordinates)
- 🔶 Email Service (console logs only)

All mock services are clearly labeled in the UI and code.

---

## 🔄 Reset Database

If you want to reset all data:

```bash
# Delete database
rm marketplace.db  # Mac/Linux
del marketplace.db  # Windows

# Re-seed data
python seed_data.py
```

---

## 📱 Mobile Testing

Test responsive design on:
- Desktop: Chrome/Firefox/Edge
- Mobile: Chrome DevTools → Mobile View
- Tablet: iPad dimensions

---

**Happy Testing! 🎉**
