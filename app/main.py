# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func

from app.models.diabetes import predict_diabetes_disease
from app.schemas.diabetes import DiabetesInput
from app.schemas.heart_disease import HeartDiseaseInput
from app.models.heart_disease import predict_heart_disease
from app.schemas.stroke import StrokeInput
from app.models.stroke import predict_stroke
from fastapi.middleware.cors import CORSMiddleware

from app.auth import auth, models, schemas
from app.auth.database import SessionLocal, engine, get_db
from app.auth.schemas import ContactMessageCreate

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
    db_user = models.User(email=user.email, hashed_password=hashed_password, is_admin=user.is_admin)
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
    access_token = auth.create_access_token(data={"sub": user.email, "is_admin": user.is_admin})
    return {"access_token": access_token, "token_type": "bearer", "is_admin": user.is_admin}

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

@app.delete("/history")
def delete_prediction_history(db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    deleted = db.query(models.PredictionHistory).filter(models.PredictionHistory.owner_id == current_user.id).delete()
    db.commit()
    return {"deleted": deleted, "message": "All prediction history deleted for current user."}

def is_admin_user(current_user: schemas.User):
    return current_user.email == "ntwarichar@gmail.com" or getattr(current_user, 'is_admin', 0) == 1

@app.get("/admin/users-with-disease/{disease_type}")
def get_users_with_disease(disease_type: str, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    if not is_admin_user(current_user):
        raise HTTPException(status_code=403, detail="Not authorized")
    # Find all users who have at least one prediction of the given disease_type and prediction_result indicating disease
    if disease_type == "diabetes":
        result_str = "The person IS diabetic"
    elif disease_type == "heart_disease":
        result_str = "Heart Disease Detected"
    elif disease_type == "stroke":
        result_str = "High Risk of Stroke"
    else:
        raise HTTPException(status_code=400, detail="Invalid disease type")
    user_ids = db.query(models.PredictionHistory.owner_id).filter(models.PredictionHistory.prediction_type == disease_type, models.PredictionHistory.prediction_result == result_str).distinct()
    users = db.query(models.User).filter(models.User.id.in_(user_ids)).all()
    return users

@app.get("/admin/users")
def admin_get_all_users(db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    if not is_admin_user(current_user):
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(models.User).all()

@app.delete("/admin/users/{user_id}")
def admin_delete_user(user_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    if not is_admin_user(current_user):
        raise HTTPException(status_code=403, detail="Not authorized")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.query(models.PredictionHistory).filter(models.PredictionHistory.owner_id == user_id).delete()
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} and their predictions deleted."}

@app.get("/admin/predictions")
def admin_get_all_predictions(db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    if not is_admin_user(current_user):
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(models.PredictionHistory).all()

@app.get("/admin/stats")
def admin_stats(db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    if not is_admin_user(current_user):
        raise HTTPException(status_code=403, detail="Not authorized")
    total_users = db.query(models.User).count()
    total_predictions = db.query(models.PredictionHistory).count()
    diabetes_predictions = db.query(models.PredictionHistory).filter(models.PredictionHistory.prediction_type == "diabetes").count()
    heart_predictions = db.query(models.PredictionHistory).filter(models.PredictionHistory.prediction_type == "heart_disease").count()
    stroke_predictions = db.query(models.PredictionHistory).filter(models.PredictionHistory.prediction_type == "stroke").count()
    return {
        "total_users": total_users,
        "total_predictions": total_predictions,
        "diabetes_predictions": diabetes_predictions,
        "heart_predictions": heart_predictions,
        "stroke_predictions": stroke_predictions,
    }

@app.post("/contact")
def create_contact_message(
    data: ContactMessageCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    message = models.ContactMessage(
        name=data.name,
        email=current_user.email,
        subject=data.subject,
        message=data.message,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return {"message": "Contact message sent successfully"}

@app.get("/admin/messages")
def get_all_messages(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    if not is_admin_user(current_user):
        raise HTTPException(status_code=403, detail="Not authorized")
    messages = db.query(models.ContactMessage).order_by(models.ContactMessage.timestamp.desc()).all()
    return [
        {
            "id": m.id,
            "name": m.name,
            "email": m.email,
            "subject": m.subject,
            "message": m.message,
            "timestamp": m.timestamp,
        }
        for m in messages
    ]
