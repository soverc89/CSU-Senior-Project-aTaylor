from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Create extensions globally
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    # 1. Initialize the app inside the function
    app = Flask(__name__)
    
    # 2. Configure the app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'some-secret-key' # In a real app, use environment variables
    
    # 3. Attach the database and login manager to the app
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'main.login'
    login_manager.login_message = "Please log in to access this page."
    
    # 4. Import and register your routes
    from . import routes
    app.register_blueprint(routes.bp)
    
    # User loader function for Flask-Login
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 5. Return the fully built app
    return app
