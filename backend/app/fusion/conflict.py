from typing import List, Dict, Any, Tuple

class ConflictResolutionEngine:
    """
    Resolves discrepancies between multi-source ocean and weather measurements
    using dynamic weighted consensus based on source reliability, quality, and freshness.
    """

    @classmethod
    def resolve_variable(
        cls,
        variable_name: str,
        sources: List[Dict[str, Any]]
        # Each source dict: {"name": str, "value": float, "reliability": float, "quality": float, "freshness_weight": float}
    ) -> Dict[str, Any]:
        if not sources:
            return {
                "fused_value": 0.0,
                "confidence": 0.0,
                "conflict_level": "UNKNOWN",
                "source_contributions": []
            }

        valid_sources = [s for s in sources if s.get("value") is not None]
        if not valid_sources:
            return {
                "fused_value": 0.0,
                "confidence": 0.0,
                "conflict_level": "NONE",
                "source_contributions": []
            }

        values = [s["value"] for s in valid_sources]
        val_range = max(values) - min(values)

        # Determine conflict level based on spread magnitude
        if val_range > 3.0 and variable_name in ["sst", "wave_height"]:
            conflict_level = "HIGH"
        elif val_range > 1.2:
            conflict_level = "MODERATE"
        else:
            conflict_level = "LOW"

        # Compute dynamic weights
        total_weight = 0.0
        weighted_sum = 0.0
        contributions = []

        for s in valid_sources:
            rel = s.get("reliability", 0.85)
            q = s.get("quality", 90.0) / 100.0
            f = s.get("freshness_weight", 0.9)
            
            # Composite weight
            w = rel * q * f
            total_weight += w
            weighted_sum += s["value"] * w
            
            contributions.append({
                "source": s["name"],
                "value": s["value"],
                "weight": round(w, 3)
            })

        fused_val = round(weighted_sum / max(total_weight, 1e-5), 2)

        # Calculate consensus confidence (penalized by conflict level)
        base_confidence = min(0.98, total_weight / len(valid_sources))
        if conflict_level == "HIGH":
            confidence = round(base_confidence * 0.75, 2)
        elif conflict_level == "MODERATE":
            confidence = round(base_confidence * 0.88, 2)
        else:
            confidence = round(base_confidence * 0.96, 2)

        return {
            "variable": variable_name,
            "fused_value": fused_val,
            "confidence": confidence,
            "conflict_level": conflict_level,
            "source_contributions": contributions
        }
