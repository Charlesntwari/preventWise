from pydantic import BaseModel
from typing import List, Optional
import datetime

class PredictionHistoryBase(BaseModel):
    prediction_type: str
    prediction_result: str
    prediction_value: float

class PredictionHistoryCreate(PredictionHistoryBase):
    pass

class PredictionHistory(PredictionHistoryBase):
    id: int
    owner_id: int
    timestamp: datetime.datetime

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    predictions: List[PredictionHistory] = []

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

