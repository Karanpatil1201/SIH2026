from app.fusion.conflict import ConflictResolutionEngine
from app.fusion.alignment import SpatialTemporalAlignmentEngine

def test_conflict_resolution():
    sources = [
        {"name": "Copernicus", "value": 28.4, "reliability": 0.95, "quality": 95, "freshness_weight": 0.95},
        {"name": "Sentinel-3", "value": 29.1, "reliability": 0.92, "quality": 90, "freshness_weight": 0.90}
    ]
    res = ConflictResolutionEngine.resolve_variable("sst", sources)
    assert 28.4 <= res["fused_value"] <= 29.1
    assert res["conflict_level"] == "LOW"

def test_spatial_alignment():
    snapped = SpatialTemporalAlignmentEngine.snap_to_marine_grid(18.9667, 72.8333)
    assert snapped["lat"] == 19.0
    assert snapped["lon"] == 72.8
