from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime

try:
    from app.database import Base
except ImportError:
    from database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)  # "Operator" or "Public Observer"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Location(Base):
    __tablename__ = "locations"

    location_id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String, unique=True, index=True, nullable=False)  # Kurnool, Vijayawada, etc.
    base_water_threshold = Column(Float, nullable=False)  # Danger water level (meters)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    readings = relationship("SensorReading", back_populates="location")

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    reading_id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.location_id"), nullable=False)
    water_level = Column(Float, nullable=False)
    rainfall = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    river_flow = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    reading_time = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    location = relationship("Location", back_populates="readings")
    predictions = relationship("PredictionResult", back_populates="reading")

class Model(Base):
    __tablename__ = "models"

    model_id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, nullable=False)
    model_nm = Column(String, nullable=True)  # xgboost_v1
    algorithm = Column(String, nullable=False)  # XGBoost Classifier
    training_accuracy = Column(Float, nullable=True)
    testing_accuracy = Column(Float, nullable=True)
    file_path = Column(String, nullable=False)

    # Relationships
    predictions = relationship("PredictionResult", back_populates="model")

class PredictionResult(Base):
    __tablename__ = "prediction_results"

    prediction_id = Column(Integer, primary_key=True, index=True)
    reading_id = Column(Integer, ForeignKey("sensor_readings.reading_id"), nullable=False)
    model_id = Column(Integer, ForeignKey("models.model_id"), nullable=False)
    risk_level = Column(String, nullable=False)  # Low, Medium, High
    flood_probability = Column(Float, nullable=False)  # Percentage score
    alert = Column(String, nullable=False)  # Safe, Watch, Warning
    recommendation = Column(String, nullable=False)  # Evacuate..., Safe...
    prediction_time = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    reading = relationship("SensorReading", back_populates="predictions")
    model = relationship("Model", back_populates="predictions")
