from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Crop, User, Task, Message, Order, Notification  # Include Notification here
from app.forms import CropForm, PredictionForm, TaskForm, MessageForm, WeatherForm, OrderForm, UpdateProfileForm
from app.ml_model.crop_prediction import predict_crop
from app.utils import save_crop_image, get_default_crop_image
from app.weather_service import get_current_weather, get_weather_forecast
import os

main_bp = Blueprint('main', __name__)

# -----------------------------
# Home Page
# -----------------------------
@main_bp.route('/')
def home():
    return render_template('index.html')

# -----------------------------
# Dashboard
# -----------------------------
@main_bp.route('/dashboard')
@login_required
def dashboard():
    recent_messages = Message.query.filter_by(receiver_id=current_user.id).order_by(Message.timestamp.desc()).limit(5).all()

    recent_crops = []
    if current_user.role in ['farmer', 'admin']:
        recent_crops = Crop.query.order_by(Crop.id.desc()).limit(5).all()

    from datetime import datetime
    now_date = datetime.now().strftime("%B %d, %Y")

    # Fetch Stats
    total_crops = Crop.query.count()
    total_orders = Order.query.count()

    # Fetch Weather (using user's first crop location or default)
    current_weather = None
    weather_city = "Mumbai" # Default
    if current_user.role == 'farmer' and current_user.crops:
        weather_city = current_user.crops[0].location

    try:
        api_key = current_app.config.get('OPENWEATHER_API_KEY')
        if api_key:
            current_weather = get_current_weather(weather_city, api_key)
    except:
        pass

    return render_template('dashboard.html',
                           recent_messages=recent_messages,
                           recent_crops=recent_crops,
                           total_crops=total_crops,
                           total_orders=total_orders,
                           now_date=now_date,
                           current_weather=current_weather)

# -----------------------------
# Crop Upload (Farmer Only)
# -----------------------------
@main_bp.route('/upload-crop', methods=['GET', 'POST'])
@login_required
def upload_crop():
    if current_user.role != 'farmer':
        flash('Access denied. Only farmers can upload crops.', 'danger')
        return redirect(url_for('main.dashboard'))

    form = CropForm()
    if form.validate_on_submit():
        image_file = None
        if form.image.data:
            image_file = save_crop_image(form.image.data)
        else:
            # Smart Default Images based on keyword matching
            name_lower = form.crop_name.data.lower()
            defaults = {
                'rice': 'rice.png',
                'wheat': 'wheat.png',
                'maize': 'maize.png',
                'corn': 'maize.png',
                'millet': 'millets.png',
                'mango': 'mango.png',
                'cotton': 'cotton.png',
                'sugarcane': 'millets.png', # Fallback to field image
                'onion': 'onion.png',
                'tomato': 'tomato.png',
                'potato': 'vegetables.png',
                'apple': 'apple.png',
                'fruit': 'apple.png',
                'veg': 'vegetables.png',
                'chilli': 'green_chilli.png',
                'green chilli': 'green_chilli.png',
                'garlic': 'onion.png'
            }
            
            # Initial match
            for keyword, filename in defaults.items():
                if keyword in name_lower:
                    image_file = filename
                    break
            
            # Category-based fallback if no specific match
            if not image_file:
                if any(k in name_lower for k in ['berry', 'orange', 'banana', 'guava', 'grapes']):
                    image_file = 'apple.png'
                elif any(k in name_lower for k in ['cabbage', 'carrot', 'spinach', 'beans', 'brinjal']):
                    image_file = 'vegetables.png'
                else:
                    image_file = 'millets.png' # General rural/field fallback

        crop = Crop(
            name=form.crop_name.data,
            quantity=form.quantity.data,
            price=form.price.data,
            harvest_date=form.harvest_date.data,
            location=form.location.data,
            description=form.description.data,
            user_id=current_user.id,
            image=image_file
        )
        try:
            db.session.add(crop)
            db.session.commit()
            flash('Crop uploaded successfully!', 'success')
            return redirect(url_for('main.my_crops'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    if request.method == 'POST' and not form.validate_on_submit():
        print("Form validation failed!")
        print(form.errors)
        flash('Please fix the errors in the form.', 'danger')

    crops = Crop.query.filter_by(user_id=current_user.id).all()
    return render_template('farmer/upload_crop.html', form=form, crops=crops)

# -----------------------------
# My Crops (Farmer Only)
# -----------------------------
@main_bp.route('/my-crops')
@login_required
def my_crops():
    if current_user.role != 'farmer':
        flash('Access denied. Only farmers can view crops.', 'danger')
        return redirect(url_for('main.dashboard'))

    crops = Crop.query.filter_by(user_id=current_user.id).all()
    return render_template('farmer/my_crops.html', crops=crops)

# -----------------------------
# Edit Crop (Farmer Only)
# -----------------------------
@main_bp.route('/edit-crop/<int:crop_id>', methods=['GET', 'POST'])
@login_required
def edit_crop(crop_id):
    if current_user.role != 'farmer':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))

    crop = Crop.query.get_or_404(crop_id)
    if crop.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.my_crops'))

    form = CropForm(obj=crop)
    if form.validate_on_submit():
        if form.image.data:
            crop.image = save_crop_image(form.image.data)

        crop.name = form.crop_name.data
        crop.quantity = form.quantity.data
        crop.price = form.price.data
        crop.harvest_date = form.harvest_date.data
        crop.location = form.location.data
        crop.description = form.description.data

        db.session.commit()
        flash('Crop updated successfully!', 'success')
        return redirect(url_for('main.my_crops'))

    return render_template('farmer/edit_crop.html', form=form, crop=crop)

