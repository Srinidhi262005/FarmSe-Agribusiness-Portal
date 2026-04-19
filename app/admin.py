from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User
from app.forms import UserForm  # Only import once

# Initialize the Blueprint for the admin routes
admin_bp = Blueprint('admin', __name__)

# Admin role check decorator for protected routes
def admin_required(func):
    def ensure_admin(*args, **kwargs):
        if current_user.role != 'admin':
            flash('You are not authorized to access this page.', 'danger')
            return redirect(url_for('main.dashboard'))  # Redirect to main dashboard if not admin
        return func(*args, **kwargs)

    ensure_admin.__name__ = func.__name__  # Ensure the original function name is retained
    return ensure_admin

# ---------------- User Management Routes ----------------

@admin_bp.route('/manage_users')
@login_required
@admin_required
def manage_users():
    """Route to manage users (pagination support)."""
    users = User.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('manage_users.html', users=users)

from werkzeug.security import generate_password_hash

@admin_bp.route('/add_user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)  # Hash the password
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,  # Store the hashed password
            role=form.role.data
        )
        db.session.add(user)
        db.session.commit()
        flash('User added successfully!', 'success')
        return redirect(url_for('admin.manage_users'))  # Redirect to user management page
    return render_template('add_user.html', form=form)

@admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data

        # Only update the password if the user has entered a new password
        if form.password.data:
            user.password = generate_password_hash(form.password.data)
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/edit_user.html', form=form, user=user)

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Route to delete a user."""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.manage_users'))  # Redirect to user management after deletion

