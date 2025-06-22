# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.models.diabetes import predict_diabetes_disease
from app.schemas.diabetes import DiabetesInput
from app.schemas.heart_disease import HeartDiseaseInput
from app.models.heart_disease import predict_heart_disease
from app.schemas.stroke import StrokeInput
from app.models.stroke import predict_stroke
from fastapi.middleware.cors import CORSMiddleware

from app.auth import auth, models, schemas
from app.auth.database import SessionLocal, engine, get_db

models.Base.metadata.create_all(bind=engine)

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

@app.post("/signup", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = auth.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.get_user(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
def welcome():
    return {"message": "Welcome to PreventWise Health Prediction API"}

@app.post("/predict")
def predict_diabetes(data: DiabetesInput, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    prediction = predict_diabetes_disease(data.dict())
    result = "The person IS diabetic" if prediction == 1 else "The person is NOT diabetic"
    
    history_entry = models.PredictionHistory(
        owner_id=current_user.id,
        prediction_type="diabetes",
        prediction_result=result,
        prediction_value=prediction
    )
    db.add(history_entry)
    db.commit()

    return {
        "prediction": prediction,
        "result": result
    }

@app.post("/predict/heart")
def predict_heart(data: HeartDiseaseInput, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    prediction = predict_heart_disease(data.dict())
    result = "Heart Disease Detected" if prediction == 1 else "No Heart Disease Detected"
    
    history_entry = models.PredictionHistory(
        owner_id=current_user.id,
        prediction_type="heart_disease",
        prediction_result=result,
        prediction_value=prediction
    )
    db.add(history_entry)
    db.commit()
    
    return {
        "prediction": prediction,
        "result": result
    }

@app.post("/predict/stroke")
def predict_stroke_risk(data: StrokeInput, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    prediction = predict_stroke(data.dict())
    result = "High Risk of Stroke" if prediction == 1 else "Low Risk of Stroke"

    history_entry = models.PredictionHistory(
        owner_id=current_user.id,
        prediction_type="stroke",
        prediction_result=result,
        prediction_value=prediction
    )
    db.add(history_entry)
    db.commit()

    return {
        "prediction": prediction,
        "result": result
    }

@app.get("/history", response_model=list[schemas.PredictionHistory])
def get_prediction_history(db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    return db.query(models.PredictionHistory).filter(models.PredictionHistory.owner_id == current_user.id).all()
