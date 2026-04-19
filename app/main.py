from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, DateField, SelectField, FileField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask import Blueprint
main_bp = Blueprint('main', __name__)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])  # Ensure this is present
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match.")])
    role = SelectField('Role', choices=[('farmer', 'Farmer'), ('buyer', 'Buyer'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Register')


# -------------------- Signup / Register Form --------------------
class SignupForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
# -------------------- Crop Form --------------------
class CropForm(FlaskForm):
    crop_name = StringField('Crop Name', validators=[DataRequired()])
    quantity = FloatField('Quantity', validators=[DataRequired()])
    price = FloatField('Price per Unit', validators=[DataRequired()])
    harvest_date = DateField('Harvest Date', format='%Y-%m-%d', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    image = FileField('Crop Image')
    submit = SubmitField('Submit')

# -------------------- Task Form --------------------
class TaskForm(FlaskForm):
    title = StringField('Task Title', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Task Description', validators=[DataRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[DataRequired()])
    priority = SelectField('Priority', choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], validators=[DataRequired()])
    submit = SubmitField('Add Task')

# -------------------- User Form --------------------
class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('farmer', 'Farmer'), ('buyer', 'Buyer'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Update User')

