from typing import Dict, Any
from app.models.schemas import ProvenanceMetadata, DataQualityReport

class DataTrustEngine:
    """
    Computes a transparent Data Trust Score (0 - 100) and tracks data provenance.
    Source reliability + Freshness + Quality + Completeness + Consistency.
    """

    # Baseline reliability rating by provider source
    SOURCE_RELIABILITY = {
        "Copernicus": 0.95,
        "Open-Meteo Marine": 0.90,
        "Open-Meteo Weather": 0.90,
        "INCOIS Advisories": 0.98,
        "Sentinel Satellite": 0.92,
        "NASA Earthdata": 0.94,
        "Demo Provider": 0.85,
    }

    @classmethod
    def calculate_trust_score(
        cls,
        source_name: str,
        quality_report: DataQualityReport,
        completeness_ratio: float = 1.0
    ) -> float:
        reliability = cls.SOURCE_RELIABILITY.get(source_name, 0.80)
        
        # Freshness multiplier
        freshness_map = {"LIVE": 1.0, "RECENT": 0.9, "DELAYED": 0.75, "STALE": 0.5, "DEMO": 0.85}
        freshness_score = freshness_map.get(quality_report.freshness, 0.8)

        # Quality score component (0 to 1.0)
        q_norm = quality_report.quality_score / 100.0

        # Formula: Weighted composite score
        trust = (
            0.35 * reliability +
            0.30 * q_norm +
            0.20 * freshness_score +
            0.15 * completeness_ratio
        ) * 100.0

        return round(trust, 1)

    @classmethod
    def create_provenance_record(
        cls,
        data_point: Dict[str, Any],
        source_name: str,
        dataset_name: str,
        quality_report: DataQualityReport
    ) -> ProvenanceMetadata:
        lat = data_point.get("latitude", 0.0)
        lon = data_point.get("longitude", 0.0)
        ts = str(data_point.get("timestamp", ""))

        trust = cls.calculate_trust_score(source_name, quality_report)
        confidence = round(trust / 100.0, 2)

        return ProvenanceMetadata(
            source=source_name,
            dataset=dataset_name,
            timestamp=ts,
            location={"lat": lat, "lon": lon},
            processing_step="Quality Validation & Provenance Enrichment",
            quality_score=quality_report.quality_score,
            trust_score=trust,
            freshness=quality_report.freshness,
            confidence=confidence
        )
