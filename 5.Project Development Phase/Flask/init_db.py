import sys
import os

# Ensure import paths resolve correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from app.database import engine, SessionLocal
    from app import models
except ImportError:
    from database import engine, SessionLocal
    import models

def create_tables():
    """Create all database tables defined in models.py."""
    models.Base.metadata.create_all(bind=engine)
    print("[OK] All tables created (or already exist).")

def seed_database():
    """Seed initial locations and default ML model details."""
    db = SessionLocal()
    try:
        # Seed locations
        locations_to_seed = [
            {"name": "Kurnool", "thresh": 8.0, "lat": 15.8281, "lon": 78.0373},
            {"name": "Vijayawada", "thresh": 6.5, "lat": 16.5062, "lon": 80.6480},
            {"name": "Guntur", "thresh": 5.0, "lat": 16.3067, "lon": 80.4365},
            {"name": "Nellore", "thresh": 7.0, "lat": 14.4426, "lon": 79.9865},
            {"name": "Tirupati", "thresh": 5.5, "lat": 13.6288, "lon": 79.4192}
        ]
        
        for loc in locations_to_seed:
            existing = db.query(models.Location).filter(models.Location.location_name == loc["name"]).first()
            if not existing:
                db_loc = models.Location(
                    location_name=loc["name"],
                    base_water_threshold=loc["thresh"],
                    latitude=loc["lat"],
                    longitude=loc["lon"]
                )
                db.add(db_loc)
                print(f"[OK] Seeded location: {loc['name']}")
                
        # Seed default model metadata record
        existing_model = db.query(models.Model).filter(models.Model.model_nm == "xgboost_v1").first()
        if not existing_model:
            db_model = models.Model(
                model_name="XGBoost Flood Predictor v1",
                model_nm="xgboost_v1",
                algorithm="XGBoost Classifier",
                training_accuracy=None,
                testing_accuracy=None,
                file_path="app/models/xgboost_flood_model.pkl"
            )
            db.add(db_model)
            print("[OK] Seeded default model metadata record (model_nm='xgboost_v1')")
            
        db.commit()
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing Raising Waters database...")
    create_tables()
    seed_database()
    print("Database initialization complete.")
