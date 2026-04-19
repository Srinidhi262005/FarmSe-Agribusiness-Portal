import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app import create_app
from app.models import db, Crop

app = create_app()

with app.app_context():
    crops = Crop.query.all()
    for crop in crops:
        name = crop.name.lower()
        if 'rice' in name:
            crop.image = 'rice.png'
        elif 'cotton' in name:
            crop.image = 'cotton.png'
        elif 'millet' in name:
            crop.image = 'millets.png'
        else:
            # For anything else, maybe a default or leave as is
            pass
    db.session.commit()
    print("Database updated with real crop images!")
