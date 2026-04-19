import os
from flask import Flask, current_app
from flask_login import current_user
from .extensions import db, migrate, login_manager, bcrypt, mail
from .auth import auth_bp
from .routes.main_routes import main_bp
from .models import User, Notification
from dotenv import find_dotenv, load_dotenv
from . import routes
from app.routes import main_routes  # This imports and registers all main_bp routes

load_dotenv(find_dotenv())

def create_app():
    app = Flask(__name__)
    app.jinja_env.add_extension('jinja2.ext.do')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'supersecretkey123'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_URI') or 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['OPENWEATHER_API_KEY'] = os.environ.get('OPENWEATHER_API_KEY')
    
    # Email Configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') or 'your_email@gmail.com'
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') or 'your_email_password'

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    # Flask-Login user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    from .utils import crop_image_name

    @app.context_processor
    def inject_vars():
        unread_notif_count = 0
        unread_msg_count = 0
        if current_user.is_authenticated:
            from .models import Message
            unread_notif_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
            unread_msg_count = Message.query.filter_by(receiver_id=current_user.id, is_read=False).count()
        return dict(
            current_app=current_app, 
            unread_notifications=unread_notif_count,
            unread_messages=unread_msg_count,
            crop_image_name=crop_image_name
        )

    return app
















