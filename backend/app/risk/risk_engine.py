from typing import Dict, Any, List, Tuple
from app.ml.xgboost_risk import XGBoostRiskModel
from app.ml.isolation_forest import AnomalyDetector
from app.ml.shap_explainer import ShapExplainer

class RiskEngine:
    """
    Central Risk Engine for VARUNA Marine Ecosystem Intelligence.
    Calculates unified, transparent, and explainable marine risk scores (0-100):
      0  - 30  : SAFE
      31 - 60  : CAUTION
      61 - 100 : DANGER

    Combines:
      1. Physical Ocean Risk (waves, currents, swell)
      2. Meteorological Weather Risk (wind gusts, barometric pressure deficit, precipitation)
      3. Anomaly Risk (Isolation Forest + Satellite anomaly flags)
      4. Machine Learning Risk (XGBoost model trained on marine physics)
      5. Agentic Consensus & Confidence weighting
    """

    def __init__(self, xgb_model: XGBoostRiskModel = None, anomaly_model: AnomalyDetector = None):
        self.xgb_model = xgb_model or XGBoostRiskModel()
        self.anomaly_model = anomaly_model or AnomalyDetector()
        self.shap_explainer = ShapExplainer(self.xgb_model)

    def calculate_risk(
        self,
        fused_data: Dict[str, Any],
        agent_findings: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Computes composite explainable marine risk score and breakdown.
        """
        # 1. Physical Ocean Risk Component (0 - 100)
        wave_h = float(fused_data.get("wave_height", 1.2) or 1.2)
        current_v = float(fused_data.get("current_velocity", 0.4) or 0.4)
        swell_h = float(fused_data.get("swell_height", 0.8) or 0.8)
        
        # Wave scale: 0-1m (low), 1-2m (moderate), 2-3m (high), >3m (critical)
        wave_risk = min(100.0, (wave_h / 4.5) * 80.0 + (swell_h / 3.0) * 20.0)
        current_risk = min(100.0, (current_v / 2.0) * 100.0)
        ocean_risk_component = round(0.75 * wave_risk + 0.25 * current_risk, 1)

        # 2. Meteorological Weather Risk Component (0 - 100)
        wind_s = float(fused_data.get("wind_speed", 15.0) or 15.0)
        pressure = float(fused_data.get("pressure", 1012.0) or 1012.0)
        precip = float(fused_data.get("precipitation", 0.0) or 0.0)

        # Pressure deficit below 1013 hPa
        pressure_deficit = max(0.0, 1013.0 - pressure)
        wind_risk = min(100.0, (wind_s / 65.0) * 100.0)
        cyclonic_pressure_risk = min(100.0, (pressure_deficit / 30.0) * 100.0)
        weather_risk_component = round(0.60 * wind_risk + 0.35 * cyclonic_pressure_risk + 0.05 * min(100.0, precip * 3.0), 1)

        # 3. Anomaly Risk Component (0 - 100)
        is_anom, anom_score, anom_type = self.anomaly_model.detect_anomaly(fused_data)
        # anom_score is negative for anomalies; convert to 0-100
        normalized_anom_risk = min(100.0, max(0.0, (0.25 - anom_score) * 120.0)) if is_anom else max(5.0, (0.1 - anom_score) * 40.0)
        anomaly_risk_component = round(min(100.0, normalized_anom_risk), 1)

        # 4. Machine Learning Model Risk Prediction (0 - 100)
        ml_score, _ = self.xgb_model.predict_risk(fused_data)
        ml_risk_component = round(ml_score, 1)

        # 5. Agent Agreement / Consensus Risk Modifier
        agent_penalty = 0.0
        agent_count = 0
        agent_confidences = []
        if agent_findings:
            for af in agent_findings:
                status = af.get("status", "SAFE")
                conf = float(af.get("confidence", 0.85))
                agent_confidences.append(conf)
                agent_count += 1
                if status == "DANGER":
                    agent_penalty += 12.0 * conf
                elif status == "CAUTION":
                    agent_penalty += 5.0 * conf
        
        avg_confidence = round(sum(agent_confidences) / max(1, len(agent_confidences)), 2) if agent_confidences else 0.90

        # Weighted Fusion: ML Model (35%), Ocean Physics (30%), Weather (25%), Anomaly (10%)
        base_fused_risk = (
            0.35 * ml_risk_component +
            0.30 * ocean_risk_component +
            0.25 * weather_risk_component +
            0.10 * anomaly_risk_component
        )
        
        # Apply slight consensus adjustment (capped)
        consensus_adj = min(15.0, agent_penalty / max(1, agent_count)) if agent_count > 0 else 0.0
        final_risk_score = round(max(0.0, min(100.0, base_fused_risk * 0.88 + consensus_adj * 0.12 + (agent_penalty * 0.2))), 1)

        # Categorize into strict SAFE / CAUTION / DANGER standards
        if final_risk_score <= 30.0:
            risk_level = "SAFE"
        elif final_risk_score <= 60.0:
            risk_level = "CAUTION"
        else:
            risk_level = "DANGER"

        # Uncertainty Level
        uncertainty = "Low" if avg_confidence >= 0.88 else ("Moderate" if avg_confidence >= 0.75 else "High")

        # Compute SHAP explainability
        positive_forces, negative_forces = self.shap_explainer.explain(fused_data)

        # Extract Key Risks
        key_risks = []
        if wave_h >= 2.5:
            key_risks.append(f"High wave elevation ({wave_h}m) above safety threshold")
        elif wave_h >= 1.8:
            key_risks.append(f"Moderate wave swell ({wave_h}m)")
            
        if wind_s >= 25.0:
            key_risks.append(f"Strong wind velocity ({wind_s} km/h)")
            
        if pressure <= 1005.0:
            key_risks.append(f"Atmospheric low pressure ({pressure} hPa) indicating cyclonic tendency")
            
        if current_v >= 1.2:
            key_risks.append(f"High ocean current velocity ({current_v} m/s)")
            
        if is_anom:
            key_risks.append("Environmental parameter anomaly detected via Isolation Forest")
            
        if not key_risks:
            key_risks.append("All baseline marine and atmospheric variables within nominal safety ranges")

        # Actionable Recommendations
        recommendations = []
        if risk_level == "DANGER":
            recommendations.append("High risk marine state: Prohibit small artisanal fishing craft (<15m) and suspend recreational activities.")
            recommendations.append("Commercial vessels must adjust transit heading away from wave shear zones and reduce engine RPM.")
            recommendations.append("Maintain continuous radio watch on VHF Channel 16 for official INCOIS / IMD storm bulletins.")
        elif risk_level == "CAUTION":
            recommendations.append("Moderate risk conditions: Coastal fishing vessels operate with vigilance; avoid remote offshore banks.")
            recommendations.append("Check bilge pumps, secure deck cargo, and verify life-saving appliances before departure.")
            recommendations.append("Monitor 6-hour forecast updates for worsening sea state trends.")
        else:
            recommendations.append("Safe conditions: Normal maritime operations, artisanal fishing, and shipping navigation clear to proceed.")
            recommendations.append("Maintain standard watchkeeping and navigation safety protocols.")

        return {
            "risk_score": final_risk_score,
            "risk_level": risk_level,
            "confidence": avg_confidence,
            "uncertainty_level": uncertainty,
            "components": {
                "ocean_risk": ocean_risk_component,
                "weather_risk": weather_risk_component,
                "anomaly_risk": anomaly_risk_component,
                "ml_prediction_risk": ml_risk_component,
                "agent_confidence": avg_confidence
            },
            "key_risks": key_risks,
            "recommendations": recommendations,
            "positive_forces": positive_forces,
            "negative_forces": negative_forces
        }
