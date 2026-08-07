import time
import os
import json
from fastapi import FastAPI, HTTPException, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.schemas import (
    SepsisPredictionRequest,
    SepsisPredictionResponse,
    HealthCheckResponse
)
from app.metrics import (
    PREDICTION_REQUESTS_TOTAL,
    PREDICTION_LATENCY_SECONDS,
    MODEL_LOADED_GAUGE
)
from src.predict import SepsisPredictor

app = FastAPI(
    title="Elvara Health | Early Sepsis Warning & Deterioration System",
    description="Machine Learning Operations (MLOps) & Clinical Decision Support System for 6-12h Sepsis Deterioration Prediction",
    version="1.0.0"
)

# Predictor instance
predictor = None

@app.on_event("startup")
def load_model():
    global predictor
    try:
        model_path = os.getenv("MODEL_PATH", "models/sepsis_model.joblib")
        predictor = SepsisPredictor(model_path=model_path)
        MODEL_LOADED_GAUGE.set(1)
        print(f"Successfully loaded Sepsis Model from {model_path}")
    except Exception as e:
        MODEL_LOADED_GAUGE.set(0)
        print(f"Error loading model during startup: {e}")

@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
def health_check():
    is_loaded = predictor is not None
    return HealthCheckResponse(
        status="healthy" if is_loaded else "degraded",
        service="elvara-sepsis-cdss",
        model_loaded=is_loaded,
        version="1.0.0"
    )

@app.post("/predict-risk", response_model=SepsisPredictionResponse, tags=["Prediction"])
def predict_risk(request: SepsisPredictionRequest):
    if predictor is None:
        raise HTTPException(status_code=503, detail="Sepsis ML Model not loaded.")

    start_time = time.time()
    try:
        patient_dict = request.dict()
        result = predictor.predict_patient(patient_dict)

        # Prometheus metrics recording
        latency = time.time() - start_time
        PREDICTION_LATENCY_SECONDS.observe(latency)
        PREDICTION_REQUESTS_TOTAL.labels(risk_category=result["risk_category"]).inc()

        return SepsisPredictionResponse(
            patient_id=result["patient_id"],
            sepsis_risk_score=result["sepsis_risk_score"],
            risk_category=result["risk_category"],
            prediction_window=result["prediction_window"],
            key_risk_factors=result["key_risk_factors"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/metrics", tags=["Monitoring"])
def metrics():
    """
    Exports Prometheus operational metrics.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/monitoring/drift-report", tags=["Monitoring"])
def generate_drift_report():
    """
    Executes Evidently AI data drift and quality report generation.
    """
    try:
        from monitoring.drift_monitor import run_drift_analysis
        report_path = run_drift_analysis()
        return {"status": "success", "report_path": report_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate drift report: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
