from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .extensions import db

# -------------------- User Model --------------------

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    # Relationships
    crops = db.relationship('Crop', back_populates='user', lazy=True)
    tasks = db.relationship('Task', back_populates='user', lazy=True)
    orders = db.relationship('Order', back_populates='buyer', lazy=True)
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', back_populates='sender')
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', back_populates='receiver')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Hashes the user's password with pbkdf2:sha256 method"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Verifies the user's password"""
        return check_password_hash(self.password_hash, password)



# -------------------- Crop Model --------------------

class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    harvest_date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Add this line
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(120), nullable=True)

    # Relationships
    user = db.relationship('User', back_populates='crops')
    orders = db.relationship('Order', back_populates='crop', lazy=True)

    def __repr__(self):
        return f'<Crop {self.name} (ID: {self.id}) - {self.quantity} units at {self.price} per unit>'


# -------------------- Task Model --------------------
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', back_populates='tasks')

    def __repr__(self):
        return f'<Task {self.title} (Due: {self.due_date})>'


# -------------------- Order Model --------------------
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    quantity = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    date_ordered = db.Column(db.DateTime, default=datetime.utcnow)

    buyer = db.relationship('User', back_populates='orders')
    crop = db.relationship('Crop', back_populates='orders')

    def __repr__(self):
        return f'<Order {self.id} - Buyer: {self.buyer_id}, Crop: {self.crop_id}, Status: {self.status}>'

    def calculate_total_price(self):
        """Calculate the total price based on quantity and crop price."""
        self.total_price = self.quantity * self.crop.price


# -------------------- Message Model --------------------
class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_read = db.Column(db.Boolean, default=False)


    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], back_populates='received_messages')

    def __repr__(self):
        return f'<Message {self.id} - From: {self.sender_id} To: {self.receiver_id}>'


# -------------------- Optional Payment Model --------------------
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship('Order', backref='payment')

    def __repr__(self):
        return f'<Payment {self.id} - Order: {self.order_id} Amount: {self.amount}>'
class WeatherForecast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    forecast_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def _repr_(self):
        return f'<WeatherForecast {self.location} - Temp: {self.temperature}, Humidity: {self.humidity}>'


# -------------------- Crop Prediction Model --------------------
class CropPrediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(100), nullable=False)
    predicted_yield = db.Column(db.Float, nullable=False)
    soil_type = db.Column(db.String(100), nullable=False)
    weather_conditions = db.Column(db.String(200), nullable=False)
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CropPrediction {self.crop_name} - Predicted Yield: {self.predicted_yield}>'


# -------------------- Notification Model --------------------
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('notifications', lazy=True))

    def __repr__(self):
        return f'<Notification {self.id} for User {self.user_id}>'







