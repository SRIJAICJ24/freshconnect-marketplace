# 🔧 Troubleshooting Guide - FreshConnect

## Common Issues & Solutions

---

## 🐍 Python & Dependencies Issues

### Issue 1: "Python not found" or "python: command not found"

**Symptoms:**
```
'python' is not recognized as an internal or external command
```

**Solutions:**

**Windows:**
1. Install Python from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart terminal
4. Try `python --version` or `py --version`

**Mac/Linux:**
```bash
# Check if Python 3 is installed
python3 --version

# Use python3 instead of python
python3 run.py
```

---

### Issue 2: "pip: command not found"

**Solution:**
```bash
# Windows
python -m pip install -r requirements.txt

# Mac/Linux
python3 -m pip install -r requirements.txt
```

---

### Issue 3: Module/Package not found errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'flask'
ImportError: cannot import name 'create_app'
```

**Solutions:**

1. **Ensure virtual environment is activated:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

2. **Reinstall dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Check you're in the right directory:**
   ```bash
   cd freshconnect-app
   ls  # Should see run.py, config.py, etc.
   ```

---

## 🗄️ Database Issues

### Issue 4: Database errors on startup

**Symptoms:**
```
sqlalchemy.exc.OperationalError
sqlite3.OperationalError: no such table
```

**Solution:**
```bash
# Delete old database
rm marketplace.db  # Mac/Linux
del marketplace.db  # Windows

# Reinitialize
python init_db.py
python seed_data.py
```

---

### Issue 5: "Cannot modify database" or "Database is locked"

**Solution:**
1. Close all connections to the database
2. Stop the Flask server (Ctrl+C)
3. Delete the database file
4. Reseed:
   ```bash
   python seed_data.py
   ```

---

## 🔑 API & Environment Issues

### Issue 6: "GEMINI_API_KEY not set in .env"

**Symptoms:**
```
ValueError: GEMINI_API_KEY not set in .env
```

**Solutions:**

1. **Create .env file:**
   ```bash
   # Windows
   copy .env.example .env
   
   # Mac/Linux
   cp .env.example .env
   ```

2. **Add your API key:**
   Edit `.env` file:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

3. **Get Gemini API Key:**
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with Google account
   - Create API key
   - Copy and paste into .env

---

### Issue 7: Gemini API errors

**Symptoms:**
```
[GEMINI ERROR] API key not valid
google.api_core.exceptions.PermissionDenied
```

**Solutions:**

1. **Check API key is correct**
2. **Ensure API is enabled** in Google Cloud Console
3. **Check quota limits** (free tier has limits)
4. **Test with a simple request** to verify key works

---

## 🌐 Server & Port Issues

### Issue 8: "Port 5000 already in use"

**Symptoms:**
```
OSError: [Errno 48] Address already in use
```

**Solutions:**

**Option 1: Change port in run.py**
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Option 2: Kill existing process**

**Windows:**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Mac/Linux:**
```bash
lsof -i :5000
kill -9 <PID>
```

---

### Issue 9: "Cannot connect to http://localhost:5000"

**Solutions:**

1. **Check server is running:**
   ```
   * Running on http://127.0.0.1:5000
   ```

2. **Try different URL:**
   - http://127.0.0.1:5000
   - http://localhost:5000
   - http://0.0.0.0:5000

3. **Check firewall settings**

4. **Restart server:**
   ```bash
   # Stop with Ctrl+C
   # Restart
   python run.py
   ```

---

## 🔐 Authentication Issues

### Issue 10: "Cannot login" or "Invalid credentials"

**Solutions:**

1. **Verify credentials from TEST_CREDENTIALS.md:**
   - Retailer: retailer1@freshconnect.com / retailer123
   - Vendor: vendor1@freshconnect.com / vendor123

2. **Check database is seeded:**
   ```bash
   python seed_data.py
   ```

3. **Clear browser cache/cookies**

4. **Try different browser**

---

### Issue 11: "Please log in" redirects or access denied

**Cause:** Session expired or role mismatch

**Solutions:**

1. **Login again**
2. **Check you're using correct role:**
   - Vendor features need vendor account
   - Retailer features need retailer account
3. **Clear cookies and login fresh**

---

## 💳 Payment Issues

### Issue 12: Payment always fails

**Note:** This is a MOCK payment gateway with 70% success rate.

**Solutions:**

1. **This is normal behavior for testing**
2. **Try multiple times** (70% success rate)
3. **Check console logs:**
   ```
   [MOCK PAYMENT] SUCCESS - Transaction: MOCKTXN...
   [MOCK PAYMENT] FAILED - Transaction: MOCKTXN...
   ```

---

## 📱 UI/Display Issues

### Issue 13: Broken layout or missing styles

**Solutions:**

1. **Clear browser cache:**
   - Ctrl+Shift+Del (Chrome)
   - Select "Cached images and files"

2. **Hard refresh:**
   - Ctrl+F5 (Windows)
   - Cmd+Shift+R (Mac)

3. **Check static files exist:**
   ```
   app/static/css/style.css
   app/static/css/mobile.css
   ```

4. **Check Flask is serving static files**

---

### Issue 14: Images not loading

**Solutions:**

1. **Check image path:**
   ```
   app/static/images/products/
   ```

2. **Check file permissions**

3. **Upload image through vendor portal**

---

## 🚀 Performance Issues

### Issue 15: App running slow

**Solutions:**

1. **Check database size:**
   ```bash
   # If marketplace.db is huge, reseed
   python seed_data.py
   ```

2. **Close other applications**

3. **Restart the server**

4. **Check for infinite loops in code**

---

## 📦 Virtual Environment Issues

### Issue 16: "venv not activating"

**Windows:**
```bash
# Try
venv\Scripts\activate

