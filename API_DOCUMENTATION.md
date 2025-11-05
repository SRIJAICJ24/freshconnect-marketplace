# 🔌 API Documentation - FreshConnect

## Overview

FreshConnect provides several API endpoints for AJAX operations and external integrations.

---

## 🌐 Base URL

```
http://localhost:5000
```

---

## 🔐 Authentication

All API endpoints except `/api/chatbot` require user authentication via Flask-Login sessions.

**Authentication Method:** Cookie-based sessions

---

## 📡 API Endpoints

### 1. Validate MOQ (Minimum Order Quantity)

**Endpoint:** `/api/validate-moq/<product_id>`  
**Method:** `POST`  
**Authentication:** Not required  
**Description:** Validates if quantity meets product's MOQ requirement

#### Request

```json
POST /api/validate-moq/1
Content-Type: application/json

{
  "quantity": 45
}
```

#### Response (Success)

```json
{
  "valid": true
}
```

#### Response (Failed Validation)

```json
{
  "valid": false,
  "message": "Minimum: 50"
}
```

**Status Codes:**
- `200 OK` - Validation passed
- `400 Bad Request` - Validation failed
- `404 Not Found` - Product not found

---

### 2. Get Driver Location

**Endpoint:** `/api/driver-location/<assignment_id>`  
**Method:** `GET`  
**Authentication:** Not required  
**Description:** Returns mock GPS coordinates for driver

#### Request

```
GET /api/driver-location/1
```

#### Response (Success)

```json
{
  "driver": "Driver 1",
  "lat": 13.0835,
  "lng": 80.2714,
  "eta_minutes": 25,
  "mock": true
}
```

#### Response (Error)

```json
{
  "error": "Not found"
}
```

**Status Codes:**
- `200 OK` - Location retrieved
- `404 Not Found` - Assignment not found

**Note:** GPS coordinates are MOCK (random coordinates in Chennai area)

---

### 3. AI Chatbot

**Endpoint:** `/api/chatbot`  
**Method:** `POST`  
**Authentication:** Required (must be logged in)  
**Description:** Send message to Gemini AI chatbot and get response

#### Request

```json
POST /api/chatbot
Content-Type: application/json

{
  "message": "How do I place an order?"
}
```

#### Response (Success)

```json
{
  "response": "To place order, browse products, add to cart, and checkout. நீங்கள் products-ஐ cart-ல் add செய்து checkout செய்யலாம்."
}
```

#### Response (Error)

```json
{
  "error": "GEMINI_API_KEY not set in .env"
}
```

**Status Codes:**
- `200 OK` - Response generated
- `401 Unauthorized` - Not logged in
- `500 Internal Server Error` - API error

**Features:**
- ✅ Real Google Gemini API integration
- ✅ Bilingual responses (Tamil + English)
- ✅ Context-aware based on user role
- ✅ Conversation logged in database

---

### 4. Add to Cart

**Endpoint:** `/retailer/add-to-cart`  
**Method:** `POST`  
**Authentication:** Required (Retailer only)  
**Description:** Add product to shopping cart

#### Request

```json
POST /retailer/add-to-cart
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 50
}
```

#### Response (Success)

```json
{
  "success": true,
  "message": "Added to cart"
}
```

#### Response (MOQ Validation Failed)

```json
{
  "success": false,
  "message": "Minimum quantity: 50"
}
```

**Status Codes:**
- `200 OK` - Added successfully
- `400 Bad Request` - MOQ validation failed
- `401 Unauthorized` - Not logged in as retailer
- `404 Not Found` - Product not found

---

## 🔄 Web Routes (Non-API)

### Authentication Routes

#### Register
```
GET  /auth/register    - Show registration form
POST /auth/register    - Create new account
```

#### Login
```
GET  /auth/login       - Show login form
POST /auth/login       - Authenticate user
```

#### Logout
```
GET  /auth/logout      - Logout user
```

---

### Vendor Routes

All require vendor authentication.

```
GET  /vendor/dashboard     - Vendor dashboard
GET  /vendor/products      - List all products
GET  /vendor/add-product   - Show add product form
POST /vendor/add-product   - Create new product
GET  /vendor/orders        - List vendor orders
```

---

### Retailer Routes

All require retailer authentication.

```
GET  /retailer/dashboard               - Retailer dashboard
GET  /retailer/browse                  - Browse products
GET  /retailer/product/<id>            - Product details
GET  /retailer/cart                    - Shopping cart
GET  /retailer/checkout                - Checkout form
POST /retailer/checkout                - Create order
GET  /retailer/orders                  - Order history
GET  /retailer/orders/<id>/track       - Track order
GET  /retailer/credit                  - Credit dashboard
```

---

### Driver Routes

All require driver authentication.

```
GET  /driver/dashboard                     - Driver dashboard
GET  /driver/assignments                   - List assignments
GET  /driver/delivery/<id>                 - Delivery details
POST /driver/delivery/<id>/pickup          - Mark picked up
POST /driver/delivery/<id>/deliver         - Mark delivered
```

---

### Admin Routes

All require admin authentication.

```
GET  /admin/dashboard      - Admin dashboard
GET  /admin/users          - List all users
GET  /admin/orders         - List all orders
```

---

### Payment Routes

Require retailer authentication.

```
GET  /payment/checkout/<order_id>      - Payment form
POST /payment/checkout/<order_id>      - Process payment (mock)
GET  /payment/success/<order_id>       - Payment success page
```

