from flask import Blueprint, render_template, request, flash
from app.ml_model.crop_prediction import predict_crop

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/predict_crop', methods=['GET', 'POST'])
def predict_crop_route():
    prediction = None
    if request.method == 'POST':
        try:
            input_data = {
                'N': float(request.form.get('N', 0)),
                'P': float(request.form.get('P', 0)),
                'K': float(request.form.get('K', 0)),
                'temperature': float(request.form.get('temperature', 0)),
                'humidity': float(request.form.get('humidity', 0)),
                'ph': float(request.form.get('ph', 0)),
                'rainfall': float(request.form.get('rainfall', 0)),
            }
            prediction = predict_crop(input_data)
        except Exception as e:
            flash('Error: ' + str(e), 'danger')

    return render_template('predict_crop.html', prediction=prediction)
