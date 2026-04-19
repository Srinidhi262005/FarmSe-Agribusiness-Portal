from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from ..extensions import db
from app.models import Crop
from app.forms import CropForm
farmer_bp = Blueprint('farmer', __name__, url_prefix='/farmer')

# View & Upload Crops
@farmer_bp.route('/upload-crop', methods=['GET', 'POST'])
@login_required
def upload_crop():
    form = CropForm()
    if request.method == 'POST' and form.validate_on_submit():
        name = form.crop_name.data
        quantity = form.quantity.data
        price = form.price.data
        harvest_date = form.harvest_date.data
        location = form.location.data
        image_file = form.image.data
        image_filename = None
        if image_file and image_file.filename:
            try:
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(current_app.root_path, 'static', 'crop_images')
                os.makedirs(image_path, exist_ok=True)
                image_file.save(os.path.join(image_path, filename))
                image_filename = f'crop_images/{filename}'
                flash(f'Image uploaded successfully: {filename}', 'success')
            except Exception as e:
                flash(f'Error uploading image: {str(e)}', 'danger')
                print(f'Image upload error: {str(e)}')
        new_crop = Crop(
            name=name,
            quantity=quantity,
            price=price,
            harvest_date=harvest_date,
            location=location,
            user_id=current_user.id,
            image=image_filename
        )
        db.session.add(new_crop)
        db.session.commit()
        flash('Crop uploaded successfully!', 'success')
        return redirect(url_for('farmer.upload_crop'))
    crops = Crop.query.filter_by(user_id=current_user.id).all()
    return render_template('farmer/upload_crop.html', crops=crops, form=form)

# Edit Crop
# Edit Crop
@farmer_bp.route('/edit-crop/<int:crop_id>', methods=['GET', 'POST'])
@login_required
def edit_crop(crop_id):
    crop = Crop.query.get_or_404(crop_id)
    if crop.user_id != current_user.id:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('farmer.upload_crop'))

    if request.method == 'POST':
        crop.name = request.form['name']
        crop.quantity = request.form['quantity']
        crop.price = request.form['price']
        crop.harvest_date = datetime.strptime(request.form['harvest_date'], '%Y-%m-%d')
        crop.location = request.form['location']
        db.session.commit()

        flash('Crop updated successfully!', 'success')
        return redirect(url_for('farmer.upload_crop'))

    # For GET request, pre-fill the form with crop data
    return render_template('farmer/edit_crop.html', crop=crop)


# Delete Crop
@farmer_bp.route('/delete-crop/<int:crop_id>', methods=['POST'])
@login_required
def delete_crop(crop_id):
    crop = Crop.query.get_or_404(crop_id)
    if crop.user_id != current_user.id:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('farmer.upload_crop'))

    db.session.delete(crop)
    db.session.commit()
    flash('Crop deleted successfully.', 'success')
    return redirect(url_for('farmer.upload_crop'))
@farmer_bp.route('/add_crop', methods=['GET', 'POST'])
def add_crop():
    form = CropForm()  # Create an instance of the CropForm
    if form.validate_on_submit():  # If the form is valid and submitted
        # Handle form submission here (save the crop to the database)
        new_crop = Crop(
            name=form.crop_name.data,
            quantity=form.quantity.data,
            price=form.price.data,
            harvest_date=form.harvest_date.data,
            location=form.location.data,
            user_id=current_user.id
        )
        db.session.add(new_crop)
        db.session.commit()
        
        # After adding, redirect to another page (for example, crop listing)
        return redirect(url_for('farmer.view_crops'))
    
    return render_template('add_crop.html', form=form)