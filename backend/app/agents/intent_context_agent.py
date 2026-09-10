"""
VARUNA Intent & Multi-Turn Context Extraction Agent
Converts natural language user queries (multilingual) into a rich StructuredContext
and manages multi-turn conversational session state.
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.agents.language_service import LanguageService
from app.gis.spatial_data import COASTAL_PORTS_AND_HARBOURS

class StructuredContext:
    def __init__(
        self,
        intent: str,
        user_type: str = "fisherman",
        vessel_type: str = "artisanal",
        location_name: str = "Mumbai Offshore",
        latitude: float = 18.9667,
        longitude: float = 72.8333,
        destination_name: Optional[str] = None,
        dest_latitude: Optional[float] = None,
        dest_longitude: Optional[float] = None,
        target_time: str = "current",
        departure_hour: Optional[int] = None,
        language: str = "en",
        needs_pfz: bool = False,
        needs_weather: bool = True,
        needs_ocean: bool = True,
        needs_satellite: bool = False,
        needs_hazard_check: bool = True,
        needs_geofence_check: bool = True,
        needs_route: bool = False,
        needs_departure_optimization: bool = False,
        needs_ecosystem_reasoning: bool = False
    ):
        self.intent = intent
        self.user_type = user_type
        self.vessel_type = vessel_type
        self.location_name = location_name
        self.latitude = latitude
        self.longitude = longitude
        self.destination_name = destination_name
        self.dest_latitude = dest_latitude
        self.dest_longitude = dest_longitude
        self.target_time = target_time
        self.departure_hour = departure_hour
        self.language = language
        self.needs_pfz = needs_pfz
        self.needs_weather = needs_weather
        self.needs_ocean = needs_ocean
        self.needs_satellite = needs_satellite
        self.needs_hazard_check = needs_hazard_check
        self.needs_geofence_check = needs_geofence_check
        self.needs_route = needs_route
        self.needs_departure_optimization = needs_departure_optimization
        self.needs_ecosystem_reasoning = needs_ecosystem_reasoning

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "user_type": self.user_type,
            "vessel_type": self.vessel_type,
            "location_name": self.location_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "destination_name": self.destination_name,
            "dest_latitude": self.dest_latitude,
            "dest_longitude": self.dest_longitude,
            "target_time": self.target_time,
            "departure_hour": self.departure_hour,
            "language": self.language,
            "needs_pfz": self.needs_pfz,
            "needs_weather": self.needs_weather,
            "needs_ocean": self.needs_ocean,
            "needs_satellite": self.needs_satellite,
            "needs_hazard_check": self.needs_hazard_check,
            "needs_geofence_check": self.needs_geofence_check,
            "needs_route": self.needs_route,
            "needs_departure_optimization": self.needs_departure_optimization,
            "needs_ecosystem_reasoning": self.needs_ecosystem_reasoning
        }

class IntentContextAgent:
    """
    Parses conversational queries into structured marine context and maintains multi-turn state.
    """

    KNOWN_LOCATIONS = {
        "ratnagiri": {"name": "Ratnagiri Coastal Waters", "lat": 16.9902, "lon": 73.2980},
        "mumbai": {"name": "Mumbai Offshore Sector", "lat": 18.9667, "lon": 72.8333},
        "bombay": {"name": "Mumbai Offshore Sector", "lat": 18.9667, "lon": 72.8333},
        "goa": {"name": "Goa Coastal Waters (Mormugao)", "lat": 15.4989, "lon": 73.8278},
        "mormugao": {"name": "Goa Coastal Waters (Mormugao)", "lat": 15.4989, "lon": 73.8278},
        "mangalore": {"name": "New Mangalore Offshore", "lat": 12.9242, "lon": 74.8190},
        "kochi": {"name": "Kochi Coastal Sector", "lat": 9.9667, "lon": 76.2667},
        "cochin": {"name": "Kochi Coastal Sector", "lat": 9.9667, "lon": 76.2667},
        "vizhinjam": {"name": "Vizhinjam Deepwater Sector", "lat": 8.3760, "lon": 76.9910},
        "tuticorin": {"name": "Tuticorin Marine Corridor", "lat": 8.7642, "lon": 78.1348},
        "chennai": {"name": "Chennai Coastal Waters", "lat": 13.0827, "lon": 80.2707},
        "visakhapatnam": {"name": "Visakhapatnam Zone", "lat": 17.6868, "lon": 83.2185},
        "vizag": {"name": "Visakhapatnam Zone", "lat": 17.6868, "lon": 83.2185},
        "paradip": {"name": "Paradip Coastal Sector", "lat": 20.3165, "lon": 86.6114},
        "kolkata": {"name": "Haldia / Sundarbans Marine Sector", "lat": 22.0257, "lon": 88.0583},
        "veraval": {"name": "Veraval Offshore Bank", "lat": 20.9000, "lon": 70.3667},
        "kandla": {"name": "Gulf of Kutch (Kandla)", "lat": 23.0033, "lon": 70.2189}
    }

    def __init__(self):
        self.name = "Intent & Context Agent"
        self._session_contexts: Dict[str, StructuredContext] = {}

    def extract_context(
        self,
        query: str,
        current_lat: float = 18.9667,
        current_lon: float = 72.8333,
        session_id: Optional[str] = None
    ) -> StructuredContext:
        """
        Parses the query, merges with previous session context if present, and outputs StructuredContext.
        """
        q_lower = query.lower()
        detected_lang = LanguageService.detect_language(query)

        # Retrieve prior session context if multi-turn
        prior: Optional[StructuredContext] = self._session_contexts.get(session_id) if session_id else None

        # 1. Location extraction
        lat = prior.latitude if prior else current_lat
        lon = prior.longitude if prior else current_lon
        loc_name = prior.location_name if prior else "Target Marine Sector"

        for key, info in self.KNOWN_LOCATIONS.items():
            if key in q_lower:
                lat = info["lat"]
                lon = info["lon"]
                loc_name = info["name"]
                break

        # Check for explicit coordinates in query: e.g. "16.99, 73.29" or "lat 18.5 lon 72.8"
        coord_match = re.search(r'(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)', query)
        if coord_match:
            try:
                c_lat = float(coord_match.group(1))
                c_lon = float(coord_match.group(2))
                if -90 <= c_lat <= 90 and -180 <= c_lon <= 180:
                    lat, lon = c_lat, c_lon
                    loc_name = f"Custom Coordinates ({lat:.2f}, {lon:.2f})"
            except ValueError:
                pass

        # 2. Destination extraction
        dest_name = prior.destination_name if prior else None
        dest_lat = prior.dest_latitude if prior else None
        dest_lon = prior.dest_longitude if prior else None

        if " to " in q_lower or " ते " in q_lower or " se " in q_lower or " tak " in q_lower:
            for key, info in self.KNOWN_LOCATIONS.items():
                if f"to {key}" in q_lower or f"कडे {key}" in q_lower or f"तक {key}" in q_lower:
                    dest_name = info["name"]
                    dest_lat = info["lat"]
                    dest_lon = info["lon"]
                    break

        # 3. User & Vessel Persona
        user_type = prior.user_type if prior else "fisherman"
        vessel_type = prior.vessel_type if prior else "artisanal"

        if any(w in q_lower for w in ["fisherman", "fishermen", "मासेमार", "मछुआरा", "மீனவர்", "trawler", "boat"]):
            user_type = "fisherman"
            vessel_type = "artisanal"
        elif any(w in q_lower for w in ["commercial", "cargo", "tanker", "shipping", "vessel master", "ship"]):
            user_type = "shipping"
            vessel_type = "commercial"
        elif any(w in q_lower for w in ["researcher", "scientist", "coral", "bleaching", "ecology", "dhw"]):
            user_type = "researcher"
        elif any(w in q_lower for w in ["disaster", "ndma", "coast guard", "authority", "navy", "cyclone"]):
            user_type = "disaster_authority"

        # 4. Target Time & Departure Hour
        target_time = prior.target_time if prior else "current"
        departure_hour = prior.departure_hour if prior else None

        # Check for specific hours: "6 AM", "06:00", "8 am", "८ वाजता", "6am"
        hour_match = re.search(r'(\d{1,2})\s*(am|pm|वाजता|बजे|:00)?', q_lower)
        if "6 am" in q_lower or "6:00" in q_lower or "६ वाजता" in q_lower or "6am" in q_lower:
            departure_hour = 6
            target_time = "tomorrow 06:00" if ("tomorrow" in q_lower or "उद्या" in q_lower or "कल" in q_lower or "tomorrow" in target_time) else "06:00"
        elif "8 am" in q_lower or "8:00" in q_lower or "८ वाजता" in q_lower or "8am" in q_lower:
            departure_hour = 8
            target_time = "tomorrow 08:00" if ("tomorrow" in q_lower or "उद्या" in q_lower or "कल" in q_lower or "tomorrow" in target_time) else "08:00"
        elif "10 am" in q_lower or "10:00" in q_lower or "१० वाजता" in q_lower or "10am" in q_lower:
            departure_hour = 10
            target_time = "10:00"
        elif "tomorrow" in q_lower or "उद्या" in q_lower or "कल" in q_lower:
            target_time = "tomorrow"
            if not departure_hour:
                departure_hour = 6

        # 5. Intent Determination
        has_fish = any(w in q_lower for w in ["fish", "pfz", "catch", "zone", "मासे", "मछली", "மீன்", "చేపలు"])
        has_route = any(w in q_lower for w in ["route", "path", "corridor", "goa", "sailing", "मार्ग", "रास्ता", "பாதை"])
        has_safety = any(w in q_lower for w in ["safe", "safety", "danger", "risk", "सुरक्षित", "खतरा", "धोका", "பாதுகாப்பு"])
        has_ecosystem = any(w in q_lower for w in ["productivity", "decreased", "decline", "coral", "bleaching", "ecosystem", "कमी", "घट"])
        has_hazard = any(w in q_lower for w in ["cyclone", "lightning", "storm", "gale", "alert", "warning", "विजा", "वादळ", "तूफान"])

        if has_fish and (has_route or has_safety or departure_hour is not None):
            intent = "fishing_safety_and_route"
        elif has_ecosystem:
            intent = "ecosystem_reasoning"
        elif has_route:
            intent = "route_planning"
        elif has_fish:
            intent = "pfz_lookup"
        elif has_hazard:
            intent = "hazard_check"
        elif prior:
            intent = prior.intent
        else:
            intent = "marine_safety"

        # Construct new structured context
        ctx = StructuredContext(
            intent=intent,
            user_type=user_type,
            vessel_type=vessel_type,
            location_name=loc_name,
            latitude=lat,
            longitude=lon,
            destination_name=dest_name,
            dest_latitude=dest_lat,
            dest_longitude=dest_lon,
            target_time=target_time,
            departure_hour=departure_hour,
            language=detected_lang,
            needs_pfz=(has_fish or intent in ["fishing_safety_and_route", "pfz_lookup"]),
            needs_weather=True,
            needs_ocean=True,
            needs_satellite=(has_fish or has_ecosystem),
            needs_hazard_check=True,
            needs_geofence_check=True,
            needs_route=(has_route or intent in ["fishing_safety_and_route", "route_planning"]),
            needs_departure_optimization=(departure_hour is not None or "when" in q_lower or "केव्हा" in q_lower or "कब" in q_lower),
            needs_ecosystem_reasoning=(has_ecosystem or intent == "ecosystem_reasoning")
        )

        # Store in session memory
        if session_id:
            self._session_contexts[session_id] = ctx

        return ctx

    def clear_session(self, session_id: str):
        if session_id in self._session_contexts:
            del self._session_contexts[session_id]
