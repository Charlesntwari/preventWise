import numpy as np
import pickle
import os

# Load the model
model_path = os.path.join("models", "heart_model.pkl")
scaler_path = os.path.join("models", "heart_scaler.pkl")

with open(model_path, "rb") as f:
    model = pickle.load(f)

with open(scaler_path, "rb") as f:
    scaler = pickle.load(f)

def predict_heart_disease(input_data):
    input_array = np.asarray(list(input_data.values())).reshape(1, -1)
    scaled_input = scaler.transform(input_array)
    prediction = model.predict(scaled_input)
    return int(prediction[0])
