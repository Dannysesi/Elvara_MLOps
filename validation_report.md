# Sepsis Dataset Validation Report

Generated for Elvara Health Early Sepsis Warning & Deterioration System case study.

**Summary: 47 PASS, 0 FAIL, 2 WARN, 3 INFO**

| Row counts | |
|---|---|
| patients | 600 |
| vital_signs | 11807 |
| clinical_history | 1449 |
| laboratory_results | 2430 |
| sepsis_outcomes | 600 |

## Checks

- [PASS] PK uniqueness: patients.patient_id duplicates = 0
- [PASS] PK uniqueness: vital_signs.observation_id duplicates = 0
- [PASS] PK uniqueness: clinical_history.history_id duplicates = 0
- [PASS] PK uniqueness: laboratory_results.lab_id duplicates = 0
- [PASS] PK uniqueness: sepsis_outcomes.outcome_id duplicates = 0
- [PASS] Referential integrity: vital_signs.patient_id orphan rows = 0
- [PASS] Referential integrity: clinical_history.patient_id orphan rows = 0
- [PASS] Referential integrity: laboratory_results.patient_id orphan rows = 0
- [PASS] Referential integrity: sepsis_outcomes.patient_id orphan rows = 0
- [PASS] Cardinality: vital_signs per patient: min=10, max=30, mean=19.7 (expected 1:N, >=1)
- [PASS] Cardinality: laboratory_results per patient: min=2, max=6, mean=4.0 (expected 1:N)
- [PASS] Cardinality: clinical_history per patient: min=1, max=4 (expected 1:N)
- [PASS] Cardinality: sepsis_outcomes per patient: max=1 (expected 1:1)
- [PASS] Missingness: vital_signs.heart_rate = 2.68% missing
- [PASS] Missingness: vital_signs.temperature = 2.48% missing
- [PASS] Missingness: vital_signs.oxygen_saturation = 2.43% missing
- [PASS] Missingness: vital_signs.respiratory_rate = 2.44% missing
- [PASS] Missingness: vital_signs.blood_pressure = 2.22% missing
- [PASS] Missingness: laboratory_results.white_cell_count = 2.92% missing
- [PASS] Missingness: laboratory_results.crp = 2.47% missing
- [PASS] Missingness: laboratory_results.lactate = 3.05% missing
- [PASS] Missingness: laboratory_results.creatinine = 3.42% missing
- [PASS] Missingness: laboratory_results.platelet_count = 3.00% missing
- [PASS] Missingness: patients key fields missing = 0
- [PASS] Range check: vital_signs.heart_rate outside plausible [30,220] = 0
- [PASS] Range check: vital_signs.temperature outside plausible [32,43] = 0
- [PASS] Range check: vital_signs.oxygen_saturation outside plausible [50,100] = 0
- [PASS] Range check: vital_signs.respiratory_rate outside plausible [5,60] = 0
- [PASS] Range check: vital_signs.blood_pressure outside plausible [40,220] = 0
- [PASS] Range check: laboratory_results.white_cell_count outside plausible [0.1,50] = 0
- [PASS] Range check: laboratory_results.crp outside plausible [0,500] = 0
- [PASS] Range check: laboratory_results.lactate outside plausible [0.1,20] = 0
- [PASS] Range check: laboratory_results.creatinine outside plausible [0.1,10] = 0
- [PASS] Range check: laboratory_results.platelet_count outside plausible [5,700] = 0
- [PASS] Range check: patients.age outside [0,110] = 0
- [PASS] Temporal logic: vital_signs recorded before patient registration_date = 0
- [PASS] Temporal logic: laboratory_results recorded before patient registration_date = 0
- [PASS] Temporal logic: sepsis diagnosis_time before registration_date = 0
- [PASS] Logical consistency: sepsis_event=True rows missing diagnosis_time = 0
- [PASS] Logical consistency: sepsis_event=False rows with a diagnosis_time set = 0
- [WARN] Duplicates: vital_signs duplicate (patient_id, timestamp) pairs = 34
- [WARN] Duplicates: laboratory_results duplicate (patient_id, timestamp) pairs = 1
- [PASS] Class balance: sepsis_event prevalence = 12.0% (target ~12%, clinically plausible for monitored acute/ICU population)
- [PASS] Clinical signal: vital_signs.heart_rate: pre-sepsis(0-12h) mean=95.7 vs non-sepsis mean=78.4 (expected higher in pre-sepsis)
- [PASS] Clinical signal: vital_signs.respiratory_rate: pre-sepsis(0-12h) mean=20.9 vs non-sepsis mean=16.1 (expected higher in pre-sepsis)
- [PASS] Clinical signal: vital_signs.oxygen_saturation: pre-sepsis(0-12h) mean=94.9 vs non-sepsis mean=97.5 (expected lower in pre-sepsis)
- [PASS] Clinical signal: vital_signs.blood_pressure: pre-sepsis(0-12h) mean=108.4 vs non-sepsis mean=122.5 (expected lower in pre-sepsis)
- [INFO] Clinical signal: laboratory_results.lactate: pre-sepsis(0-12h) mean=2.33 vs non-sepsis mean=1.00
- [INFO] Clinical signal: laboratory_results.crp: pre-sepsis(0-12h) mean=63.41 vs non-sepsis mean=6.08
- [INFO] Clinical signal: laboratory_results.white_cell_count: pre-sepsis(0-12h) mean=10.61 vs non-sepsis mean=7.54
- [PASS] Outcome logic: hospitalisation_required rate: sepsis=88.9% vs non-sepsis=15.2%
- [PASS] Outcome logic: Deceased rate: sepsis=8.3% vs non-sepsis=0.0%
