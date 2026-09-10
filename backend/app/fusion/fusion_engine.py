from typing import Dict, Any, Optional
from datetime import datetime, timezone

from app.data_quality.engine import DataQualityEngine
from app.provenance.engine import DataTrustEngine
from app.fusion.alignment import SpatialTemporalAlignmentEngine
from app.fusion.conflict import ConflictResolutionEngine
from app.models.schemas import CombinedMarineData, DataQualityReport

class DataFusionEngine:
    """
    Fuses heterogeneous data from Ocean, Weather, Satellite, and Advisory sources
    into a unified Marine Intelligence Record.
    """

    @classmethod
    def fuse_records(
        cls,
        lat: float,
        lon: float,
        ocean_raw: Optional[Dict[str, Any]] = None,
        weather_raw: Optional[Dict[str, Any]] = None,
        satellite_raw: Optional[Dict[str, Any]] = None,
        location_name: str = "Arabian Sea Offshore"
    ) -> CombinedMarineData:
        ocean = ocean_raw or {}
        weather = weather_raw or {}
        satellite = satellite_raw or {}

        # Helper to safely extract float with fallback when key is present but value is None
        def safe_float(val, default):
            if val is None:
                return default
            try:
                return float(val)
            except (ValueError, TypeError):
                return default

        # 1. Snap to standard Marine Grid & Normalize Timestamps
        grid = SpatialTemporalAlignmentEngine.snap_to_marine_grid(lat, lon)
        raw_ts = ocean.get("timestamp") or weather.get("timestamp") or datetime.now(timezone.utc).isoformat()
        normalized_ts = SpatialTemporalAlignmentEngine.normalize_timestamp(raw_ts)

        # 2. Extract key parameters across providers
        # Conflict resolution for SST (e.g. Satellite vs Copernicus vs Model)
        sst_sources = []
        if ocean.get("sst") is not None:
            sst_sources.append({"name": ocean.get("source", "Copernicus"), "value": safe_float(ocean["sst"], 28.5), "reliability": 0.95, "quality": 95, "freshness_weight": 0.95})
        if satellite.get("sst") is not None:
            sst_sources.append({"name": satellite.get("source", "Sentinel-3"), "value": safe_float(satellite["sst"], 28.5), "reliability": 0.92, "quality": 90, "freshness_weight": 0.90})

        fused_sst_res = ConflictResolutionEngine.resolve_variable("sst", sst_sources)
        final_sst = fused_sst_res["fused_value"] if sst_sources else safe_float(ocean.get("sst"), 28.5)

        # Build fused record fields with strict type safety
        fused_dict = {
            "latitude": grid["lat"],
            "longitude": grid["lon"],
            "timestamp": normalized_ts,
            "sst": final_sst,
            "wave_height": safe_float(ocean.get("wave_height"), 1.2),
            "wave_direction": safe_float(ocean.get("wave_direction"), 240.0),
            "wave_period": safe_float(ocean.get("wave_period"), 7.5),
            "swell_height": safe_float(ocean.get("swell_height"), 0.8),
            "current_velocity": safe_float(ocean.get("current_velocity"), 0.5),
            "wind_speed": safe_float(weather.get("wind_speed"), 18.5),
            "wind_direction": safe_float(weather.get("wind_direction"), 260.0),
            "pressure": safe_float(weather.get("pressure"), 1012.0),
            "precipitation": safe_float(weather.get("precipitation"), 0.0),
            "salinity": safe_float(ocean.get("salinity"), 35.5),
            "chlorophyll": safe_float(ocean.get("chlorophyll") or satellite.get("chlorophyll") or satellite.get("chlorophyll_sat"), 0.45),
            "sea_level": safe_float(ocean.get("sea_level"), 0.15)
        }

        # 3. Quality Evaluation
        quality_report = DataQualityEngine.evaluate_quality(fused_dict)

        # 4. Data Trust Score Calculation
        primary_source = ocean.get("source") or weather.get("source") or "Multi-Source Fused"
        trust_score = DataTrustEngine.calculate_trust_score(primary_source, quality_report)

        # Determine mode (LIVE vs DEMO)
        mode = ocean.get("mode") or weather.get("mode") or "LIVE"

        return CombinedMarineData(
            location={"lat": grid["lat"], "lon": grid["lon"], "name": location_name},
            timestamp=normalized_ts,
            sst=fused_dict["sst"],
            wave_height=fused_dict["wave_height"],
            wave_direction=fused_dict["wave_direction"],
            wave_period=fused_dict["wave_period"],
            swell_height=fused_dict["swell_height"],
            current_velocity=fused_dict["current_velocity"],
            wind_speed=fused_dict["wind_speed"],
            wind_direction=fused_dict["wind_direction"],
            pressure=fused_dict["pressure"],
            precipitation=fused_dict["precipitation"],
            salinity=fused_dict["salinity"],
            chlorophyll=fused_dict["chlorophyll"],
            sea_level=fused_dict["sea_level"],
            quality_report=quality_report,
            trust_score=trust_score,
            data_source_mode=mode,
            salinity_source=ocean.get("salinity_source", "fallback"),
            chlorophyll_source=ocean.get("chlorophyll_source", "fallback"),
            source=ocean.get("source") or weather.get("source") or "open-meteo",
            status=ocean.get("status") or weather.get("status") or "LIVE",
            live_data_available=bool(ocean.get("live_data_available", True) and weather.get("live_data_available", True)),
            fetched_at=ocean.get("fetched_at") or weather.get("fetched_at"),
            is_forecast=bool(ocean.get("is_forecast") or weather.get("is_forecast")),
            forecast_target=ocean.get("forecast_target") or weather.get("forecast_target")
        )
