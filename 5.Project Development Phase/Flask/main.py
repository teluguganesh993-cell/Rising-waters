from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
import sys

# Ensure import paths resolve correctly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from app import models, schemas, crud, ml
    from app.database import engine, get_db
except ImportError:
    import models, schemas, crud, ml
    from database import engine, get_db

# Create SQLite Database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Rising Waters Flood Alert API", version="1.0.0")

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- USER ENDPOINTS ---
@app.post("/api/users", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/api/users", response_model=List[schemas.UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)

# --- LOCATION ENDPOINTS ---
@app.post("/api/locations", response_model=schemas.LocationResponse)
def create_location(location: schemas.LocationCreate, db: Session = Depends(get_db)):
    db_loc = crud.get_location_by_name(db, name=location.location_name)
    if db_loc:
        raise HTTPException(status_code=400, detail="Location name already registered")
    return crud.create_location(db=db, location=location)

@app.get("/api/locations", response_model=List[schemas.LocationResponse])
def read_locations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_locations(db, skip=skip, limit=limit)

# --- SENSOR READING ENDPOINTS ---
@app.post("/api/readings", response_model=schemas.SensorReadingResponse)
def create_reading(reading: schemas.SensorReadingCreate, db: Session = Depends(get_db)):
    loc = crud.get_location(db, reading.location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return crud.create_sensor_reading(db=db, reading=reading)

@app.get("/api/readings", response_model=List[schemas.SensorReadingResponse])
def read_readings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_sensor_readings(db, skip=skip, limit=limit)

# --- MODEL ENDPOINTS ---
@app.get("/api/models", response_model=List[schemas.ModelResponse])
def read_models(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_models(db, skip=skip, limit=limit)

# --- PREDICTION ENDPOINTS ---
@app.post("/api/predictions/run", response_model=schemas.PredictionResultResponse)
def run_prediction(req: schemas.FloodPredictionRequest, db: Session = Depends(get_db)):
    try:
        risk_lvl, prob_score, alert_val, rec_val = ml.predict_flood_risk(db, req.reading_id, req.model_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    prediction_in = schemas.PredictionResultCreate(
        reading_id=req.reading_id,
        model_id=req.model_id,
        risk_level=risk_lvl,
        flood_probability=prob_score,
        alert=alert_val,
        recommendation=rec_val
    )
    return crud.create_prediction_result(db=db, prediction=prediction_in)

@app.get("/api/predictions", response_model=List[schemas.PredictionResultResponse])
def read_predictions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_prediction_results(db, skip=skip, limit=limit)

# --- STATS ENDPOINT ---
@app.get("/api/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_users = db.query(models.User).count()
    total_locations = db.query(models.Location).count()
    total_readings = db.query(models.SensorReading).count()
    
    preds = db.query(models.PredictionResult).all()
    total_preds = len(preds)
    
    low_risk = sum(1 for p in preds if p.risk_level == "Low")
    med_risk = sum(1 for p in preds if p.risk_level == "Medium")
    high_risk = sum(1 for p in preds if p.risk_level == "High")
    
    # Active alerts defined as high risk Predictions in the database
    active_alerts = high_risk
    
    readings = db.query(models.SensorReading).all()
    avg_water_level = (sum(r.water_level for r in readings) / len(readings)) if readings else 0.0
    max_rainfall = max((r.rainfall for r in readings), default=0.0)
    
    return {
        "total_users": total_users,
        "total_locations": total_locations,
        "total_readings": total_readings,
        "total_predictions": total_preds,
        "low_risk_count": low_risk,
        "medium_risk_count": med_risk,
        "high_risk_count": high_risk,
        "active_alerts": active_alerts,
        "average_water_level": round(avg_water_level, 2),
        "max_rainfall": round(max_rainfall, 2)
    }

# Serving Dashboard Frontend
@app.get("/")
def get_dashboard():
    paths = [
        os.path.join("app", "static", "index.html"),
        os.path.join("static", "index.html")
    ]
    for path in paths:
        if os.path.exists(path):
            return FileResponse(path)
    return {"message": "Welcome to Rising Waters API. Please create index.html in static/"}

# Mount Static Directory last (fallback for other files)
static_dir = "static"
if os.path.exists("app/static"):
    static_dir = "app/static"
else:
    os.makedirs("static", exist_ok=True)
    
app.mount("/", StaticFiles(directory=static_dir), name="static")