---

## 📊 Response Formats

### Success Response

```json
{
  "success": true,
  "message": "Operation successful",
  "data": { }
}
```

### Error Response

```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error"
}
```

---

## 🔒 Security

### Session Management
- Cookies are HTTP-only
- Session timeout: 7 days
- Secure flag in production

### CSRF Protection
- Flask-WTF ready
- Token validation on forms

### Rate Limiting
- Not implemented (add in production)

---

## ⚠️ Mock Services

These endpoints use MOCK implementations:

1. **Payment Processing** (`/payment/checkout/<id>`)
   - Simulates card validation
   - 70% success rate
   - Generates mock transaction IDs

2. **Driver Location** (`/api/driver-location/<id>`)
   - Returns random coordinates
   - Chennai area (13.08, 80.27)
   - Mock ETA calculation

3. **SMS Notifications** (Internal)
   - Console logging only
   - No actual SMS sent

---

## 📝 Request Examples

### Using JavaScript Fetch

```javascript
// Add to Cart
fetch('/retailer/add-to-cart', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        product_id: 1,
        quantity: 50
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        alert('Added to cart!');
    }
});

// Chatbot
fetch('/api/chatbot', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        message: 'How do I track my order?'
    })
})
.then(response => response.json())
.then(data => {
    console.log(data.response);
});

// Get Driver Location
fetch('/api/driver-location/1')
    .then(response => response.json())
    .then(data => {
        console.log(`Lat: ${data.lat}, Lng: ${data.lng}`);
        console.log(`ETA: ${data.eta_minutes} minutes`);
    });
```

### Using cURL

```bash
# Add to Cart
curl -X POST http://localhost:5000/retailer/add-to-cart \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 50}' \
  --cookie "session=your-session-cookie"

# Chatbot
curl -X POST http://localhost:5000/api/chatbot \
  -H "Content-Type: application/json" \
  -d '{"message": "How to order?"}' \
  --cookie "session=your-session-cookie"

# Driver Location
curl http://localhost:5000/api/driver-location/1
```

---

## 🧪 Testing APIs

### Using Postman

1. Import collection (endpoints above)
2. Login to get session cookie
3. Use cookie in subsequent requests
4. Test all endpoints

### Using Browser Console

```javascript
// Test in browser console (when logged in)
fetch('/api/chatbot', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: 'Hello'})
})
.then(r => r.json())
.then(console.log);
```

---

## 📈 Future API Enhancements

### Planned for Production

1. **RESTful API**
   - JSON responses for all operations
   - Proper status codes
   - Pagination support

2. **Authentication**
   - JWT tokens
   - API key support
   - OAuth integration

3. **Rate Limiting**
   - Request throttling
   - Per-user limits
   - API quotas

4. **Webhooks**
   - Order status updates
   - Payment notifications
   - Delivery updates

5. **Real Services**
   - Actual payment gateway
   - Real SMS service
   - Real GPS tracking

---

## 🔗 Integration Examples

### Mobile App Integration

```javascript
// React Native / Flutter
async function placeOrder(orderData) {
    const response = await fetch('http://api.freshconnect.com/retailer/checkout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify(orderData)
    });
    return await response.json();
}
```

### External System Integration

```python
# Python integration
import requests

def get_products():
    response = requests.get(
        'http://api.freshconnect.com/products',
        headers={'Authorization': f'Bearer {api_key}'}
    )
    return response.json()
```

---

## 📊 API Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Not authenticated |
| 403 | Forbidden | Not authorized |
| 404 | Not Found | Resource not found |
| 500 | Server Error | Internal error |

---

## 🐛 Error Handling

### Client-Side

```javascript
fetch('/api/endpoint')
    .then(response => {
        if (!response.ok) {
            throw new Error('API request failed');
        }
        return response.json();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Something went wrong');
    });
```

### Server-Side

All endpoints have try-catch blocks:
- Database errors logged
- User-friendly messages returned
- Stack traces hidden in production

---

## 🔍 Debugging APIs

### Enable Debug Mode

In `.env`:
```
DEBUG=True
FLASK_ENV=development
```

### Check Logs

```bash
# Watch server console for:
[MOCK PAYMENT] SUCCESS - Transaction: MOCKTXN...
[MOCK DRIVER] Driver 1 assigned to order 5
[GEMINI ERROR] API key not valid
```

---

## 📱 CORS Configuration

Currently disabled. For production:

```python
from flask_cors import CORS

# In app/__init__.py
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourfrontend.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

---

## 🎯 API Best Practices

### Implemented
- ✅ RESTful design
- ✅ JSON responses
- ✅ Proper status codes
- ✅ Error handling
- ✅ Input validation

### For Production
- Rate limiting
- API versioning
- Request logging
- Response caching
- API documentation (OpenAPI/Swagger)

---

## 📚 Related Documentation

- Main documentation: [README.md](README.md)
- Setup guide: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- Test credentials: [TEST_CREDENTIALS.md](TEST_CREDENTIALS.md)

---

## 🎓 Learning Resources

- **Flask**: https://flask.palletsprojects.com/
- **REST APIs**: https://restfulapi.net/
- **JSON**: https://www.json.org/
- **HTTP Status Codes**: https://httpstatuses.com/

---

**Note:** This is documentation for a college project. Some features are mocked for demonstration purposes.

**API Version:** 1.0  
**Last Updated:** Nov 2024  
**Status:** ✅ Complete
