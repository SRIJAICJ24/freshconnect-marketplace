import os
import sys
from app import create_app, db
from app.models import User, Product, Order

# Create app with environment-specific config
config_name = os.environ.get('FLASK_ENV', 'development')
print(f"🚀 Starting FreshConnect with config: {config_name}")
print(f"📊 Python version: {sys.version}")
print(f"🔑 SECRET_KEY set: {bool(os.environ.get('SECRET_KEY'))}")
print(f"🗄️ DATABASE_URL set: {bool(os.environ.get('DATABASE_URL'))}")
print(f"🤖 GEMINI_API_KEY set: {bool(os.environ.get('GEMINI_API_KEY'))}")

try:
    app = create_app(config_name)
    print("✅ App created successfully!")
except Exception as e:
    print(f"❌ Failed to create app: {e}")
    raise

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Product': Product, 'Order': Order}

if __name__ == '__main__':
    # For local development only
    # In production, gunicorn handles the app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
