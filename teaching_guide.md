# Teaching Guide: Elvara Health Early Sepsis Warning & Deterioration System

This comprehensive teaching guide breaks down the architectural decisions, code design, data science methodologies, and MLOps engineering for the **Early Sepsis Warning & Deterioration System**.

---

## 🧭 Step 1: Project Structure Decisions (Why This Layout?)

### Unstructured vs Enterprise MLOps Structure
In ad-hoc data science projects, everything often lives in a single notebook or folder. In modern clinical AI and enterprise MLOps, this creates severe issues:
1. **Code Duplication**: Logic written in notebooks cannot be imported into production APIs.
2. **Data Leakage**: Processing entire datasets without strict temporal cutoffs introduces future information into model training.
3. **Deployment Failure**: Production servers cannot run raw `.ipynb` files efficiently.

### Enterprise Directory Layout
```
c:\Users\Leinad\Downloads\files\
├── data/                         # Isolated raw and processed data
│   ├── raw/                      # Immutable raw EHR CSVs
│   └── processed/                # Prepared sepsis_features.csv
├── notebooks/                    # Exploration and prototyping sandbox
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   └── 03_model_development.ipynb
├── src/                          # Production Python package (Core Engine)
│   ├── data_pipeline.py          # Ingestion & data cleaning
│   ├── feature_engineering.py    # Temporal 6h/24h lookback features
│   ├── train.py                  # ML model training & evaluation
│   └── predict.py                # Real-time inference & risk driver analysis
├── app/                          # Production FastAPI Microservice
│   ├── main.py                   # REST API routes
│   ├── schemas.py                # Pydantic data validation
│   └── metrics.py                # Prometheus metrics exporter
├── monitoring/                   # Evidently AI & Prometheus/Grafana
│   ├── drift_monitor.py          # Feature & prediction drift detection
│   └── prometheus.yml            # Metrics scraper config
├── docker/                       # Containerization & Orchestration
│   ├── Dockerfile.api
│   └── docker-compose.yml
├── tests/                        # Automated Pytest suite
└── models/                       # Versioned model artifacts
```

---

## 📓 Step 2: Notebooks (Exploration & Prototyping)

Notebooks serve as the **experimentation lab** to discover patterns before writing production modules:

1. **`01_data_exploration.ipynb`**:
   - Profile initial row counts across 5 core tables (`patients`, `vital_signs`, `clinical_history`, `laboratory_results`, `sepsis_outcomes`).
   - Check missingness percentages (~2.4% in vitals/labs) and clip unphysiological outliers (e.g. oxygen saturation clamped to [50%, 100%]).
   - Verify clinical signals (e.g., pre-sepsis heart rate mean is 95.7 bpm vs 78.4 bpm in non-sepsis).

2. **`02_feature_engineering.ipynb`**:
   - **Preventing Data Leakage**: In real clinical practice, we must predict sepsis **6 to 12 hours before onset**.
   - **Prediction Cutoff**: For sepsis patients, `prediction_time = diagnosis_time - 9 hours` (midpoint of 6-12h window). Only data recorded *before* `prediction_time` is used.

3. **`03_model_development.ipynb`**:
   - Compare candidate algorithms: Baseline `LogisticRegression` vs Primary `HistGradientBoostingClassifier`.
   - Evaluate ROC-AUC, Precision, Recall, and F1-score under imbalanced clinical prevalence (~12% sepsis rate).

---

## ⚙️ Step 3: The `src` Core Engine (Most Important)

The `src/` directory contains clean, modular Python modules reusable across training, testing, and production API serving.

### A. Data Ingestion & Cleaning (`src/data_pipeline.py`)
- **`load_raw_data(data_dir)`**: Ingests raw CSV tables with proper date parsing.
- **`clean_data(...)`**:
  - Deduplicates timestamp observations per patient.
  - Clamps physiological range extremes.
  - Cleans string fields in clinical history.

```python
def clean_data(patients, vitals, history, labs, outcomes):
    vitals_clean = vitals.drop_duplicates(subset=["patient_id", "timestamp"]).reset_index(drop=True)
    vitals_clean["heart_rate"] = vitals_clean["heart_rate"].clip(30, 220)
    vitals_clean["oxygen_saturation"] = vitals_clean["oxygen_saturation"].clip(50.0, 100.0)
    return patients, vitals_clean, history, labs, outcomes
```

