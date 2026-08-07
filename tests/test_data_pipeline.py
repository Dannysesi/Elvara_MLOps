import pandas as pd
from src.data_pipeline import load_raw_data, clean_data

def test_load_and_clean_data():
    patients, vitals, history, labs, outcomes = load_raw_data()
    assert not patients.empty, "Patients table should not be empty"
    assert not vitals.empty, "Vitals table should not be empty"
    assert not history.empty, "Clinical history table should not be empty"
    assert not labs.empty, "Labs table should not be empty"
    assert not outcomes.empty, "Outcomes table should not be empty"

    p_c, v_c, h_c, l_c, o_c = clean_data(patients, vitals, history, labs, outcomes)
    
    # Check deduplication
    assert v_c.duplicated(subset=["patient_id", "timestamp"]).sum() == 0, "Vitals should have no duplicate timestamps per patient"
    assert l_c.duplicated(subset=["patient_id", "timestamp"]).sum() == 0, "Labs should have no duplicate timestamps per patient"

    # Range clamping check
    v_hr = v_c["heart_rate"].dropna()
    v_o2 = v_c["oxygen_saturation"].dropna()
    assert (v_hr >= 30).all() and (v_hr <= 220).all()
    assert (v_o2 >= 50).all() and (v_o2 <= 100).all()