# -----------------------------
# Marketplace (All Users)
# -----------------------------
@main_bp.route('/marketplace')
@login_required
def marketplace():
    query = request.args.get('q', '')
    sort_by = request.args.get('sort', 'newest')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    crops_query = Crop.query.filter(Crop.quantity > 0)

    if query:
        crops_query = crops_query.filter(
            (Crop.name.ilike(f'%{query}%')) |
            (Crop.location.ilike(f'%{query}%'))
        )

    if min_price is not None:
        crops_query = crops_query.filter(Crop.price >= min_price)

    if max_price is not None:
        crops_query = crops_query.filter(Crop.price <= max_price)

    if sort_by == 'price_asc':
        crops_query = crops_query.order_by(Crop.price.asc())
    elif sort_by == 'price_desc':
        crops_query = crops_query.order_by(Crop.price.desc())
    else:
        crops_query = crops_query.order_by(Crop.created_at.desc())

    crops = crops_query.all()
    return render_template('marketplace.html', products=crops, query=query, sort=sort_by, min_price=min_price, max_price=max_price)

# -----------------------------
# Buy Product (Buyer Only)
# -----------------------------
@main_bp.route('/buy/<int:product_id>', methods=['GET', 'POST'])
@login_required
def buy_product(product_id):
    if current_user.role != 'buyer':
        flash('Only buyers can place orders.', 'danger')
        return redirect(url_for('main.marketplace'))

    crop = Crop.query.get_or_404(product_id)
    form = OrderForm()

    if form.validate_on_submit():
        if form.quantity.data > crop.quantity:
            flash(f'Only {crop.quantity} kg available.', 'danger')
            return render_template('buy_product.html', product=crop, form=form)

        total_price = form.quantity.data * crop.price

        order = Order(
            buyer_id=current_user.id,
            crop_id=crop.id,
            quantity=form.quantity.data,
            total_price=total_price,
            status='Pending'
        )

        crop.quantity -= form.quantity.data

        db.session.add(order)
        db.session.commit()

        flash('Order placed! Proceed to checkout.', 'info')
        return redirect(url_for('main.checkout', order_id=order.id))

    return render_template('buy_product.html', product=crop, form=form)

# -----------------------------
# Checkout (Mock Payment)
# -----------------------------
@main_bp.route('/checkout/<int:order_id>', methods=['GET', 'POST'])
@login_required
def checkout(order_id):
    order = Order.query.get_or_404(order_id)
    if order.buyer_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('main.marketplace'))

    if request.method == 'POST':
        # Mock payment processing
        order.status = 'Pending'  # Change from 'Pending Payment' to 'Pending' (Farmer approval)

        # Notify Farmer
        notif = Notification(
            user_id=order.crop.user_id,
            message=f"New order received for {order.crop.name} from {current_user.name}."
        )
        db.session.add(notif)
        db.session.commit()

        flash('Payment successful! Your order has been sent to the farmer for approval.', 'success')
        return redirect(url_for('main.orders'))

    return render_template('checkout.html', order=order)

# -----------------------------
# Notifications
# -----------------------------
@main_bp.route('/notifications')
@login_required
def notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    # Mark as read
    for n in notifs:
        n.is_read = True
    db.session.commit()
    return render_template('notifications.html', notifications=notifs)

# -----------------------------
# Orders (All Users)
# -----------------------------
@main_bp.route('/orders')
@login_required
def orders():
    if current_user.role == 'farmer':
        orders = Order.query.join(Crop).filter(Crop.user_id == current_user.id).order_by(Order.date_ordered.desc()).all()
    elif current_user.role == 'buyer':
        orders = Order.query.filter_by(buyer_id=current_user.id).order_by(Order.date_ordered.desc()).all()
    else:
        orders = Order.query.order_by(Order.date_ordered.desc()).all()

    return render_template('orders.html', orders=orders)

