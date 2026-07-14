import os
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
import xgboost as xgb
import sqlite3

def generate_synthetic_data(num_samples=1200, random_state=42):
    np.random.seed(random_state)
    
    locations = ["Kurnool", "Vijayawada", "Guntur", "Nellore", "Tirupati"]
    thresholds = {
        "Kurnool": 8.0,
        "Vijayawada": 6.5,
        "Guntur": 5.0,
        "Nellore": 7.0,
        "Tirupati": 5.5
    }
    
    # Generate features
    location = np.random.choice(locations, size=num_samples)
    
    water_level = []
    rainfall = []
    temperature = []
    humidity = []
    river_flow = []
    wind_speed = []
    flood_probability = []
    flood_predicted = []
    
    for loc in location:
        thresh = thresholds[loc]
        # Water level fluctuates around threshold - 1.5m
        w_level = np.random.normal(thresh - 1.5, 2.2)
        w_level = max(0.5, round(w_level, 2))
        water_level.append(w_level)
        
        # Rainfall lognormal
        rain = np.random.lognormal(mean=3.2, sigma=0.9)
        rain = min(250.0, max(0.0, round(rain, 1)))
        rainfall.append(rain)
        
        # Temperature
        temp = np.random.normal(30.0, 5.0)
        temp = min(48.0, max(12.0, round(temp, 1)))
        temperature.append(temp)
        
        # Humidity
        hum = np.random.normal(70.0, 15.0)
        hum = min(100.0, max(20.0, round(hum, 0)))
        humidity.append(hum)
        
        # River flow is correlated with water level
        flow = w_level * 22.0 + np.random.normal(0.0, 20.0)
        flow = min(1200.0, max(10.0, round(flow, 1)))
        river_flow.append(flow)
        
        # Wind speed
        wind = np.random.lognormal(mean=2.6, sigma=0.6)
        wind = min(90.0, max(0.0, round(wind, 1)))
        wind_speed.append(wind)
        
        # Calculate probability logic
        p = 0.05 # base
        
        # Water level impact
        if w_level > thresh:
            p += 0.40 * (w_level - thresh)
        else:
            p += 0.02 * (w_level - thresh) # minor penalty/bonus
            
        # Rainfall impact
        if rain > 60.0:
            p += 0.25
        elif rain > 30.0:
            p += 0.10
            
        # River flow impact
        if flow > 200.0:
            p += 0.15
            
        # Humidity and wind speed (storm conditions)
        if hum > 85.0:
            p += 0.05
        if wind > 40.0:
            p += 0.05
            
        p = np.clip(p, 0.01, 0.99)
        flood_probability.append(p)
        
        # Sample prediction
        predicted = np.random.binomial(1, p)
        flood_predicted.append(predicted)
        
    df = pd.DataFrame({
        "location": location,
        "water_level": water_level,
        "rainfall": rainfall,
        "temperature": temperature,
        "humidity": humidity,
        "river_flow": river_flow,
        "wind_speed": wind_speed,
        "flood_predicted": flood_predicted
    })
    
    return df

def train_and_save_model():
    print("Generating synthetic flood dataset...")
    os.makedirs("5.Project Development Phase/Dataset", exist_ok=True)
    df = generate_synthetic_data(1200)
    df.to_csv("5.Project Development Phase/Dataset/flood_data.csv", index=False)
    print("Dataset saved to 5.Project Development Phase/Dataset/flood_data.csv")
    
    X = df.drop(columns=["flood_predicted"])
    y = df["flood_predicted"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    categorical_features = ["location"]
    numerical_features = ["water_level", "rainfall", "temperature", "humidity", "river_flow", "wind_speed"]
    
    categorical_transformer = OneHotEncoder(drop="first", handle_unknown="ignore")
    numerical_transformer = StandardScaler()
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numerical_transformer, numerical_features),
            ("cat", categorical_transformer, categorical_features)
        ]
    )
    
    print("Training XGBoost Classifier...")
    model_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", xgb.XGBClassifier(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.1,
                random_state=42,
                use_label_encoder=False,
                eval_metric="logloss"
            ))
        ]
    )
    
    model_pipeline.fit(X_train, y_train)
    
    train_preds = model_pipeline.predict(X_train)
    test_preds = model_pipeline.predict(X_test)
    
    train_acc = float(accuracy_score(y_train, train_preds))
    test_acc = float(accuracy_score(y_test, test_preds))
    
    print(f"Training Accuracy: {train_acc * 100:.2f}%")
    print(f"Testing Accuracy: {test_acc * 100:.2f}%")
    
    os.makedirs("5.Project Development Phase/Flask/app/models", exist_ok=True) # supports both local run modes
    os.makedirs("5.Project Development Phase/Flask", exist_ok=True)
    
    model_path = "5.Project Development Phase/Flask/flood_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model_pipeline, f)
        
    # Also save a copy inside app/models for relative import support in subfolder imports
    fallback_model_path = "5.Project Development Phase/Flask/app/models/xgboost_flood_model.pkl"
    with open(fallback_model_path, "wb") as f:
        pickle.dump(model_pipeline, f)
        
    print(f"Model saved successfully to {model_path} and {fallback_model_path}")
    
    # Seed details in SQLite database
    db_path = "5.Project Development Phase/Flask/flood_monitoring.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS models (
            model_id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            model_nm TEXT,
            algorithm TEXT NOT NULL,
            training_accuracy REAL,
            testing_accuracy REAL,
            file_path TEXT NOT NULL
        )
    """)
    
    cursor.execute("SELECT model_id FROM models WHERE model_nm = 'xgboost_v1'")
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute("""
            UPDATE models 
            SET training_accuracy = ?, testing_accuracy = ?, file_path = ?
            WHERE model_id = ?
        """, (train_acc, test_acc, fallback_model_path, existing[0]))
    else:
        cursor.execute("""
            INSERT INTO models (model_name, model_nm, algorithm, training_accuracy, testing_accuracy, file_path)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("XGBoost Flood Predictor v1", "xgboost_v1", "XGBoost Classifier", train_acc, test_acc, fallback_model_path))
        
    conn.commit()
    conn.close()
    print("Model database entry updated/created.")

if __name__ == "__main__":
    train_and_save_model()
