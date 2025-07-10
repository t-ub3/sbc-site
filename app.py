import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///sbc_news.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Import routes after app initialization
from routes import *

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()
    
    # Create admin user from environment variables
    from models import User
    from werkzeug.security import generate_password_hash
    
    admin_email = os.environ.get("ADMIN_EMAIL")
    admin_password = os.environ.get("ADMIN_PASSWORD")
    admin_name = os.environ.get("ADMIN_NAME", "Administrator")
    
    if admin_email and admin_password:
        existing_admin = User.query.filter_by(email=admin_email).first()
        if not existing_admin:
            admin_user = User(
                email=admin_email,
                password_hash=generate_password_hash(admin_password),
                name=admin_name,
                role='admin',
                role_title='Chief Editor'
            )
            db.session.add(admin_user)
            db.session.commit()
            app.logger.info(f"Admin user created: {admin_email}")
