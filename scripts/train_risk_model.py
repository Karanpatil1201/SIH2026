import os
import sys
import joblib
import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

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

def train_xgboost_risk():
    print("[Train Risk Model] Preparing dataset...")
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "processed", "marine_training_data.csv"))
    if not os.path.exists(data_path):
        df = generate_and_preprocess_dataset(n_samples=3000, save_path=data_path)
    else:
        df = pd.read_csv(data_path)

    X = df[FEATURE_NAMES]
    y = df["risk_target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print(f"[Train Risk Model] Training XGBoost Regressor on {len(X_train)} samples...")
    model = XGBRegressor(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.06,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = root_mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"[Train Risk Model] Evaluation: MAE={mae:.2f}, RMSE={rmse:.2f}, R²={r2:.4f}")

    model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "xgboost_risk.pkl")
    joblib.dump(model, model_path)
    print(f"[Train Risk Model] Saved model to {model_path}")

if __name__ == "__main__":
    train_xgboost_risk()
