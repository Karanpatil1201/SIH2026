import json
import os

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "external", "realistic_ocean_climate_dataset.csv")
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "ecosystem_bleaching_model.pkl")
METADATA_PATH = os.path.join(MODEL_DIR, "ecosystem_bleaching_model_metadata.json")

FEATURE_COLUMNS = ["sst_c", "ph", "species_observed", "marine_heatwave", "latitude", "longitude", "location"]
NUMERIC_FEATURES = ["sst_c", "ph", "species_observed", "latitude", "longitude"]
CATEGORICAL_FEATURES = ["marine_heatwave", "location"]
TARGET_COLUMN = "bleaching_severity"


def load_dataset() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    df = df.rename(columns={"SST (°C)": "sst_c"})
    df["marine_heatwave"] = df["Marine Heatwave"].astype(str).str.lower().eq("true")
    df["species_observed"] = pd.to_numeric(df["Species Observed"], errors="coerce")
    df["sst_c"] = pd.to_numeric(df["sst_c"], errors="coerce")
    df["ph"] = pd.to_numeric(df["pH Level"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
    df["location"] = df["Location"].fillna("Unknown").astype(str)
    df[TARGET_COLUMN] = df["Bleaching Severity"].fillna("None").replace({"None": "None"})
    return df[FEATURE_COLUMNS + [TARGET_COLUMN]].dropna()


def train_ecosystem_model() -> dict:
    df = load_dataset()
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", "passthrough", NUMERIC_FEATURES),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(n_estimators=240, class_weight="balanced", random_state=42, n_jobs=4)),
        ]
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    metrics = {
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "macro_f1": round(float(f1_score(y_test, predictions, average="macro")), 4),
        "records": int(len(df)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "classes": sorted(y.unique().tolist()),
    }

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    with open(METADATA_PATH, "w", encoding="utf-8") as metadata_file:
        json.dump(
            {
                "model": "RandomForest ecosystem bleaching severity classifier",
                "features": FEATURE_COLUMNS,
                "target": TARGET_COLUMN,
                "metrics": metrics,
            },
            metadata_file,
            indent=2,
        )

    print(f"[Train Ecosystem Model] Saved model to {MODEL_PATH}")
    print(f"[Train Ecosystem Model] Metrics: {metrics}")
    return metrics


if __name__ == "__main__":
    train_ecosystem_model()
