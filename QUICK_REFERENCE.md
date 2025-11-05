# ⚡ Quick Reference Card - FreshConnect

## 🚀 Quick Start (3 Commands)

```bash
pip install -r requirements.txt
python seed_data.py
python run.py
```
Then open: **http://localhost:5000**

---

## 🔑 Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@freshconnect.com | admin123 |
| Vendor | vendor1@freshconnect.com | vendor123 |
| Retailer | retailer1@freshconnect.com | retailer123 |
| Driver | driver1@freshconnect.com | driver123 |

---

## 💳 Mock Payment Card

```
Card Number: 1234567890123456 (any 16 digits)
Expiry: 12/25 (any future date)
CVV: 123 (any 3 digits)
Success Rate: 70% (for testing)
```

---

## 📁 Essential Files

| File | Purpose |
|------|---------|
| `run.py` | Start server |
| `seed_data.py` | Initialize database |
| `config.py` | Configuration |
| `.env` | API keys (create this!) |
| `app/models.py` | Database models |
| `app/routes/` | All routes |

---

## 🌐 Important URLs

```
Homepage:           http://localhost:5000
Admin Dashboard:    /admin/dashboard
Vendor Dashboard:   /vendor/dashboard
Retailer Browse:    /retailer/browse
Driver Assignments: /driver/assignments
Login:             /auth/login
Register:          /auth/register
```

---

## 🗄️ Database Tables

1. **users** - All user accounts
2. **products** - Product listings
3. **orders** - Order records
4. **order_items** - Items in orders
5. **payments** - Payment transactions
6. **drivers** - Driver profiles
7. **driver_assignments** - Delivery assignments
8. **retailer_credits** - Credit scores
9. **chat_logs** - AI chat history

---

## ✅ Real vs Mock Features

### ✅ REAL (Working)
- Google Gemini AI chatbot
- User authentication
- Database operations
- Order management
- Shopping cart
- MOQ validation

### 🔶 MOCK (Simulated)
- Payment gateway
- SMS notifications  
- GPS tracking
- Email service

---

## 🏅 Credit Score Tiers

| Tier | Score | Discount | Benefits |
|------|-------|----------|----------|
| 🥉 Bronze | 0-250 | 0% | Prepay |
| 🥈 Silver | 251-500 | 5% | Net 7 |
| 🥇 Gold | 501-750 | 10% | Net 15/30 |
| 💎 Platinum | 751-1000 | 15% | Net 30/60 |

---

## 🎯 Demo Flow (5 minutes)

1. **Login as Vendor** → Add Product
2. **Login as Retailer** → Browse → Add to Cart
3. **Checkout** → Enter Address
4. **Payment** → Use mock card
5. **Track Order** → View mock GPS
6. **Login as Driver** → Mark Delivered

---

## 🔧 Common Commands

```bash
# Start virtual environment
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Seed sample data
python seed_data.py

# Run server
python run.py

# Reset database
rm marketplace.db              # Mac/Linux
del marketplace.db             # Windows
python seed_data.py
```

---

## 🐛 Quick Fixes

| Problem | Solution |
|---------|----------|
| Module not found | `pip install -r requirements.txt` |
| Database error | `python seed_data.py` |
| Port in use | Change port in `run.py` |
| API key error | Add key to `.env` file |
| Can't login | Check TEST_CREDENTIALS.md |

---

## 📂 Project Structure

```
freshconnect-app/
├── app/
│   ├── models.py          # 9 database models
│   ├── routes/            # 8 route blueprints
│   ├── templates/         # 25+ HTML files
│   ├── static/            # CSS, JS, images
│   ├── ai_service.py      # Gemini (REAL)
│   ├── payment_service.py # Payment (MOCK)
│   ├── driver_service.py  # GPS (MOCK)
│   └── credit_system.py   # Credit (MOCK)
├── config.py
├── run.py
├── seed_data.py
└── README.md
```

---

## 🎓 For Presentation

**Key Points to Mention:**
1. Full-stack Flask application
2. 4 user roles with distinct workflows
3. Real AI integration (Gemini)
4. Mock services for safe demo
5. Mobile responsive design
6. Professional UI with Bootstrap 5

**Be Ready to Show:**
- Complete purchase flow
- All user dashboards
- Credit score system
- Order tracking
- Clean code structure

---

## 🔗 External Resources

- **Gemini API:** https://makersuite.google.com/app/apikey
- **Flask Docs:** https://flask.palletsprojects.com/
- **Bootstrap 5:** https://getbootstrap.com/docs/5.3/
- **SQLAlchemy:** https://docs.sqlalchemy.org/

---

## 📞 Need Help?

1. Check **TROUBLESHOOTING.md**
2. Review **README.md**
3. Check **SETUP_GUIDE.md**
4. Verify **PROJECT_CHECKLIST.md**

---

## ⚠️ Important Reminders

- ✅ Only Gemini API is REAL
- 🔶 All other APIs are MOCKED
- 🔑 Add GEMINI_API_KEY to `.env`
- 📱 Test on mobile view
- 🎯 70% payment success rate is normal
- 💾 Backup database before major changes

---

## 🎯 Success Criteria

Your project is ready when:
- ✅ All 4 user roles work
- ✅ Complete purchase flow works
- ✅ Order tracking displays
- ✅ Credit score updates
- ✅ AI chatbot responds
- ✅ Mobile responsive
- ✅ No console errors
- ✅ Demo flows smoothly

---

## 📊 Tech Stack Summary

**Backend:** Flask + SQLAlchemy + SQLite  
**Frontend:** Bootstrap 5 + JavaScript  
**API:** Google Gemini (Real)  
**Auth:** Flask-Login  
**Template:** Jinja2  

---

## 🏆 Features Count

- **9** Database models
- **8** Route blueprints
- **25+** HTML templates
- **4** User roles
- **1** Real API (Gemini)
- **4** Mock services
- **200+** Checklist items

---

## 📅 Typical Timeline

- ⏰ **Setup:** 10 minutes
- ⏰ **Test All Features:** 30 minutes
- ⏰ **Review Code:** 20 minutes
- ⏰ **Prepare Demo:** 30 minutes
- ⏰ **Practice Presentation:** 15 minutes

**Total:** ~2 hours to be fully ready

---

## 🎬 One-Line Pitch

> "FreshConnect is a B2B marketplace connecting vendors and retailers directly, featuring AI assistance, credit scoring, and complete order management - built with Flask, Bootstrap, and Google Gemini API."

---

**Print this for quick reference during presentation! 📄**

**You've got this! 💪 Good luck! 🌟**
