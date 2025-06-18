import numpy as np
import pickle
from pathlib import Path

def predict_diabetes_disease(input_data: dict) -> int:
    """
    Predict diabetes probability using the trained model
    
    Args:
        input_data (dict): Dictionary containing patient data with the following keys:
            - pregnancies: int
            - glucose: float
            - blood_pressure: float
            - skin_thickness: float
            - insulin: float
            - bmi: float
            - diabetes_pedigree: float
            - age: int
    
    Returns:
        int: Prediction (1 for diabetic, 0 for not diabetic)
    """
    try:
        # Load the model, scaler, and feature list
        base_path = Path(__file__).parent.parent.parent
        model_path = base_path / 'models' / 'diabetes_model.pkl'
        scaler_path = base_path / 'models' / 'diabetes_scaler.pkl'
        features_path = base_path / 'models' / 'diabetes_features.pkl'
        
        # Check if files exist
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found at {model_path}")
        if not scaler_path.exists():
            raise FileNotFoundError(f"Scaler file not found at {scaler_path}")
        if not features_path.exists():
            raise FileNotFoundError(f"Features file not found at {features_path}")
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        with open(features_path, 'rb') as f:
            expected_features = pickle.load(f)
        
        # Map input data keys to expected feature names
        feature_mapping = {
            'pregnancies': 'Pregnancies',
            'glucose': 'Glucose',
            'blood_pressure': 'BloodPressure',
            'skin_thickness': 'SkinThickness',
            'insulin': 'Insulin',
            'bmi': 'BMI',
            'diabetes_pedigree': 'DiabetesPedigreeFunction',
            'age': 'Age'
        }
        
        # Convert input data to match expected feature names
        processed_data = {}
        for input_key, value in input_data.items():
            if input_key in feature_mapping:
                processed_data[feature_mapping[input_key]] = value
        
        # Ensure all expected features are present
        for feature in expected_features:
            if feature not in processed_data:
                raise ValueError(f"Missing required feature: {feature}")
        
        # Convert input data to numpy array in the correct order
        features = np.array([[processed_data[feature] for feature in expected_features]])
        
        # Scale the features
        features_scaled = scaler.transform(features)
        
        # Make prediction
        prediction = model.predict(features_scaled)[0]
        
        return int(prediction)
        
    except Exception as e:
        print(f"Error in diabetes prediction: {str(e)}")
        raise