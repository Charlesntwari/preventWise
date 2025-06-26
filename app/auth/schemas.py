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
    is_admin: int = 0

class User(UserBase):
    id: int
    predictions: List[PredictionHistory] = []
    is_admin: int = 0

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ContactMessageCreate(BaseModel):
    name: str
    subject: str
    message: str

class ContactMessage(ContactMessageCreate):
    id: int
    email: str
    timestamp: datetime.datetime
    class Config:
        orm_mode = True

