import json
import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "external", "fisheries", "capture_quantity_joined.csv")
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "fisheries_catch_model.pkl")
METADATA_PATH = os.path.join(MODEL_DIR, "fisheries_catch_model_metadata.json")

CATEGORICAL_COLUMNS = ["ISO3_Code", "Common name", "Scientific_Name", "Area", "MEASURE", "STATUS"]
NUMERIC_COLUMNS = ["PERIOD"]
FEATURE_COLUMNS = NUMERIC_COLUMNS + [f"{column}_code" for column in CATEGORICAL_COLUMNS]


def load_training_data() -> pd.DataFrame:
    columns = ["MEASURE", "PERIOD", "VALUE", "STATUS", "ISO3_Code", "Country", "Common name", "Scientific_Name", "Area"]
    df = pd.read_csv(DATA_PATH, usecols=columns)
    df["VALUE"] = pd.to_numeric(df["VALUE"], errors="coerce").fillna(0).clip(lower=0)
    df["PERIOD"] = pd.to_numeric(df["PERIOD"], errors="coerce").fillna(0).astype(int)
    for column in CATEGORICAL_COLUMNS:
        df[column] = df[column].fillna("UNKNOWN").astype(str)
        df[f"{column}_code"] = pd.factorize(df[column], sort=True)[0]
    return df


def train_fisheries_model() -> dict:
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Fisheries dataset not found: {DATA_PATH}")

    df = load_training_data()
    # A deterministic sample keeps local retraining practical while retaining broad coverage.
    if len(df) > 300_000:
        df = df.sample(n=300_000, random_state=42)

    X = df[FEATURE_COLUMNS]
    y = np.log1p(df["VALUE"])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = XGBRegressor(
        n_estimators=180,
        max_depth=8,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=4,
    )
    model.fit(X_train, y_train)
    predicted_log = model.predict(X_test)
    actual = np.expm1(y_test)
    predicted = np.maximum(0, np.expm1(predicted_log))
    metrics = {
        "mae_quantity": round(float(mean_absolute_error(actual, predicted)), 3),
        "rmse_quantity": round(float(np.sqrt(mean_squared_error(actual, predicted))), 3),
        "r2_log_quantity": round(float(r2_score(y_test, predicted_log)), 4),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
    }

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    with open(METADATA_PATH, "w", encoding="utf-8") as metadata_file:
        json.dump({"model": "XGBoost fisheries catch quantity regressor", "features": FEATURE_COLUMNS, "target": "log1p(VALUE)", "metrics": metrics}, metadata_file, indent=2)

    print(f"[Train Fisheries Model] Saved model to {MODEL_PATH}")
    print(f"[Train Fisheries Model] Metrics: {metrics}")
    return metrics


if __name__ == "__main__":
    train_fisheries_model()
