# Elvara Health | Early Sepsis Warning & Deterioration System

A production-ready Machine Learning Operations (MLOps) and Clinical Decision Support System (CDSS) designed to identify patients at risk of developing sepsis within a **6–12 hour prediction window**.

---

## 🏥 Architecture Overview

```
                        +--------------------------------+
                        |   Elvara Health Platform       |
                        |   (EHR / Vitals / Labs)        |
                        +---------------+----------------+
                                        |
                                        v
                        +---------------+----------------+
                        |  Data Preprocessing &          |
                        |  Temporal Feature Engine       |
                        +---------------+----------------+
                                        |
                                        v
                        +---------------+----------------+
                        |  HistGradientBoosting Model    |
                        |  (Sepsis Risk Scorer 6-12h)   |
                        +---------------+----------------+
                                        |
                   +--------------------+--------------------+
                   |                                         |
                   v                                         v
    +--------------+---------------+         +---------------+---------------+
    |  FastAPI CDSS Microservice   |         |   Evidently AI & Prometheus   |
    |  POST /predict-risk          |         |   Drift & Ops Monitoring      |
    +------------------------------+         +-------------------------------+
```

---

## 📁 Repository Structure

```
├── elvara/                       # Virtual environment
├── data/
│   ├── raw/                      # Patients, vitals, labs, history, outcomes CSVs
│   └── processed/                # Engineered sepsis_features.csv
├── notebooks/                    # Interactive analysis & exploration notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   └── 03_model_development.ipynb
├── src/                          # Core Python logic
│   ├── data_pipeline.py          # Data ingestion & cleaning
│   ├── feature_engineering.py    # Temporal 6h vital / 24h lab feature extraction
│   ├── train.py                  # Model training (HistGradientBoosting vs LogisticRegression)
│   └── predict.py                # Inference engine & clinical risk driver analysis
├── app/                          # Production FastAPI Application
│   ├── main.py                   # FastAPI app routes
│   ├── schemas.py                # Pydantic data validation schemas
│   └── metrics.py                # Prometheus metrics counters & histograms
├── monitoring/                   # Evidently AI & Prometheus/Grafana Configuration
│   ├── drift_monitor.py          # Evidently AI drift & data quality calculation
│   ├── prometheus.yml            # Prometheus scrape config
│   └── reports/                  # Generated HTML drift reports
├── models/                       # Model artifacts & metadata
│   ├── sepsis_model.joblib
│   └── model_metadata.json
├── docker/                       # Docker containerization
│   ├── Dockerfile.api
│   └── docker-compose.yml        # Orchestrates API, Prometheus, and Grafana
├── tests/                        # Unit & integration test suite
│   ├── test_data_pipeline.py
│   ├── test_features.py
│   ├── test_model.py
│   └── test_api.py
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### 1. Environment Setup

```powershell
# Create elvara virtual environment
python -m venv elvara

# Activate virtual environment
.\elvara\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### 2. Run Data Pipeline & Train ML Model

```powershell
.\elvara\Scripts\python.exe -m src.train
```

Outputs:
- Primary Model (`HistGradientBoostingClassifier`) & Baseline (`LogisticRegression`) metrics.
- Saved model payload at `models/sepsis_model.joblib`.
- Saved metadata at `models/model_metadata.json`.

### 3. Launch FastAPI Prediction Microservice

```powershell
.\elvara\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload
```

Endpoints:
- **Swagger Documentation**: `http://localhost:8000/docs`
- **Health Check**: `GET http://localhost:8000/health`
- **Real-Time Risk Prediction**: `POST http://localhost:8000/predict-risk`
- **Prometheus Metrics**: `GET http://localhost:8000/metrics`
- **Evidently Drift Trigger**: `POST http://localhost:8000/monitoring/drift-report`

### 4. Sample Prediction Request

```json
POST /predict-risk
{
  "patient_id": 101,
  "age": 68,
  "gender": "Male",
  "comorbidity_count": 2,
  "vitals": [
    {
      "heart_rate": 108.5,
      "temperature": 38.6,
      "oxygen_saturation": 93.5,
      "respiratory_rate": 24.0,
      "blood_pressure": 96.0
    }
  ],
  "labs": [
    {
      "white_cell_count": 15.1,
      "crp": 92.0,
      "lactate": 3.4,
      "creatinine": 1.9,
      "platelet_count": 135.0
    }
  ]
}
```

### 5. Launch Monitoring Stack via Docker Compose

```powershell
docker-compose -f docker/docker-compose.yml up --build
```

Services:
- **FastAPI Endpoint**: `http://localhost:8000`
- **Prometheus UI**: `http://localhost:9090`
- **Grafana Dashboard**: `http://localhost:3000` (User: `admin`, Pass: `admin`)

### 6. Run Unit & Integration Tests

```powershell
.\elvara\Scripts\pytest.exe
```

---

## 📊 Key Clinical Features & Metrics

| Metric | Target Window |
|---|---|
| **Prediction Window** | 6–12 Hours Prior to Sepsis Onset |
| **Primary Model** | `HistGradientBoostingClassifier` (Class Weighted) |
| **Baseline Model** | `LogisticRegression` |
| **Vital Lookback** | 6 Hours (`mean`, `min`, `max`, `std`, `rate_per_hr`) |
| **Lab Lookback** | 24 Hours (`mean`, `last`) |
