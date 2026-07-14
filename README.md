# Rising Waters — Project Development Phase

## Project Overview
Rising Waters is an AI-powered river water monitoring and flood alert prediction system. The application analyzes telemetry inputs from IoT river sensors and local weather stations to predict flood risks in real-time, issuing warnings and evacuations recommendation protocols to protect lives and property.

The model uses:
- **Station Location** (Kurnool, Vijayawada, Guntur, Nellore, Tirupati)
- **Water Level** (meters)
- **Rainfall** (mm)
- **Temperature** (°C)
- **Humidity** (%)
- **River Flow Rate** (m³/s)
- **Wind Speed** (km/h)

to predict the flood risk probability and generate advisory classifications.

---

## Technologies Used
- Python 3.11
- Pandas
- NumPy
- Scikit-Learn
- XGBoost
- FastAPI / Uvicorn
- Flask
- SQLAlchemy
- Pydantic v2
- HTML5 / CSS3 (Glassmorphism)
- Vanilla JavaScript
- Chart.js

---

## Machine Learning Model
**Model Used:** XGBoost Classifier

**Preprocessing:**
- Categorical features (Location): `OneHotEncoder(drop='first')`
- Numerical features (Water Level, Rainfall, Temperature, Humidity, Flow Rate, Wind Speed): `StandardScaler()`

**Data:** Synthetically generated dataset of 1,200 telemetry logs mapped to historical flood probabilities and water level baselines.

---

## Project Structure
```
5.Project Development Phase/
├── Dataset/
│   └── flood_data.csv          # Synthetic telemetry data
├── Flask/
│   ├── static/
│   │   ├── index.html         # Interactive Glassmorphism Dashboard (SPA)
│   │   ├── styles.css         # Glassmorphism Design System Stylesheet
│   │   └── app.js             # SPA Controller & API Client
│   ├── templates/
│   │   ├── home.html          # Traditional landing page
│   │   ├── predict.html       # Traditional flood metrics form
│   │   └── submit.html        # Prediction result display page
│   ├── app.py                 # Standalone Flask server (Fallback Forms Interface)
│   ├── main.py                # FastAPI backend REST server (Serves Dashboard & API)
│   ├── models.py              # SQLAlchemy ORM models
│   ├── crud.py                # CRUD database helper functions
│   ├── database.py            # SQLite database connection setup
│   ├── schemas.py             # Pydantic validation schemas
│   ├── ml.py                  # ML model inference module
│   ├── init_db.py             # Database table creation and seeding script
│   ├── schema.sql             # Raw DDL SQL file
│   ├── flood_model.pkl        # Serialized trained XGBoost model
│   ├── flood_monitoring.db    # Seeded SQLite database
│   ├── Procfile               # Heroku/Render process file
│   ├── requirements.txt       # Python dependencies list
│   └── runtime.txt            # Python environment version
├── Training/
│   └── train_model.py         # Data generator and XGBoost model training script
├── README.md                  # This file
└── render.yaml                # Render.com deployment configuration
```

---

## Setup & Installation

### 1. Clone Repository
```bash
git clone <repository-url>
```

### 2. Navigate to Flask Folder
```bash
cd "5.Project Development Phase/Flask"
```

### 3. Install Dependencies
Ensure you are using the correct Python virtual environment and run:
```bash
pip install -r requirements.txt
```

### 4. Initialize Database
Initialize the database tables and seed baseline river station markers:
```bash
python init_db.py
```

### 5. Train & Serialize the ML Model
Generate the synthetic dataset and train the XGBoost classifier pipeline:
```bash
python ../Training/train_model.py
```

### 6. Run FastAPI Server (Dashboard & REST API)
```bash
uvicorn main:app --reload --port 8000
```
- Open Dashboard: `http://127.0.0.1:8000/`
- API Swagger Docs: `http://127.0.0.1:8000/docs`

### 7. Run Flask Server (Fallback Form Interface)
```bash
python app.py
```
- Open Forms View: `http://127.0.0.1:5000/`

---

## Key Features
- **XGBoost ML Classification:** Predicts flood risks dynamically based on water level thresholds and rain velocity.
- **Dynamic Advisories:** Maps prediction scores to Safe (Low), Watch (Medium), and Warning (High) risk alerts with recommendations.
- **Glassmorphism Dashboard:** Dark-mode dashboard displaying analytics charts, recent prediction lists, and form telemetry.
- **SQLite Database Integration:** Connects to locations, users, sensor readings, and prediction logs using SQLAlchemy ORM.
- **FastAPI Backend:** Lightweight RESTful API with auto-generated Swagger documentation.
- **Flask Fallback View:** Standard multi-page forms workflow for simple browsers.

---

## Developed By
- Telugu Ganesh
- Adimulapu Anil Kumar  
- Asia Kakravada  
- Akhil Kontham  
- P Vaahid
