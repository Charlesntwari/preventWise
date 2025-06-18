from pydantic import BaseModel, Field

class StrokeInput(BaseModel):
    age: float = Field(..., ge=0, le=120, description="Age of the patient")
    hypertension: int = Field(..., ge=0, le=1, description="Hypertension status (1 for yes, 0 for no)")
    heart_disease: int = Field(..., ge=0, le=1, description="Heart disease status (1 for yes, 0 for no)")
    avg_glucose_level: float = Field(..., ge=0, description="Average glucose level in blood")
    bmi: float = Field(..., ge=0, description="Body Mass Index")
    gender_Male: int = Field(..., ge=0, le=1, description="Gender (1 for male, 0 for female)")
    ever_married_Yes: int = Field(..., ge=0, le=1, description="Marriage status (1 for yes, 0 for no)")
    work_type_Never_worked: int = Field(..., ge=0, le=1, description="Work type: Never worked")
    work_type_Private: int = Field(..., ge=0, le=1, description="Work type: Private")
    work_type_Self_employed: int = Field(..., ge=0, le=1, description="Work type: Self-employed")
    work_type_children: int = Field(..., ge=0, le=1, description="Work type: Children")
    Residence_type_Urban: int = Field(..., ge=0, le=1, description="Residence type (1 for urban, 0 for rural)")
    smoking_status_formerly_smoked: int = Field(..., ge=0, le=1, description="Smoking status: Formerly smoked")
    smoking_status_never_smoked: int = Field(..., ge=0, le=1, description="Smoking status: Never smoked")
    smoking_status_smokes: int = Field(..., ge=0, le=1, description="Smoking status: Currently smokes") 