import pickle
import numpy as np
import pandas as pd

# Load the saved model and encoders
with open('app/ml_model/crop_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('app/ml_model/label_encoders.pkl', 'rb') as f:
    encoders = pickle.load(f)

with open('app/ml_model/target_encoder.pkl', 'rb') as f:
    target_encoder = pickle.load(f)


def predict_crop(input_data: dict) -> str:
    """
    Predict the crop given input feature data.
    
    input_data: dict with keys:
      - 'N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'
      - Make sure keys match your dataset features
    
    Returns predicted crop label as string.
    """

    # Convert input dict to DataFrame (1 row)
    df = pd.DataFrame([input_data])

    # Encode categorical features if any (usually none here)
    for col in df.columns:
        if col in encoders:
            df[col] = encoders[col].transform(df[col])

    # Predict using the model
    prediction_encoded = model.predict(df)[0]

    # Decode prediction to original label
    prediction_label = target_encoder.inverse_transform([prediction_encoded])[0]

    return prediction_label


# Example usage
if __name__ == "__main__":
    sample_input = {
        'N': 90,
        'P': 42,
        'K': 43,
        'temperature': 20.8,
        'humidity': 82,
        'ph': 6.5,
        'rainfall': 200
    }

    predicted_crop = predict_crop(sample_input)
    print(f"Predicted Crop: {predicted_crop}")



