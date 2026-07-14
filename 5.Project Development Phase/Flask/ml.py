import os
import pickle
import pandas as pd
from sqlalchemy.orm import Session

try:
    from app import crud, models
except ImportError:
    import crud, models

MODEL_PATHS = [
    "flood_model.pkl",
    "app/models/xgboost_flood_model.pkl",
    "../Flask/flood_model.pkl"
]

def get_prediction_model():
    for path in MODEL_PATHS:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    model = pickle.load(f)
                return model
            except Exception as e:
                print(f"Error loading model from {path}: {e}")
    return None

def predict_flood_risk(db: Session, reading_id: int, model_id: int):
    # 1. Fetch Sensor Reading
    reading = crud.get_sensor_reading(db, reading_id)
    if not reading:
        raise ValueError(f"Sensor reading with ID {reading_id} not found")
        
    # 2. Fetch Location details
    location = crud.get_location(db, reading.location_id)
    if not location:
        raise ValueError(f"Location with ID {reading.location_id} not found")
        
    # 3. Load model pipeline
    model_pipeline = get_prediction_model()
    if not model_pipeline:
        raise ValueError("Model binary file not found. Please run the training script first.")
        
    # 4. Build features DataFrame matching training columns
    data = {
        "location": [location.location_name],
        "water_level": [reading.water_level],
        "rainfall": [reading.rainfall],
        "temperature": [reading.temperature],
        "humidity": [reading.humidity],
        "river_flow": [reading.river_flow],
        "wind_speed": [reading.wind_speed]
    }
    
    df = pd.DataFrame(data)
    
    # 5. Run prediction
    try:
        prob = float(model_pipeline.predict_proba(df)[0][1]) # Class 1 (Flood) probability
    except Exception as e:
        # Fallback heuristic calculation if pipeline fails (for testing/safety)
        thresh = location.base_water_threshold
        val = 0.05
        if reading.water_level > thresh:
            val += 0.4 * (reading.water_level - thresh)
        if reading.rainfall > 60:
            val += 0.25
        prob = min(0.99, max(0.01, val))
        
    # 6. Map to human-readable outputs
    prob_percent = round(prob * 100, 2)
    
    if prob < 0.30:
        risk_level = "Low"
        alert = "Safe"
        recommendation = "Safe / No Action Required"
    elif prob < 0.70:
        risk_level = "Medium"
        alert = "Flood Watch"
        recommendation = "Monitor Closely & Move Valuables to Higher Ground"
    else:
        risk_level = "High"
        alert = "Flood Warning"
        recommendation = "Evacuate Low-Lying Areas Immediately"
        
    return risk_level, prob_percent, alert, recommendation
