import csv
import json
import math
import os
from functools import lru_cache
from typing import Any, Dict, Optional

import joblib
import pandas as pd


DATASET_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "external", "realistic_ocean_climate_dataset.csv")
)
MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "ecosystem_bleaching_model.pkl")
)
METADATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "ecosystem_bleaching_model_metadata.json")
)


@lru_cache(maxsize=1)
def _load_records() -> list[Dict[str, Any]]:
    if not os.path.exists(DATASET_PATH):
        return []

    records: list[Dict[str, Any]] = []
    with open(DATASET_PATH, "r", encoding="utf-8-sig", newline="") as dataset_file:
        for row in csv.DictReader(dataset_file):
            try:
                records.append(
                    {
                        "date": row.get("Date", ""),
                        "location": row.get("Location", "Unknown"),
                        "latitude": float(row["Latitude"]),
                        "longitude": float(row["Longitude"]),
                        "sst_c": float(row["SST (C)"] if "SST (C)" in row else row["SST (\u00b0C)"]),
                        "ph": float(row["pH Level"]),
                        "bleaching_severity": row.get("Bleaching Severity", "Unknown"),
                        "species_observed": int(float(row["Species Observed"])),
                        "marine_heatwave": row.get("Marine Heatwave", "False").strip().lower() == "true",
                    }
                )
            except (KeyError, TypeError, ValueError):
                continue
    return records


class EcosystemClimateDataset:
    """Nearest-neighbour lookup for the supplied historical ecosystem observations."""

    @classmethod
    def nearest_observation(cls, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        records = _load_records()
        if not records:
            return None

        return min(
            records,
            key=lambda record: (record["latitude"] - lat) ** 2 + (record["longitude"] - lon) ** 2,
        )

    @classmethod
    def summary(cls) -> Dict[str, Any]:
        records = _load_records()
        return {
            "dataset": "realistic_ocean_climate_dataset.csv",
            "records": len(records),
            "status": "AVAILABLE" if records else "UNAVAILABLE",
            "coverage": "Historical ecosystem observations (2015)",
        }

    @classmethod
    def model_status(cls) -> Dict[str, Any]:
        if not os.path.exists(METADATA_PATH):
            return {"status": "NOT_TRAINED", "model": "ecosystem_bleaching_model.pkl"}
        with open(METADATA_PATH, "r", encoding="utf-8") as metadata_file:
            return {"status": "TRAINED", **json.load(metadata_file)}

    @classmethod
    def predict_bleaching(cls, observation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not os.path.exists(MODEL_PATH):
            return None
        try:
            model = joblib.load(MODEL_PATH)
            features = {
                "sst_c": observation["sst_c"],
                "ph": observation["ph"],
                "species_observed": observation["species_observed"],
                "marine_heatwave": observation["marine_heatwave"],
                "latitude": observation["latitude"],
                "longitude": observation["longitude"],
                "location": observation["location"],
            }
            feature_frame = pd.DataFrame([features])
            prediction = str(model.predict(feature_frame)[0])
            probabilities = model.predict_proba(feature_frame)[0]
            confidence = float(max(probabilities))
            return {"predicted_bleaching_severity": prediction, "confidence": round(confidence, 3)}
        except Exception:
            return None
