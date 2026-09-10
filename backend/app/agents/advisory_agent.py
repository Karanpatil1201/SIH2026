from typing import Dict, Any
from app.providers.advisory import AdvisoryService

class AdvisoryAgent:
    """
    Advisory Agent checking official government marine warnings, INCOIS alerts,
    and cyclone bulletins affecting the query location.
    """
    def __init__(self):
        self.service = AdvisoryService()

    def process(self, region: str = "Arabian Sea") -> Dict[str, Any]:
        advisories = self.service.get_advisories(region)
        active_count = len(advisories)
        max_severity = "INFO"
        if any(a["severity"] == "CRITICAL" for a in advisories):
            max_severity = "CRITICAL"
        elif any(a["severity"] in ["WARNING", "SEVERE"] for a in advisories):
            max_severity = "WARNING"

        return {
            "agent": "AdvisoryAgent",
            "status": "COMPLETED",
            "findings": {
                "active_advisories_count": active_count,
                "max_severity": max_severity,
                "advisories": advisories
            }
        }
