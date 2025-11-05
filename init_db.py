from app import create_app, db
from dotenv import load_dotenv

def init_database():
    """
    Initialize the database
    Creates all tables defined in models.py
    """
    load_dotenv()
    
    app = create_app()
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✅ Database initialized successfully!")
        print(f"Database file: {app.config['SQLALCHEMY_DATABASE_URI']}")

if __name__ == '__main__':
    init_database()
