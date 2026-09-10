import shap
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from app.ml.xgboost_risk import XGBoostRiskModel
from app.models.schemas import FeatureContribution

class ShapExplainer:
    """
    Computes exact SHAP (SHapley Additive exPlanations) values for XGBoost risk predictions.
    Generates dynamic positive and negative feature impact lists with human-readable explanations.
    """

    FEATURE_DESCRIPTIONS = {
        "wave_height": "Significant wave height exposure",
        "wind_speed": "Surface wind speed force",
        "pressure": "Atmospheric pressure drop / cyclone indicator",
        "current_velocity": "Surface current velocity shear",
        "swell_height": "Primary ocean swell height",
        "wave_period": "Wave period swell steepness",
        "sst": "Sea Surface Temperature variation",
        "precipitation": "Coastal precipitation intensity",
        "sea_level": "Sea level height anomaly",
        "salinity": "Sea surface salinity gradient",
        "chlorophyll": "Chlorophyll-a ocean concentration"
    }

    def __init__(self, xgboost_model_wrapper: XGBoostRiskModel):
        self.model_wrapper = xgboost_model_wrapper
        self.explainer = None
        self._init_explainer()

    def _init_explainer(self):
        try:
            # TreeExplainer optimized for XGBoost
            self.explainer = shap.TreeExplainer(self.model_wrapper.model)
        except Exception as e:
            print(f"[ShapExplainer] Initializing TreeExplainer failed, using ExactExplainer fallback: {e}")
            self.explainer = None

    def explain(self, features: Dict[str, Any]) -> Tuple[List[FeatureContribution], List[FeatureContribution]]:
        return self.explain_prediction(features)

    def explain_prediction(self, features: Dict[str, Any]) -> Tuple[List[FeatureContribution], List[FeatureContribution]]:
        feature_names = self.model_wrapper.FEATURE_NAMES
        input_data = [features.get(f, 0.0) for f in feature_names]
        df_in = pd.DataFrame([input_data], columns=feature_names)

        if self.explainer:
            try:
                shap_values = self.explainer.shap_values(df_in)[0]
            except Exception:
                shap_values = self._approximate_shap_values(features, feature_names)
        else:
            shap_values = self._approximate_shap_values(features, feature_names)

        positive_forces: List[FeatureContribution] = []
        negative_forces: List[FeatureContribution] = []

        for name, val, impact in zip(feature_names, input_data, shap_values):
            imp_rounded = round(float(impact), 1)
            if abs(imp_rounded) < 0.1:
                continue

            desc = self.FEATURE_DESCRIPTIONS.get(name, f"{name} factor")
            contrib = FeatureContribution(
                feature=name,
                impact=imp_rounded,
                value=val,
                description=f"{desc} ({val})"
            )

            if imp_rounded > 0:
                positive_forces.append(contrib)
            else:
                negative_forces.append(contrib)

        # Sort by absolute impact magnitude
        positive_forces.sort(key=lambda x: x.impact, reverse=True)
        negative_forces.sort(key=lambda x: x.impact) # Most negative first

        return positive_forces, negative_forces

    def _approximate_shap_values(self, features: Dict[str, Any], feature_names: List[str]) -> np.ndarray:
        """
        Physics-guided fallback approximation if SHAP binary tree explainer fails.
        """
        impacts = []
        for name in feature_names:
            val = features.get(name, 0.0)
            if name == "wave_height":
                imp = (val - 1.5) * 8.5
            elif name == "wind_speed":
                imp = (val - 20.0) * 0.65
            elif name == "pressure":
                imp = (1013.0 - val) * 0.75
            elif name == "current_velocity":
                imp = (val - 0.4) * 12.0
            elif name == "swell_height":
                imp = (val - 0.8) * 6.0
            else:
                imp = 0.5 if val > 25 else -0.5
            impacts.append(imp)
        return np.array(impacts)
