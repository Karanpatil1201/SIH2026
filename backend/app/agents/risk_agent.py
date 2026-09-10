from typing import Dict, Any
from app.ml.xgboost_risk import XGBoostRiskModel
from app.ml.shap_explainer import ShapExplainer

class RiskAgent:
    """
    Risk Agent calculating XGBoost Risk Score (0-100), mapping Risk Levels
    (LOW, MODERATE, HIGH, CRITICAL), and computing SHAP feature explanations.
    """
    def __init__(self):
        self.xgb_model = XGBoostRiskModel()
        self.shap_explainer = ShapExplainer(self.xgb_model)

    def process(self, fused_data: Dict[str, Any]) -> Dict[str, Any]:
        score, level = self.xgb_model.predict_risk(fused_data)
        pos_forces, neg_forces = self.shap_explainer.explain_prediction(fused_data)

        # Calculate confidence & uncertainty
        quality_score = fused_data.get("quality_report", {}).quality_score if isinstance(fused_data.get("quality_report"), object) and hasattr(fused_data.get("quality_report"), "quality_score") else 90.0
        confidence = round(min(0.96, (quality_score / 100.0) * 0.95), 2)

        uncertainty_level = "Low"
        if confidence < 0.7:
            uncertainty_level = "High"
        elif confidence < 0.85:
            uncertainty_level = "Moderate"

        return {
            "agent": "RiskAgent",
            "status": "COMPLETED",
            "findings": {
                "risk_score": score,
                "risk_level": level,
                "confidence": confidence,
                "uncertainty_level": uncertainty_level,
                "positive_forces": [f.model_dump() for f in pos_forces],
                "negative_forces": [f.model_dump() for f in neg_forces]
            }
        }
