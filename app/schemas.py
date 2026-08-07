from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class VitalObservation(BaseModel):
    timestamp: Optional[str] = Field(default=None, description="ISO timestamp string")
    heart_rate: Optional[float] = Field(default=None, description="Beats per minute")
    temperature: Optional[float] = Field(default=None, description="Body temperature in °C")
    oxygen_saturation: Optional[float] = Field(default=None, description="Blood oxygen SpO2 %")
    respiratory_rate: Optional[float] = Field(default=None, description="Breaths per minute")
    blood_pressure: Optional[float] = Field(default=None, description="Mean arterial/systolic BP")

class LabObservation(BaseModel):
    timestamp: Optional[str] = Field(default=None, description="ISO timestamp string")
    white_cell_count: Optional[float] = Field(default=None, description="WBC (10^9/L)")
    crp: Optional[float] = Field(default=None, description="C-reactive protein (mg/L)")
    lactate: Optional[float] = Field(default=None, description="Serum lactate (mmol/L)")
    creatinine: Optional[float] = Field(default=None, description="Serum creatinine (mg/dL)")
    platelet_count: Optional[float] = Field(default=None, description="Platelets (10^9/L)")

class SepsisPredictionRequest(BaseModel):
    patient_id: int = Field(..., example=101, description="Unique patient identifier")
    age: int = Field(..., example=65, description="Patient age in years")
    gender: str = Field(..., example="Male", description="Patient gender ('Male' or 'Female')")
    comorbidity_count: int = Field(default=0, example=2, description="Count of underlying medical conditions")
    vitals: List[VitalObservation] = Field(default=[], description="Series of recent vital sign observations")
    labs: List[LabObservation] = Field(default=[], description="Series of recent laboratory measurements")

class SepsisPredictionResponse(BaseModel):
    patient_id: int
    sepsis_risk_score: float
    risk_category: str
    prediction_window: str
    key_risk_factors: List[str]

class HealthCheckResponse(BaseModel):
    status: str
    service: str
    model_loaded: bool
    version: str