### B. Temporal Feature Engineering (`src/feature_engineering.py`)
Extracts rich physiological signals strictly prior to the patient's cutoff:
- **Vital Sign Features (6-hour lookback)**: `mean`, `min`, `max`, `std`, `last`, `rate_per_hr` (e.g., SpO2 decline rate per hour).
- **Laboratory Features (24-hour lookback)**: `mean`, `last` (WBC, CRP, lactate, creatinine, platelets).
- **Static Patient Features**: `age`, `gender_Male` (one-hot), `comorbidity_count`.

```python
def extract_vital_features(vitals_df, patient_id, cutoff, lookback_hours=6.0):
    window = vitals_df[(vitals_df['patient_id'] == patient_id) & 
                       (vitals_df['timestamp'] <= cutoff) & 
                       (vitals_df['timestamp'] >= cutoff - pd.Timedelta(hours=lookback_hours))]
    # Computes mean, min, max, std, last, and rate_per_hr per vital sign
```

### C. Model Training & Evaluation (`src/train.py`)
- Split 600 patient feature rows (75% train / 25% test with stratify).
- Train `HistGradientBoostingClassifier` with `class_weight='balanced'` to handle imbalanced sepsis target.
- Evaluate ROC-AUC, Precision, Recall, F1-Score, and Confusion Matrix.
- Save trained payload (`model`, `feature_names`, `medians`) to `models/sepsis_model.joblib` and metrics metadata to `models/model_metadata.json`.

### D. Real-Time Inference Engine (`src/predict.py`)
- **`SepsisPredictor`**: Loads trained `.joblib` model artifact.
- Implements `predict_patient(patient_data)`:
  - Transforms raw API payload into identical feature vectors.
  - Imputes missing features using stored training medians.
  - Calculates probability score (0.0 to 1.0) and assigns `risk_category` (`Low`, `Moderate`, `High`).
  - Generates **Explainable AI Clinical Drivers** (e.g. "Elevated Serum Lactate (3.4 mmol/L)").

---

## 🌐 Step 4: Building the FastAPI Microservice (`app/`)

### A. Data Validation Schemas (`app/schemas.py`)
Uses Pydantic models to strictly enforce type checking for incoming JSON patient records.

```python
class SepsisPredictionRequest(BaseModel):
    patient_id: int
    age: int
    gender: str
    comorbidity_count: int = 0
    vitals: List[VitalObservation] = []
    labs: List[LabObservation] = []
```

### B. Observability & Metrics (`app/metrics.py`)
Defines Prometheus counters and histograms to track API throughput and model inference latency in production:
- `PREDICTION_REQUESTS_TOTAL`: Counter labeled by `risk_category`.
- `PREDICTION_LATENCY_SECONDS`: Histogram measuring prediction latency in seconds.

### C. API Endpoints (`app/main.py`)
- `@app.on_event("startup")`: Loads model payload into memory on API launch.
- `GET /health`: Health and readiness probe for load balancers.
- `POST /predict-risk`: Main endpoint consuming patient observations and returning risk assessment.
- `GET /metrics`: Exports Prometheus formatted telemetry.

---

## 🧪 Step 5: Testing Suite (`tests/`)

Automated Pytest suite ensures regression safety:
- **`test_data_pipeline.py`**: Verifies zero duplicate timestamps and range clamping.
- **`test_features.py`**: Ensures feature matrix contains zero nulls and correct shape.
- **`test_model.py`**: Tests end-to-end model training, file persistence, and predictor scoring.
- **`test_api.py`**: Verifies FastAPI HTTP status codes and JSON response structures.

---

## 📊 Step 6: MLOps Monitoring & Deployment (`monitoring/` & `docker/`)

1. **Evidently AI (`monitoring/drift_monitor.py`)**:
   - Calculates Kolmogorov-Smirnov statistical tests and Evidently AI reports comparing real-time operational inference inputs against reference training data to detect **feature drift** and **data quality degradation**.
2. **Prometheus & Grafana (`monitoring/prometheus.yml`)**:
   - Prometheus scrapes `/metrics` every 15 seconds.
   - Grafana renders clinical risk category distributions and API response times on interactive dashboards.
3. **Containerization (`docker/Dockerfile.api` & `docker-compose.yml`)**:
   - Dockerizes the application environment so it runs identically across local, staging, and cloud production environments.
