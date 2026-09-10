from app.agents.safety_verification_agent import SafetyVerificationAgent

def test_safety_verification_guardrail_pass():
    agent = SafetyVerificationAgent()
    fused_data = {
        "wave_height": 1.2,
        "wind_speed": 14.0,
        "quality_report": {"freshness": "LIVE"}
    }
    geofence_data = {
        "findings": {
            "restricted_violations": [],
            "imbl_warnings": []
        }
    }
    hazard_data = {"alerts": []}
    
    result = agent.verify_safety(
        fused_data=fused_data,
        agent_findings=[],
        geofence_data=geofence_data,
        hazard_data=hazard_data
    )
    assert result["status"] == "PASSED"
    assert result["is_safety_verified"] is True

def test_safety_verification_guardrail_block_on_restricted_waters():
    agent = SafetyVerificationAgent()
    fused_data = {
        "wave_height": 1.2,
        "wind_speed": 14.0,
        "quality_report": {"freshness": "LIVE"}
    }
    geofence_data = {
        "findings": {
            "restricted_violations": [{"name": "Mumbai Naval Exclusion", "category": "DEFENCE"}],
            "imbl_warnings": []
        }
    }
    result = agent.verify_safety(
        fused_data=fused_data,
        agent_findings=[],
        geofence_data=geofence_data
    )
    assert result["status"] == "REJECTED_UNSAFE"
    assert result["is_safety_verified"] is False
    assert len(result["blockers"]) > 0
