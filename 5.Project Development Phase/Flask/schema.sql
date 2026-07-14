-- DDL Schema Dump for Rising Waters Monitoring & Flood Alert System

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS locations (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_name TEXT NOT NULL UNIQUE,
    base_water_threshold REAL NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sensor_readings (
    reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER NOT NULL,
    water_level REAL NOT NULL,
    rainfall REAL NOT NULL,
    temperature REAL NOT NULL,
    humidity REAL NOT NULL,
    river_flow REAL NOT NULL,
    wind_speed REAL NOT NULL,
    reading_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations (location_id)
);

CREATE TABLE IF NOT EXISTS models (
    model_id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    model_nm TEXT,
    algorithm TEXT NOT NULL,
    training_accuracy REAL,
    testing_accuracy REAL,
    file_path TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prediction_results (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    reading_id INTEGER NOT NULL,
    model_id INTEGER NOT NULL,
    risk_level TEXT NOT NULL,
    flood_probability REAL NOT NULL,
    alert TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reading_id) REFERENCES sensor_readings (reading_id),
    FOREIGN KEY (model_id) REFERENCES models (model_id)
);
