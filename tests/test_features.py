import pandas as pd
import numpy as np
from src.data_pipeline import load_raw_data, clean_data
from src.feature_engineering import get_prediction_times, extract_vital_features, build_feature_matrix

def test_feature_engineering_pipeline():
    patients, vitals, history, labs, outcomes = clean_data(*load_raw_data())

    # Limit to small subset for fast testing
    patients_sub = patients.head(20)
    outcomes_sub = outcomes[outcomes['patient_id'].isin(patients_sub['patient_id'])]
    vitals_sub = vitals[vitals['patient_id'].isin(patients_sub['patient_id'])]
    labs_sub = labs[labs['patient_id'].isin(patients_sub['patient_id'])]

    feat_matrix = build_feature_matrix(patients_sub, vitals_sub, labs_sub, outcomes_sub)
    assert not feat_matrix.empty, "Feature matrix should not be empty"
    assert "sepsis_event" in feat_matrix.columns
    assert "heart_rate_mean" in feat_matrix.columns
    assert "lactate_last" in feat_matrix.columns
    assert feat_matrix.isna().sum().sum() == 0, "Feature matrix should contain no null values"
