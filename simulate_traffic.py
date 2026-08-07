import time
import random
import httpx

API_URL = "http://localhost:8080/predict-risk"

def generate_random_patient(pid: int):
    # Randomize clinical vitals to simulate diverse patient deterioration states
    is_high_risk = random.random() < 0.35
    if is_high_risk:
        hr = random.uniform(100.0, 135.0)
        temp = random.uniform(38.5, 40.2)
        spo2 = random.uniform(88.0, 93.0)
        resp = random.uniform(22.0, 30.0)
        bp = random.uniform(80.0, 95.0)
        wbc = random.uniform(14.0, 22.0)
        crp = random.uniform(70.0, 150.0)
        lactate = random.uniform(2.5, 5.0)
    else:
        hr = random.uniform(65.0, 85.0)
        temp = random.uniform(36.4, 37.2)
        spo2 = random.uniform(97.0, 100.0)
        resp = random.uniform(12.0, 18.0)
        bp = random.uniform(110.0, 130.0)
        wbc = random.uniform(5.0, 9.5)
        crp = random.uniform(1.0, 8.0)
        lactate = random.uniform(0.8, 1.4)

    return {
        "patient_id": pid,
        "age": random.randint(35, 85),
        "gender": random.choice(["Male", "Female"]),
        "comorbidity_count": random.randint(0, 4),
        "vitals": [
            {
                "heart_rate": round(hr, 1),
                "temperature": round(temp, 1),
                "oxygen_saturation": round(spo2, 1),
                "respiratory_rate": round(resp, 1),
                "blood_pressure": round(bp, 1)
            }
        ],
        "labs": [
            {
                "white_cell_count": round(wbc, 1),
                "crp": round(crp, 1),
                "lactate": round(lactate, 2),
                "creatinine": round(random.uniform(0.8, 2.2), 2),
                "platelet_count": round(random.uniform(120.0, 350.0), 1)
            }
        ]
    }

def main(total_requests: int = 30):
    print(f"--- Generating {total_requests} real-time sepsis prediction requests to populate Grafana & Prometheus dashboards ---")
    client = httpx.Client(timeout=10.0)
    
    for i in range(1, total_requests + 1):
        patient = generate_random_patient(pid=1000 + i)
        try:
            r = client.post(API_URL, json=patient)
            if r.status_code == 200:
                data = r.json()
                print(f"[{i}/{total_requests}] Patient #{data['patient_id']} -> Score: {data['sepsis_risk_score']:.4f} | Category: {data['risk_category']}")
            else:
                print(f"[{i}/{total_requests}] Request failed with code {r.status_code}")
        except Exception as e:
            print(f"[{i}/{total_requests}] Error sending request: {e}")
        
        time.sleep(0.3)

    print("\n--- Simulation complete! Prometheus metrics updated. ---")

if __name__ == "__main__":
    main()
