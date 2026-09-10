import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from xgboost import XGBRegressor

class XGBoostRiskModel:
    """
    Primary Machine Learning Model (XGBoost Regressor) for Marine Risk Scoring.
    Outputs continuous Risk Score (0-100) and categorizes into LOW, MODERATE, HIGH, CRITICAL.
    """
    FEATURE_NAMES = [
        "sst", "wave_height", "wave_period", "swell_height",
        "current_velocity", "wind_speed", "pressure",
        "precipitation", "salinity", "chlorophyll", "sea_level"
    ]

    MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "xgboost_risk.pkl")

    def __init__(self):
        self.model = None
        self._load_or_train_model()

    def _load_or_train_model(self):
        norm_path = os.path.abspath(self.MODEL_PATH)
        if os.path.exists(norm_path):
            try:
                self.model = joblib.load(norm_path)
                return
            except Exception as e:
                print(f"[XGBoostRiskModel] Could not load saved model: {e}")
        
        # Fallback inline training if model file does not exist yet
        self._train_default_model()

    def _train_default_model(self):
        np.random.seed(42)
        n_samples = 1000
        
        # Generate synthetic realistic training set for physics-consistent marine risk
        sst = np.random.uniform(20.0, 32.0, n_samples)
        wave_h = np.random.uniform(0.5, 6.0, n_samples)
        wave_p = np.random.uniform(4.0, 14.0, n_samples)
        swell = wave_h * np.random.uniform(0.4, 0.8, n_samples)
        current_v = np.random.uniform(0.1, 2.5, n_samples)
        wind_s = np.random.uniform(5.0, 80.0, n_samples)
        pressure = np.random.uniform(970.0, 1025.0, n_samples)
        precip = np.random.uniform(0.0, 50.0, n_samples)
        salinity = np.random.uniform(32.0, 37.0, n_samples)
        chloro = np.random.uniform(0.1, 5.0, n_samples)
        sea_level = np.random.uniform(-0.5, 1.5, n_samples)

        # Physics-based risk calculation target
        # Risk scales heavily with high wave height, high wind, low pressure (cyclone), high current
        risk_target = (
            (wave_h / 6.0) * 35.0 +
            (wind_s / 80.0) * 35.0 +
            (np.maximum(0, 1013.0 - pressure) / 40.0) * 20.0 +
            (current_v / 2.5) * 10.0
        ) + np.random.normal(0, 2.0, n_samples)

        risk_target = np.clip(risk_target, 0.0, 100.0)

        df_X = pd.DataFrame({
            "sst": sst, "wave_height": wave_h, "wave_period": wave_p, "swell_height": swell,
            "current_velocity": current_v, "wind_speed": wind_s, "pressure": pressure,
            "precipitation": precip, "salinity": salinity, "chlorophyll": chloro, "sea_level": sea_level
        })

        self.model = XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.08, random_state=42)
        self.model.fit(df_X, risk_target)
        
        # Save model
        os.makedirs(os.path.dirname(self.MODEL_PATH), exist_ok=True)
        joblib.dump(self.model, self.MODEL_PATH)

    def predict_risk(self, features: Dict[str, Any]) -> Tuple[float, str]:
        """
        Predicts Risk Score (0-100) and returns (score, level).
        """
        input_data = [features.get(f, 0.0) for f in self.FEATURE_NAMES]
        df_in = pd.DataFrame([input_data], columns=self.FEATURE_NAMES)
        
        raw_pred = float(self.model.predict(df_in)[0])
        score = round(float(np.clip(raw_pred, 0.0, 100.0)), 1)

        if score <= 30.0:
            level = "LOW"
        elif score <= 60.0:
            level = "MODERATE"
        elif score <= 80.0:
            level = "HIGH"
        else:
            level = "CRITICAL"

        return score, level
