from typing import Dict, Any, List
from app.ml.isolation_forest import AnomalyDetector

class AnomalyAgent:
    """
    Anomaly Agent evaluating Isolation Forest output to identify abnormal SST spikes,
    extreme wave surges, wind shear, and multivariate marine anomalies.
    """
    def __init__(self):
        self.name = "Anomaly Agent"
        self.detector = AnomalyDetector()

    def process(self, fused_data: Dict[str, Any]) -> Dict[str, Any]:
        is_anom, score, anomaly_type = self.detector.detect_anomaly(fused_data)
        
        reasons: List[str] = []
        recommendations: List[str] = []

        if is_anom:
            reasons.append(f"Environmental outlier detected: {anomaly_type} (Anomaly index: {score}).")
            recommendations.append("Cross-verify unexpected physical outlier in local telemetry.")
        else:
            reasons.append("Environmental variables within nominal multivariate distribution.")
            recommendations.append("Standard baseline conditions confirmed.")

        return {
            "agent": self.name,
            "status": "CAUTION" if is_anom else "SAFE",
            "confidence": round(1.0 - score * 0.3, 2),
            "findings": {
                "is_anomaly": is_anom,
                "anomaly_score": score,
                "anomaly_type": anomaly_type,
                "explanation": f"{anomaly_type} detected (score: {score})",
                "confidence": round(1.0 - score * 0.3, 2)
            },
            "reasons": reasons,
            "recommendations": recommendations
        }