# If that doesn't work
venv\Scripts\activate.bat

# PowerShell
venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
source venv/bin/activate

# Check activation
which python  # Should show venv path
```

---

### Issue 17: "Permission denied" when creating venv

**Mac/Linux:**
```bash
sudo python3 -m venv venv
```

**Windows:**
Run terminal as Administrator

---

## 🔄 Session & Cookie Issues

### Issue 18: "Cart empty" after adding items

**Solutions:**

1. **Check cookies are enabled** in browser
2. **Don't use incognito/private mode**
3. **Check SECRET_KEY** in .env is set
4. **Try different browser**

---

## 📝 Template Errors

### Issue 19: "TemplateNotFound" errors

**Symptoms:**
```
jinja2.exceptions.TemplateNotFound: vendor/dashboard.html
```

**Solutions:**

1. **Check file exists:**
   ```
   app/templates/vendor/dashboard.html
   ```

2. **Check file path spelling** (case-sensitive on Linux/Mac)

3. **Verify template structure:**
   ```
   app/
     templates/
       vendor/
         dashboard.html
   ```

---

## 🐛 General Debugging Tips

### Enable Debug Mode

In `.env`:
```env
DEBUG=True
FLASK_ENV=development
```

### Check Console Logs

**Browser Console:**
- Press F12
- Go to Console tab
- Look for JavaScript errors

**Server Console:**
- Watch terminal where `python run.py` is running
- Look for error messages
- Check mock service logs

### Common Error Locations

1. **Import errors:** Check `app/__init__.py`
2. **Database errors:** Check `app/models.py`
3. **Route errors:** Check `app/routes/*.py`
4. **Template errors:** Check `app/templates/*.html`

---

## 🆘 Still Having Issues?

### Debugging Checklist

- [ ] Virtual environment activated?
- [ ] All dependencies installed?
- [ ] .env file created with API key?
- [ ] Database initialized and seeded?
- [ ] Correct Python version (3.8+)?
- [ ] In correct directory?
- [ ] No typos in file names?
- [ ] Firewall not blocking?
- [ ] Port not already in use?

### Nuclear Option (Complete Reset)

If nothing works, try complete reset:

```bash
# 1. Deactivate venv
deactivate

# 2. Delete everything
rm -rf venv marketplace.db  # Mac/Linux
rmdir /s venv & del marketplace.db  # Windows

# 3. Start fresh
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
python seed_data.py
python run.py
```

---

## 📞 Getting Help

### Before Asking for Help, Provide:

1. **Error message** (full text)
2. **What you were trying to do**
3. **Your operating system**
4. **Python version:** `python --version`
5. **Steps you've already tried**

### Check These First:

- README.md for setup instructions
- SETUP_GUIDE.md for quick setup
- This TROUBLESHOOTING.md file
- Code comments in the files

---

## 💡 Prevention Tips

### Best Practices:

1. **Always activate venv** before working
2. **Commit to git regularly** if using version control
3. **Backup database** before major changes
4. **Keep .env secure** (never commit to git)
5. **Test after each major change**
6. **Read error messages carefully**
7. **Check file paths are correct**
8. **Use correct Python version**

---

**Remember:** Most issues are solved by:
1. Checking you're in the right directory
2. Virtual environment is activated
3. Dependencies are installed
4. Database is initialized

**You got this! 💪**
