from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, Crop, Order

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# --- Protect admin routes ---
def admin_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Unauthorized access!", "danger")
            return redirect(url_for('main.dashboard'))
        return func(*args, **kwargs)
    return wrapper

# --- Admin Dashboard ---
@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    user_count = User.query.count()
    crop_count = Crop.query.count()
    order_count = Order.query.count()
    return render_template('admin/admin_dashboard.html',
                           user_count=user_count,
                           crop_count=crop_count,
                           order_count=order_count)

# --- Manage Users ---
@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@admin_bp.route('/users/delete/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == "admin":
        flash("You cannot delete another admin!", "warning")
        return redirect(url_for('admin.manage_users'))
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully", "success")
    return redirect(url_for('admin.manage_users'))

# --- Manage Crops ---
@admin_bp.route('/crops')
@login_required
@admin_required
def manage_crops():
    crops = Crop.query.all()
    return render_template('admin/manage_crops.html', crops=crops)

@admin_bp.route('/crops/delete/<int:crop_id>')
@login_required
@admin_required
def delete_crop(crop_id):
    crop = Crop.query.get_or_404(crop_id)
    db.session.delete(crop)
    db.session.commit()
    flash("Crop deleted successfully", "success")
    return redirect(url_for('admin.manage_crops'))

# --- Manage Orders ---
@admin_bp.route('/orders')
@login_required
@admin_required
def manage_orders():
    orders = Order.query.all()
    return render_template('admin/manage_orders.html', orders=orders)

@admin_bp.route('/orders/delete/<int:order_id>')
@login_required
@admin_required
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash("Order deleted successfully", "success")
    return redirect(url_for('admin.manage_orders'))
