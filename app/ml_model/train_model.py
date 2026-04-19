
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
import pickle
import os

# Path to your dataset
dataset_path = r'C:\Users\hp\Downloads\mock_crop_dataset.csv'

# Check if dataset exists
if not os.path.exists(dataset_path):
    raise FileNotFoundError(f"Dataset not found at {dataset_path}")

# Load dataset
df = pd.read_csv(dataset_path)

# Print columns for debugging
print("Columns in dataset:", df.columns.tolist())

# Update target column to match your dataset
target_col = 'label'  # your dataset's target column

if target_col not in df.columns:
    raise KeyError(f"Target column '{target_col}' not found in dataset columns")

# Separate features and target
X = df.drop(target_col, axis=1)
y = df[target_col]

# Label encode categorical feature columns if any
encoders = {}
for col in X.columns:
    if X[col].dtype == 'object':
        encoders[col] = LabelEncoder()
        X[col] = encoders[col].fit_transform(X[col])

# Encode target labels
target_encoder = LabelEncoder()
y = target_encoder.fit_transform(y)

# Train Decision Tree model
model = DecisionTreeClassifier()
model.fit(X, y)

# Save model and encoders
with open('app/ml_model/crop_model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('app/ml_model/label_encoders.pkl', 'wb') as f:
    pickle.dump(encoders, f)

with open('app/ml_model/target_encoder.pkl', 'wb') as f:
    pickle.dump(target_encoder, f)

print("✅ Model and encoders saved successfully!")



