from sqlalchemy.orm import Session

try:
    from app import models, schemas
except ImportError:
    import models, schemas

# --- USER CRUD ---
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, email=user.email, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- LOCATION CRUD ---
def get_location(db: Session, location_id: int):
    return db.query(models.Location).filter(models.Location.location_id == location_id).first()

def get_location_by_name(db: Session, name: str):
    return db.query(models.Location).filter(models.Location.location_name == name).first()

def get_locations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Location).offset(skip).limit(limit).all()

def create_location(db: Session, location: schemas.LocationCreate):
    db_location = models.Location(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

# --- SENSOR READING CRUD ---
def get_sensor_reading(db: Session, reading_id: int):
    return db.query(models.SensorReading).filter(models.SensorReading.reading_id == reading_id).first()

def get_sensor_readings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.SensorReading).offset(skip).limit(limit).all()

def create_sensor_reading(db: Session, reading: schemas.SensorReadingCreate):
    db_reading = models.SensorReading(**reading.dict())
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading

# --- MODEL CRUD ---
def get_model(db: Session, model_id: int):
    return db.query(models.Model).filter(models.Model.model_id == model_id).first()

def get_models(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Model).offset(skip).limit(limit).all()

def create_model(db: Session, model: schemas.ModelCreate):
    db_model = models.Model(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

# --- PREDICTION RESULT CRUD ---
def get_prediction_result(db: Session, prediction_id: int):
    return db.query(models.PredictionResult).filter(models.PredictionResult.prediction_id == prediction_id).first()

def get_prediction_results(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.PredictionResult).offset(skip).limit(limit).all()

def create_prediction_result(db: Session, prediction: schemas.PredictionResultCreate):
    db_pred = models.PredictionResult(**prediction.dict())
    db.add(db_pred)
    db.commit()
    db.refresh(db_pred)
    return db_pred
