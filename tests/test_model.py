import os
import pytest
from src.train import train_and_evaluate_models
from src.predict import SepsisPredictor

def test_model_training_and_inference(tmp_path):
    models_dir = str(tmp_path / "models")
    data_dir = str(tmp_path / "data")
    
    meta = train_and_evaluate_models(models_dir=models_dir, data_dir=data_dir)
    assert meta["primary_metrics"]["roc_auc"] >= 0.55, "ROC-AUC should be at least 0.55"

    model_file = os.path.join(models_dir, "sepsis_model.joblib")
    assert os.path.exists(model_file)

    predictor = SepsisPredictor(model_path=model_file)
    sample_patient = {
        "patient_id": 888,
        "age": 72,
        "gender": "Female",
        "comorbidity_count": 3,
        "vitals": [
            {"heart_rate": 115.0, "temperature": 39.1, "oxygen_saturation": 91.0, "respiratory_rate": 26.0, "blood_pressure": 88.0}
        ],
        "labs": [
            {"white_cell_count": 18.5, "crp": 120.0, "lactate": 4.2, "creatinine": 2.1, "platelet_count": 110.0}
        ]
    }
    res = predictor.predict_patient(sample_patient)
    assert res["patient_id"] == 888
    assert res["risk_category"] in ["Low", "Moderate", "High"]
    assert 0.0 <= res["sepsis_risk_score"] <= 1.0
