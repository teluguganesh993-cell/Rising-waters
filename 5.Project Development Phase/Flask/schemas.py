from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --- USER ---
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- LOCATION ---
class LocationBase(BaseModel):
    location_name: str
    base_water_threshold: float
    latitude: float
    longitude: float

class LocationCreate(LocationBase):
    pass

class LocationResponse(LocationBase):
    location_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- SENSOR READING ---
class SensorReadingBase(BaseModel):
    location_id: int
    water_level: float
    rainfall: float
    temperature: float
    humidity: float
    river_flow: float
    wind_speed: float

class SensorReadingCreate(SensorReadingBase):
    pass

class SensorReadingResponse(SensorReadingBase):
    reading_id: int
    reading_time: datetime

    class Config:
        from_attributes = True

# --- MODEL ---
class ModelBase(BaseModel):
    model_name: str
    model_nm: Optional[str] = None
    algorithm: str
    training_accuracy: Optional[float] = None
    testing_accuracy: Optional[float] = None
    file_path: str

class ModelCreate(ModelBase):
    pass

class ModelResponse(ModelBase):
    model_id: int

    class Config:
        from_attributes = True

# --- PREDICTION RESULT ---
class PredictionResultBase(BaseModel):
    reading_id: int
    model_id: int
    risk_level: str
    flood_probability: float
    alert: str
    recommendation: str

class PredictionResultCreate(PredictionResultBase):
    pass

class PredictionResultResponse(PredictionResultBase):
    prediction_id: int
    prediction_time: datetime

    class Config:
        from_attributes = True

# --- RUN PREDICTION ---
class FloodPredictionRequest(BaseModel):
    reading_id: int
    model_id: int
