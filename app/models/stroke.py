import pickle
import numpy as np
from pathlib import Path

def predict_stroke(data: dict) -> int:
    """
    Predict stroke probability using the trained model
    
    Args:
        data (dict): Dictionary containing patient data with the following keys:
            - age: float
            - hypertension: int (0 or 1)
            - heart_disease: int (0 or 1)
            - avg_glucose_level: float
            - bmi: float
            - gender_Male: int (0 or 1)
            - ever_married_Yes: int (0 or 1)
            - work_type_Never_worked: int (0 or 1)
            - work_type_Private: int (0 or 1)
            - work_type_Self_employed: int (0 or 1)
            - work_type_children: int (0 or 1)
            - Residence_type_Urban: int (0 or 1)
            - smoking_status_formerly_smoked: int (0 or 1)
            - smoking_status_never_smoked: int (0 or 1)
            - smoking_status_smokes: int (0 or 1)
    
    Returns:
        int: Prediction (1 for stroke, 0 for no stroke)
    """
    try:
        # Load the model, scaler, and feature list
        model_path = Path(__file__).parent.parent.parent / 'models' / 'stroke_model.pkl'
        scaler_path = Path(__file__).parent.parent.parent / 'models' / 'stroke_scaler.pkl'
        features_path = Path(__file__).parent.parent.parent / 'models' / 'stroke_features.pkl'
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        with open(features_path, 'rb') as f:
            expected_features = pickle.load(f)
        
        # Ensure all expected features are present in the input data
        for feature in expected_features:
            if feature not in data:
                data[feature] = 0
        
        # Convert input data to numpy array in the correct order
        features = np.array([[data[feature] for feature in expected_features]])
        
        # Scale the features
        features_scaled = scaler.transform(features)
        
        # Make prediction with adjusted threshold
        prediction_proba = model.predict_proba(features_scaled)[0][1]
        prediction = 1 if prediction_proba > 0.3 else 0
        
        return prediction
        
    except Exception as e:
        print(f"Error in stroke prediction: {str(e)}")
        raise 