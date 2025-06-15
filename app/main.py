# main.py
from fastapi import FastAPI
from app.models.diabetes import predict_diabetes_disease
from app.schemas.diabetes import DiabetesInput
from app.schemas.heart_disease import HeartDiseaseInput
from app.models.heart_disease import predict_heart_disease
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow requests from your Angular app
origins = [
    "http://localhost:4200",  # Angular dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 👈 Allow your frontend
    allow_credentials=True,
    allow_methods=["*"],    # 👈 Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],    # 👈 Allow all headers
)

@app.get("/")
def welcome():
    return {"message": "Welcome to PreventWise Health Prediction API"}

@app.post("/predict")
def predict_diabetes(data: DiabetesInput):
    prediction = predict_diabetes_disease(data.dict())
    result = "The person IS diabetic" if prediction == 1 else "The person is NOT diabetic"
    return {
        "prediction": prediction,
        "result": result
    }

@app.post("/predict/heart")
def predict_heart(data: HeartDiseaseInput):
    prediction = predict_heart_disease(data.dict())
    result = "Heart Disease Detected" if prediction == 1 else "No Heart Disease Detected"
    return {
        "prediction": prediction,
        "result": result
    }
