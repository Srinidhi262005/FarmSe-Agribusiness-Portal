import os
import secrets
from flask import current_app
from PIL import Image

# -------- Save uploaded crop image --------
def save_crop_image(form_image):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    picture_fn = random_hex + f_ext
    images_dir = os.path.join(current_app.root_path, 'static/crop_images')
    os.makedirs(images_dir, exist_ok=True)
    picture_path = os.path.join(images_dir, picture_fn)

    # Resize the image to 500x500 max while maintaining aspect ratio
    output_size = (500, 500)
    i = Image.open(form_image)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

# -------- Crop image helpers --------

def normalize_crop_image_name(image_name):
    if not image_name:
        return None

    image_name = image_name.strip()
    prefixes = ['crop_images/', 'static/crop_images/', './crop_images/', '/crop_images/']
    for prefix in prefixes:
        if image_name.startswith(prefix):
            return image_name[len(prefix):]
    return image_name


def get_default_crop_image(crop_name):
    name = (crop_name or '').lower()
    if not name:
        return 'vegetables.png'

    keyword_map = {
        'rice': 'rice.png',
        'paddy': 'rice.png',
        'wheat': 'wheat.png',
        'maize': 'maize.png',
        'corn': 'maize.png',
        'millet': 'millets.png',
        'ragi': 'millets.png',
        'jowar': 'millets.png',
        'sorghum': 'millets.png',
        'cotton': 'cotton.png',
        'mango': 'mango.png',
        'apple': 'apple.png',
        'banana': 'apple.png',
        'orange': 'apple.png',
        'guava': 'apple.png',
        'berry': 'apple.png',
        'grape': 'apple.png',
        'tomato': 'tomato.png',
        'onion': 'onion.png',
        'potato': 'vegetables.png',
        'carrot': 'vegetables.png',
        'spinach': 'vegetables.png',
        'beans': 'vegetables.png',
        'brinjal': 'vegetables.png',
        'cabbage': 'vegetables.png',
        'chilli': 'vegetables.png',
        'garlic': 'onion.png',
        'lettuce': 'vegetables.png',
        'okra': 'vegetables.png',
        'pumpkin': 'vegetables.png',
        'sugarcane': 'millets.png'
    }

    for keyword, filename in keyword_map.items():
        if keyword in name:
            return filename

    if any(term in name for term in ['fruit', 'fruits']):
        return 'apple.png'
    if any(term in name for term in ['vegetable', 'veggies', 'veg']):
        return 'vegetables.png'
    if any(term in name for term in ['harvest', 'farm', 'field']):
        return 'vegetables.png'

    return 'vegetables.png'


def crop_image_name(image_name, crop_name=''):
    normalized = normalize_crop_image_name(image_name)
    return normalized or get_default_crop_image(crop_name)

# -------- Dummy weather forecast (placeholder for API) --------
def get_weather_forecast(location):
    return {
        "location": location,
        "forecast": "Sunny with a chance of rain",
        "temperature": "28°C",
        "humidity": "60%"
    }

# -------- Rule-based crop predictor (optional use) --------
def predict_crop_by_conditions(soil, temperature, humidity):
    soil = soil.lower()
    if soil == 'loamy' and temperature > 25 and humidity > 50:
        return "Rice"
    elif soil == 'clay':
        return "Wheat"
    else:
        return "Maize"

# -------- Predict crop from form input (main method used in routes) --------
def predict_crop(input_data):
    """
    input_data: dict with keys including
    'N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'
    """
    if input_data.get('N', 0) > 100:
        return "Sugarcane"
    elif input_data.get('temperature', 0) > 30:
        return "Cotton"
    elif input_data.get('rainfall', 0) < 50:
        return "Millets"
    else:
        return "Wheat"


