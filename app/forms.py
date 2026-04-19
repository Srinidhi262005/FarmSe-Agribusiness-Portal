from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DecimalField, DateField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed  # <-- File upload validation


# -------------------- Login Form --------------------
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# -------------------- Register Form --------------------
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match.")])
    role = SelectField('Role', choices=[('farmer', 'Farmer'), ('buyer', 'Buyer'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Register')


# -------------------- User Form --------------------
class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match.")])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('user', 'User')], validators=[DataRequired()])


# -------------------- Signup Form --------------------
class SignupForm(FlaskForm):
    username = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    role = SelectField('Role', choices=[('farmer', 'Farmer'), ('buyer', 'Buyer'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')


# -------------------- Crop Form --------------------
class CropForm(FlaskForm):
    crop_name = StringField('Crop Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=1000)])
    quantity = IntegerField('Quantity (kg)', validators=[DataRequired()])
    price = DecimalField('Price per kg (₹)', validators=[DataRequired()])
    harvest_date = DateField('Harvest Date', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    image = FileField('Crop Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Submit')


# -------------------- Task Form --------------------
class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Add Task')


# -------------------- Order Form --------------------
class OrderForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Place Order')


# -------------------- Message Form --------------------
class MessageForm(FlaskForm):
    recipient = SelectField('Recipient', coerce=int, validators=[DataRequired()])
    content = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')



# -------------------- Weather Form --------------------
class WeatherForm(FlaskForm):
    location = StringField('Enter City Name', validators=[DataRequired()])
    submit = SubmitField('Get Forecast')

# -------------------- Prediction Form --------------------
class PredictionForm(FlaskForm):
    n_content = DecimalField('Nitrogen (N) Content', validators=[DataRequired()])
    p_content = DecimalField('Phosphorus (P) Content', validators=[DataRequired()])
    k_content = DecimalField('Potassium (K) Content', validators=[DataRequired()])
    temperature = DecimalField('Temperature (°C)', validators=[DataRequired()])
    humidity = DecimalField('Humidity (%)', validators=[DataRequired()])
    ph_level = DecimalField('pH Level', validators=[DataRequired()])
    rainfall = DecimalField('Rainfall (mm)', validators=[DataRequired()])
    
    submit = SubmitField('Predict Crop')



# -------------------- Chatbot Form --------------------
class ChatbotForm(FlaskForm):
    query = TextAreaField('Ask a question about farming, weather, or crops...', validators=[DataRequired()])
    submit = SubmitField('Ask')










# -------------------- Profile Form --------------------
class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Profile')
