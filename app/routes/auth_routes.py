from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from app.extensions import db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import LoginForm, RegisterForm, SignupForm

# ✅ Fix Blueprint name (was _name_ which is incorrect)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# -------------------------
# Login Route
# -------------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Login successful.', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Invalid login credentials.', 'danger')
    return render_template('auth/login.html', form=form)


# -------------------------
# Signup Route
# -------------------------
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data.strip().lower()
        email = form.email.data.strip().lower()

        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Username already exists. Please choose another one.", "danger")
            return render_template("auth/signup.html", form=form)

        if existing_email:
            flash("Email is already registered. Try logging in.", "danger")
            return render_template("auth/signup.html", form=form)

        new_user = User(
            username=username,
            name=form.name.data.strip(),
            email=email,
            role='farmer'
        )
        new_user.set_password(form.password.data)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('auth/signup.html', form=form)


# -------------------------
# Register Route
# -------------------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip().lower()
        email = form.email.data.strip().lower()

        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user or existing_email:
            flash('User with this username or email already exists.', 'danger')
            return render_template('auth/register.html', form=form)

        user = User(
            username=username,
            name=form.name.data,
            email=email,
            role=form.role.data
        )
        user.set_password(form.password.data)

        try:
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('auth/register.html', form=form)


# -------------------------
# Logout Route
# -------------------------
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

