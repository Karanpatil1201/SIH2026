from datetime import datetime, timezone
from app.data_quality.engine import DataQualityEngine

def test_data_quality_valid():
    sample = {
        "latitude": 18.9667,
        "longitude": 72.8333,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sst": 28.5,
        "wave_height": 1.5,
        "wave_direction": 240.0,
        "wave_period": 7.0,
        "swell_height": 0.8,
        "current_velocity": 0.4,
        "wind_speed": 18.0,
        "wind_direction": 250.0,
        "pressure": 1012.0,
        "salinity": 35.0,
        "chlorophyll": 0.5,
        "sea_level": 0.1
    }
    report = DataQualityEngine.evaluate_quality(sample)
    assert report.status == "VALID"
    assert report.quality_score >= 90.0

def test_data_quality_out_of_bounds():
    sample_invalid = {
        "latitude": 18.9667,
        "longitude": 72.8333,
        "timestamp": "2026-09-05T12:00:00Z",
        "sst": -100.0, # Impossible SST value
        "wave_height": 1.5
    }
    report = DataQualityEngine.evaluate_quality(sample_invalid)
    assert report.status in ["WARNING", "INVALID"]
    assert "sst" in report.anomalies
