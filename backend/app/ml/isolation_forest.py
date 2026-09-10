import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    """
    Isolation Forest for detecting multivariate ocean & weather anomalies.
    Outputs: is_anomaly (bool) and anomaly_score (0.0 to 1.0).
    """
    FEATURE_NAMES = [
        "sst", "wave_height", "wave_period", "swell_height",
        "current_velocity", "wind_speed", "pressure",
        "precipitation", "salinity", "chlorophyll", "sea_level"
    ]

    MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "isolation_forest.pkl")

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
                print(f"[AnomalyDetector] Could not load saved model: {e}")
        
        self._train_default_model()

    def _train_default_model(self):
        np.random.seed(42)
        n_samples = 800
        
        # Normal marine observations distribution
        data = np.column_stack([
            np.random.normal(28.0, 1.5, n_samples),   # sst
            np.random.normal(1.5, 0.5, n_samples),    # wave_height
            np.random.normal(7.0, 1.2, n_samples),    # wave_period
            np.random.normal(0.8, 0.3, n_samples),    # swell
            np.random.normal(0.4, 0.2, n_samples),    # current
            np.random.normal(20.0, 6.0, n_samples),   # wind
            np.random.normal(1012.0, 3.0, n_samples), # pressure
            np.random.exponential(1.0, n_samples),    # precipitation
            np.random.normal(35.5, 0.4, n_samples),   # salinity
            np.random.normal(0.5, 0.2, n_samples),    # chlorophyll
            np.random.normal(0.1, 0.1, n_samples),    # sea_level
        ])

        df = pd.DataFrame(data, columns=self.FEATURE_NAMES)
        self.model = IsolationForest(n_estimators=100, contamination=0.08, random_state=42)
        self.model.fit(df)

        os.makedirs(os.path.dirname(self.MODEL_PATH), exist_ok=True)
        joblib.dump(self.model, self.MODEL_PATH)

    def detect_anomaly(self, features: Dict[str, Any]) -> Tuple[bool, float, str]:
        """
        Detects if features constitute an anomaly.
        Returns: (is_anomaly, anomaly_score, anomaly_type)
        """
        input_data = [features.get(f, 0.0) for f in self.FEATURE_NAMES]
        df_in = pd.DataFrame([input_data], columns=self.FEATURE_NAMES)

        pred = self.model.predict(df_in)[0] # 1 for inlier, -1 for outlier
        decision_score = float(self.model.decision_function(df_in)[0])

        is_anomaly = bool(pred == -1)
        # Convert decision function to 0-1 scale score where 1 = extreme anomaly
        anomaly_score = round(float(np.clip(0.5 - decision_score, 0.0, 1.0)), 2)

        # Categorize anomaly type
        anomaly_type = "Normal Baseline"
        if is_anomaly:
            if features.get("wave_height", 0) > 3.0:
                anomaly_type = "Extreme Wave Anomaly"
            elif features.get("wind_speed", 0) > 45.0:
                anomaly_type = "Severe Wind Spike"
            elif features.get("pressure", 1013) < 995.0:
                anomaly_type = "Atmospheric Pressure Drop Anomaly"
            elif features.get("sst", 28) > 31.0:
                anomaly_type = "Sea Surface Temperature Spike"
            else:
                anomaly_type = "Multivariate Environmental Anomaly"

        return is_anomaly, anomaly_score, anomaly_type
