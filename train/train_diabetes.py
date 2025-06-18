# train.py
import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# Create models directory if it doesn't exist
models_dir = Path('models')
models_dir.mkdir(exist_ok=True)

# Load dataset
diabetes_dataset = pd.read_csv('data/diabetes.csv')

# Split data
X = diabetes_dataset.drop(columns='Outcome', axis=1)
Y = diabetes_dataset['Outcome']

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, stratify=Y, random_state=2)

# Standardize
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train model
model = LogisticRegression()
model.fit(X_train, Y_train)

# Save model and scaler
with open(models_dir / 'diabetes_model.pkl', 'wb') as file:
    pickle.dump(model, file)

with open(models_dir / 'diabetes_scaler.pkl', 'wb') as file:
    pickle.dump(scaler, file)

# Save feature names
feature_names = X.columns.tolist()
with open(models_dir / 'diabetes_features.pkl', 'wb') as file:
    pickle.dump(feature_names, file)
