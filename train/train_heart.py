# train/train_heart.py
import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

# Load dataset
heart_data = pd.read_csv('data/heart_disease_data.csv')

# Features and labels
X = heart_data.drop(columns='target', axis=1)
Y = heart_data['target']

# Split the dataset
X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=0.2, stratify=Y, random_state=42
)

# Standardize features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train model
model = RandomForestClassifier()
model.fit(X_train, Y_train)

# Save the model
with open('models/heart_model.pkl', 'wb') as f:
    pickle.dump(model, f)

# Save the scaler
with open('models/heart_scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

print("Heart model and scaler saved successfully.")
