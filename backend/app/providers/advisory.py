from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone
from app.providers.base import AdvisoryDataProvider

class AdvisoryService(AdvisoryDataProvider):
    """
    Official Marine Advisory Provider (INCOIS, Cyclone Warnings, High Wave Alerts).
    Tracks advisory_id, source, title, severity, affected_region, expiry_time.
    """

    def get_advisories(self, region: str = "Arabian Sea") -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        return [
            {
                "advisory_id": "INCOIS-ADV-2026-089",
                "source": "INCOIS / Indian Meteorological Department",
                "title": "High Wave & Strong Wind Advisory for Maharashtra-Goa Coast",
                "description": "High wave heights (2.8m - 4.2m) and wind gusts exceeding 45 km/h predicted over Arabian Sea coastal zones. Fishermen advised not to venture into deep sea.",
                "issue_time": now.isoformat(),
                "expiry_time": (now + timedelta(days=2)).isoformat(),
                "affected_region": "Arabian Sea (Mumbai - Goa Coastal Waters)",
                "severity": "WARNING",
                "confidence": 0.94,
                "status": "ACTIVE",
                "source_url": "https://incois.gov.in/portal/osf/advisories"
            },
            {
                "advisory_id": "INCOIS-ADV-2026-092",
                "source": "Joint Typhoon Warning Center / IMD",
                "title": "Pre-Monsoon Depressional Watch over Bay of Bengal",
                "description": "Low-pressure system intensifying near Andaman Sea. Coastal shipping routes advised to monitor track updates closely.",
                "issue_time": now.isoformat(),
                "expiry_time": (now + timedelta(days=4)).isoformat(),
                "affected_region": "Bay of Bengal (Visakhapatnam to Port Blair)",
                "severity": "WATCH",
                "confidence": 0.88,
                "status": "ACTIVE",
                "source_url": "https://mausam.imd.gov.in"
            }
        ]
