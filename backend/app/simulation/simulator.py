from typing import Dict, Any, List
from app.ml.xgboost_risk import XGBoostRiskModel
from app.providers.demo import DemoOceanProvider
from app.models.schemas import WhatIfRequest, WhatIfResponse

class WhatIfSimulationEngine:
    """
    What-If Simulation Engine evaluating sensitivity of Marine Risk to parameter changes.
    Simulates scenarios like Wind +20%, Wave +30%, Pressure -15 hPa.
    """

    def __init__(self):
        self.xgb_model = XGBoostRiskModel()

    def run_simulation(self, req: WhatIfRequest) -> WhatIfResponse:
        # 1. Retrieve base environmental state
        base_record = DemoOceanProvider.get_demo_record(req.lat, req.lon)
        orig_risk, orig_level = self.xgb_model.predict_risk(base_record)

        # 2. Apply scenario multipliers & deltas
        sim_record = base_record.copy()
        
        sim_wind = base_record["wind_speed"] * (1.0 + req.wind_increase_pct / 100.0)
        sim_wave = base_record["wave_height"] * (1.0 + req.wave_increase_pct / 100.0)
        sim_press = base_record["pressure"] - req.pressure_drop_hpa

        sim_record["wind_speed"] = round(sim_wind, 1)
        sim_record["wave_height"] = round(sim_wave, 2)
        sim_record["pressure"] = round(sim_press, 1)

        sim_risk, sim_level = self.xgb_model.predict_risk(sim_record)
        risk_delta = round(sim_risk - orig_risk, 1)

        contributions: List[str] = []
        if req.wind_increase_pct > 0:
            contributions.append(f"Wind speed surge (+{req.wind_increase_pct}%) to {round(sim_wind, 1)} km/h")
        if req.wave_increase_pct > 0:
            contributions.append(f"Wave height amplification (+{req.wave_increase_pct}%) to {round(sim_wave, 2)} m")
        if req.pressure_drop_hpa > 0:
            contributions.append(f"Atmospheric pressure drop (-{req.pressure_drop_hpa} hPa) to {round(sim_press, 1)} hPa")

        if not contributions:
            contributions.append("No parameter modifications applied.")

        impact_desc = "Significant risk elevation on coastal and offshore routes." if risk_delta > 15 else "Moderate risk shift; manageable under standard precaution."

        explanation = (
            f"Model-based simulation indicates that modifying environmental inputs results in a "
            f"risk score change of {risk_delta:+0.1f} points (from {orig_risk} [{orig_level}] to {sim_risk} [{sim_level}])."
        )

        return WhatIfResponse(
            original_risk=orig_risk,
            simulated_risk=sim_risk,
            risk_delta=risk_delta,
            original_level=orig_level,
            simulated_level=sim_level,
            affected_route_impact=impact_desc,
            top_contributing_changes=contributions,
            explanation=explanation
        )