# -----------------------------
# Update Order Status (Farmer Only)
# -----------------------------
@main_bp.route('/orders/update/<int:order_id>/<string:status>', methods=['POST'])
@login_required
def update_order_status(order_id, status):
    if current_user.role != 'farmer':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.orders'))

    order = Order.query.get_or_404(order_id)

    # Verify the order belongs to one of the farmer's crops
    if order.crop.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('main.orders'))

    if status in ['Approved', 'Delivered', 'Rejected']:
        # If rejecting, return the quantity back to the crop's available stock
        if status == 'Rejected' and order.status != 'Rejected':
            order.crop.quantity += order.quantity

        order.status = status

        # Notify Buyer
        notif = Notification(
            user_id=order.buyer_id,
            message=f"Your order #{order.id} for {order.crop.name} has been {status.lower()}."
        )
        db.session.add(notif)
        db.session.commit()

        flash(f'Order #{order.id} marked as {status}.', 'success')
    else:
        flash('Invalid status.', 'danger')

    return redirect(url_for('main.orders'))

# -----------------------------
# Weather Forecast (All Users)
# -----------------------------
@main_bp.route('/weather-forecast', methods=['GET', 'POST'])
@login_required
def weather_forecast():
    form = WeatherForm()
    weather_data = None
    current_weather = None
    API_KEY = current_app.config.get('OPENWEATHER_API_KEY') or os.getenv('OPENWEATHER_API_KEY')

    if form.validate_on_submit():
        if not API_KEY:
            flash('OpenWeather API Key is missing. Please set OPENWEATHER_API_KEY in your environment or .env', 'danger')
            return render_template('weather.html', form=form, weather_data=None, current_weather=None)

        location = form.location.data.strip()
        try:
            current_weather = get_current_weather(location, API_KEY)
            weather_data = get_weather_forecast(location, API_KEY)
            flash(f"Weather for {current_weather['location']}", 'success')
        except Exception as e:
            flash(f"Unable to retrieve weather for {location.title()}: {e}", 'danger')

    return render_template('weather.html', form=form, weather_data=weather_data, current_weather=current_weather)

# -----------------------------
# Task Planner (All Users)
# -----------------------------
@main_bp.route('/tasks', methods=['GET', 'POST'])  # ✅ FIXED: was using wrong blueprint name
@login_required
def task_planner():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            due_date=form.due_date.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        flash('Task added!', 'success')
        return redirect(url_for('main.task_planner'))

    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('task_planner.html', form=form, tasks=tasks)

@main_bp.route('/delete-task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('main.task_planner'))

    db.session.delete(task)
    db.session.commit()
    flash('Task removed.', 'success')
    return redirect(url_for('main.task_planner'))

# -----------------------------
# User Profile (All Users)
# -----------------------------
@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.name = form.name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.name.data = current_user.name
        form.email.data = current_user.email

    return render_template('profile.html', form=form)

# -----------------------------
# Manage Users (Admin Only)
# -----------------------------
@main_bp.route('/manage-users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        flash('Access denied. Only admins can manage users.', 'danger')
        return redirect(url_for('main.dashboard'))

    users = User.query.all()
    return render_template('manage_users.html', users=users)

# -----------------------------
# Admin - Manage All Crops
# -----------------------------
@main_bp.route('/admin/crops')
@login_required
def admin_manage_all_crops():
    if current_user.role != 'admin':
        flash('Access denied. Only admins can view all crops.', 'danger')
        return redirect(url_for('main.dashboard'))
    crops = Crop.query.all()
    return render_template('admin/manage_all_crops.html', crops=crops)

@main_bp.route('/admin/delete-crop/<int:crop_id>', methods=['POST'])
@login_required
def delete_crop_admin(crop_id):
    if current_user.role != 'admin':
        flash('Access denied. Only admins can delete crops.', 'danger')
        return redirect(url_for('main.dashboard'))
    crop = Crop.query.get_or_404(crop_id)
    db.session.delete(crop)
    db.session.commit()
    flash('Crop deleted successfully.', 'success')
    return redirect(url_for('main.admin_manage_all_crops'))

# -----------------------------
# Inbox (All Users)
# -----------------------------
@main_bp.route('/inbox')
@login_required
def inbox():
    # Find all users current_user has messaged with
    sent_to = db.session.query(Message.receiver_id).filter_by(sender_id=current_user.id)
    received_from = db.session.query(Message.sender_id).filter_by(receiver_id=current_user.id)
    contact_ids = set([r[0] for r in sent_to.all()] + [r[0] for r in received_from.all()])

    conversations = []
    for uid in contact_ids:
        latest_msg = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == uid)) |
            ((Message.sender_id == uid) & (Message.receiver_id == current_user.id))
        ).order_by(Message.timestamp.desc()).first()

        unread_count = Message.query.filter_by(sender_id=uid, receiver_id=current_user.id, is_read=False).count()

        conversations.append({
            'user': User.query.get(uid),
            'latest_message': latest_msg,
            'unread_count': unread_count
        })

    conversations.sort(key=lambda x: x['latest_message'].timestamp, reverse=True)
    return render_template('inbox.html', conversations=conversations)

