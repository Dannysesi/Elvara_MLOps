import os
import pandas as pd
import numpy as np

def load_raw_data(data_dir: str = "data/raw"):
    """
    Loads raw CSV tables for Elvara Health Early Sepsis System.
    Falls back to current working directory if data/raw does not exist yet.
    """
    if not os.path.exists(data_dir) and os.path.exists("patients.csv"):
        data_dir = "."

    patients_path = os.path.join(data_dir, "patients.csv")
    vitals_path = os.path.join(data_dir, "vital_signs.csv")
    history_path = os.path.join(data_dir, "clinical_history.csv")
    labs_path = os.path.join(data_dir, "laboratory_results.csv")
    outcomes_path = os.path.join(data_dir, "sepsis_outcomes.csv")

    patients = pd.read_csv(patients_path, parse_dates=["registration_date"])
    vitals = pd.read_csv(vitals_path, parse_dates=["timestamp"])
    history = pd.read_csv(history_path)
    labs = pd.read_csv(labs_path, parse_dates=["timestamp"])
    outcomes = pd.read_csv(outcomes_path, parse_dates=["diagnosis_time"])

    return patients, vitals, history, labs, outcomes

def clean_data(patients: pd.DataFrame,
               vitals: pd.DataFrame,
               history: pd.DataFrame,
               labs: pd.DataFrame,
               outcomes: pd.DataFrame):
    """
    Applies data quality controls, deduplication, and sanity range checks.
    """
    patients_clean = patients.copy()
    vitals_clean = vitals.copy()
    history_clean = history.copy()
    labs_clean = labs.copy()
    outcomes_clean = outcomes.copy()

    # 1. Deduplicate vital signs & laboratory timestamp pairs per patient
    vitals_clean = vitals_clean.drop_duplicates(subset=["patient_id", "timestamp"]).reset_index(drop=True)
    labs_clean = labs_clean.drop_duplicates(subset=["patient_id", "timestamp"]).reset_index(drop=True)

    # 2. Physiological range checks / clamping
    # Vitals
    vitals_clean["heart_rate"] = vitals_clean["heart_rate"].clip(30, 220)
    vitals_clean["temperature"] = vitals_clean["temperature"].clip(32.0, 43.0)
    vitals_clean["oxygen_saturation"] = vitals_clean["oxygen_saturation"].clip(50.0, 100.0)
    vitals_clean["respiratory_rate"] = vitals_clean["respiratory_rate"].clip(5, 60)
    vitals_clean["blood_pressure"] = vitals_clean["blood_pressure"].clip(40, 220)

    # Labs
    labs_clean["white_cell_count"] = labs_clean["white_cell_count"].clip(0.1, 50.0)
    labs_clean["crp"] = labs_clean["crp"].clip(0.0, 500.0)
    labs_clean["lactate"] = labs_clean["lactate"].clip(0.1, 20.0)
    labs_clean["creatinine"] = labs_clean["creatinine"].clip(0.1, 10.0)
    labs_clean["platelet_count"] = labs_clean["platelet_count"].clip(5.0, 700.0)

    # 3. Clean clinical history string fields
    history_clean["diagnosis_history"] = history_clean["diagnosis_history"].fillna("None")
    history_clean["infection_history"] = history_clean["infection_history"].fillna("None")
    history_clean["medication_history"] = history_clean["medication_history"].fillna("None")
    history_clean["treatment_history"] = history_clean["treatment_history"].fillna("None")

    return patients_clean, vitals_clean, history_clean, labs_clean, outcomes_clean

if __name__ == "__main__":
    patients, vitals, history, labs, outcomes = load_raw_data()
    p_c, v_c, h_c, l_c, o_c = clean_data(patients, vitals, history, labs, outcomes)
    print(f"Cleaned Patients: {p_c.shape}")
    print(f"Cleaned Vitals:   {v_c.shape}")
    print(f"Cleaned History:  {h_c.shape}")
    print(f"Cleaned Labs:     {l_c.shape}")
    print(f"Cleaned Outcomes: {o_c.shape}")
