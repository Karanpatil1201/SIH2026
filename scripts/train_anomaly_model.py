import os
import sys
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

# Add project root and backend directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_path = os.path.join(project_root, "backend")
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from scripts.preprocess import generate_and_preprocess_dataset

FEATURE_NAMES = [
    "sst", "wave_height", "wave_period", "swell_height",
    "current_velocity", "wind_speed", "pressure",
    "precipitation", "salinity", "chlorophyll", "sea_level"
]

def train_isolation_forest():
    print("[Train Anomaly Model] Preparing dataset...")
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "processed", "marine_training_data.csv"))
    if not os.path.exists(data_path):
        df = generate_and_preprocess_dataset(n_samples=3000, save_path=data_path)
    else:
        df = pd.read_csv(data_path)

    X = df[FEATURE_NAMES]

    print(f"[Train Anomaly Model] Training Isolation Forest on {len(X)} records...")
    model = IsolationForest(
        n_estimators=120,
        contamination=0.04,
        max_samples="auto",
        random_state=42
    )
    model.fit(X)

    model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "isolation_forest.pkl")
    joblib.dump(model, model_path)
    print(f"[Train Anomaly Model] Saved Isolation Forest model to {model_path}")

if __name__ == "__main__":
    train_isolation_forest()