# -----------------------------
# Chat (All Users)
# -----------------------------
@main_bp.route('/chat/<int:user_id>', methods=['GET', 'POST'])
@login_required
def chat(user_id):
    other_user = User.query.get_or_404(user_id)

    # Mark messages as read
    Message.query.filter_by(sender_id=user_id, receiver_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()

    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()

    form = MessageForm()
    if form.validate_on_submit():
        new_message = Message(
            sender_id=current_user.id,
            receiver_id=user_id,
            content=form.content.data
        )
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('main.chat', user_id=user_id))

    return render_template('chat.html', other_user=other_user, messages=messages, form=form)

# -----------------------------
# Chatbot (All Users)
# -----------------------------
@main_bp.route('/chatbot', methods=['GET', 'POST'])
@login_required
def chatbot():
    if request.method == 'POST':
        query = ''
        if request.is_json:
            query = request.get_json().get('query', '')
        else:
            query = request.form.get('query', '')

        lower_query = query.lower()

        if any(word in lower_query for word in ['hi', 'hello', 'hey', 'greetings']):
            response = "Hello there! Welcome to FarmSe. I can help you with weather updates, crop prediction, and the marketplace. What do you need help with?"
        elif 'weather' in lower_query or 'forecast' in lower_query:
            response = "You can check the latest 5-day weather forecast by visiting the Weather Forecast page from your dashboard."
        elif 'predict' in lower_query or 'best crop' in lower_query:
            response = "We have an AI tool that predicts the best crop for you! Just click 'Predict' on your dashboard and enter your soil details."
        elif 'crop' in lower_query or 'upload' in lower_query:
            response = "Farmers can upload their crops to the marketplace, and buyers can browse them. Check out your dashboard for these options."
        elif 'market' in lower_query or 'buy' in lower_query or 'sell' in lower_query:
            response = "You can visit our Marketplace to buy fresh products directly from farmers! If you are a farmer, you can upload your crops to sell."
        elif 'help' in lower_query:
            response = "I am the FarmSe assistant. You can ask me about weather, crop predictions, or the marketplace."
        else:
            response = "Sorry, I am still learning. You can ask me about weather, crops, predictions, or the marketplace!"

        if request.is_json:
            from flask import jsonify
            return jsonify({'response': response})

        return render_template('chatbot.html', response=response)

    return render_template('chatbot.html', response=None)

# -----------------------------
# Terms & Conditions
# -----------------------------
@main_bp.route('/terms')
def terms():
    return render_template('main/terms.html')

# -----------------------------
# Privacy Policy
# -----------------------------
@main_bp.route('/privacy')
def privacy():
    return render_template('main/privacy.html')

# -----------------------------
# Delete Crop (Farmer Only)
# -----------------------------
@main_bp.route('/delete-crop/<int:crop_id>', methods=['POST'])
@login_required
def delete_crop(crop_id):
    if current_user.role != 'farmer':
        flash('Access denied. Only farmers can delete crops.', 'danger')
        return redirect(url_for('main.dashboard'))

    crop = Crop.query.get_or_404(crop_id)
    if crop.user_id != current_user.id:
        flash('Unauthorized access to this crop.', 'danger')
        return redirect(url_for('main.my_crops'))

    try:
        db.session.delete(crop)
        db.session.commit()
        flash('Crop deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting crop: {str(e)}', 'danger')

    return redirect(url_for('main.my_crops'))

# -----------------------------
# Crop Prediction (All Users)
# -----------------------------
@main_bp.route('/predict-crop', methods=['GET', 'POST'])
@login_required
def crop_prediction():
    form = PredictionForm()
    prediction = None

    if form.validate_on_submit():
        try:
            input_data = {
                'N': float(form.n_content.data),
                'P': float(form.p_content.data),
                'K': float(form.k_content.data),
                'temperature': float(form.temperature.data),
                'humidity': float(form.humidity.data),
                'ph': float(form.ph_level.data),
                'rainfall': float(form.rainfall.data)
            }
            prediction = predict_crop(input_data)
            flash('Prediction successful!', 'success')
        except Exception as e:
            flash(f'Error during prediction: {str(e)}', 'danger')
    elif request.method == 'POST':
        flash('Please fix the errors in the form.', 'warning')

    return render_template('prediction_crop.html', form=form, prediction=prediction)


