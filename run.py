import os
from app import create_app, db
from app.models import User, Product, Order

# Create app with environment-specific config
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Product': Product, 'Order': Order}

if __name__ == '__main__':
    # For local development only
    # In production, gunicorn handles the app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
