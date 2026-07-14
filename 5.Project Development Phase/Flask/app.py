import os
import pickle
import pandas as pd
import numpy as np
from flask import Flask, request, render_template

app = Flask(__name__)
app.secret_key = "rising_waters_secret_key_12345"

# Load the saved model file
MODEL_PATHS = ['flood_model.pkl', 'app/models/xgboost_flood_model.pkl']
model = None

for path in MODEL_PATHS:
    if os.path.exists(path):
        try:
            with open(path, 'rb') as f:
                model = pickle.load(f)
            print(f"Loaded model from '{path}' successfully.")
            break
        except Exception as e:
            print(f"Error loading model from {path}: {e}")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/predict', methods=["POST", "GET"])
def predict():
    return render_template("predict.html")

@app.route('/predict/submit', methods=["POST"])
@app.route('/submit', methods=["POST"])
def submit():
    if request.method == "POST":
        try:
            # Retrieve values from form
            location = request.form.get('location', 'Kurnool')
            water_level = float(request.form.get('water_level', 0.0))
            rainfall = float(request.form.get('rainfall', 0.0))
            temperature = float(request.form.get('temperature', 0.0))
            humidity = float(request.form.get('humidity', 0.0))
            river_flow = float(request.form.get('river_flow', 0.0))
            wind_speed = float(request.form.get('wind_speed', 0.0))
            
            # Construct DataFrame matching model features exactly
            data = pd.DataFrame([{
                "location": location,
                "water_level": water_level,
                "rainfall": rainfall,
                "temperature": temperature,
                "humidity": humidity,
                "river_flow": river_flow,
                "wind_speed": wind_speed
            }])
            
            print(f"Evaluating form inputs:\n{data}")
            
            # Predict
            if model is not None:
                prob = float(model.predict_proba(data)[0][1])
            else:
                # Heuristic fallback if model is not trained yet
                thresholds = {
                    "Kurnool": 8.0,
                    "Vijayawada": 6.5,
                    "Guntur": 5.0,
                    "Nellore": 7.0,
                    "Tirupati": 5.5
                }
                thresh = thresholds.get(location, 6.0)
                val = 0.05
                if water_level > thresh:
                    val += 0.40 * (water_level - thresh)
                if rainfall > 60:
                    val += 0.25
                prob = min(0.99, max(0.01, val))
                
            prob_percent = round(prob * 100, 2)
            
            if prob < 0.30:
                risk_level = "Low"
            elif prob < 0.70:
                risk_level = "Medium"
            else:
                risk_level = "High"
                
            return render_template("submit.html", prediction=risk_level, probability=prob_percent, location=location)
            
        except Exception as e:
            print(f"Error during prediction: {e}")
            return render_template("submit.html", prediction="Error", probability=0.0, location="Unknown")
            
    return render_template("predict.html")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)
