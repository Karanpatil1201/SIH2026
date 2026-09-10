"""
VARUNA Intent & Multi-Turn Context Extraction Agent
Converts natural language user queries (multilingual) into a rich StructuredContext
and manages multi-turn conversational session state.
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
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
        needs_ecosystem_reasoning: bool = False,
        location_source: str = "caller_coordinates",
        is_forecast: bool = False
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
        self.location_source = location_source
        self.is_forecast = is_forecast

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
            "needs_ecosystem_reasoning": self.needs_ecosystem_reasoning,
            "location_source": self.location_source,
            "is_forecast": self.is_forecast
        }

class IntentContextAgent:
    """
    Parses conversational queries into structured marine context and maintains multi-turn state.
    """

    DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")

    # Multilingual lookup for Indian ports and coastal marine sectors
    KNOWN_LOCATIONS = {
        # Ratnagiri
        "ratnagiri": {"name": "Ratnagiri Coastal Waters", "lat": 16.9902, "lon": 73.2980},
        "रत्नागिरी": {"name": "Ratnagiri Coastal Waters", "lat": 16.9902, "lon": 73.2980},
        "रत्नागिरि": {"name": "Ratnagiri Coastal Waters", "lat": 16.9902, "lon": 73.2980},
        
        # Mumbai
        "mumbai": {"name": "Mumbai Offshore Sector", "lat": 18.9667, "lon": 72.8333},
        "bombay": {"name": "Mumbai Offshore Sector", "lat": 18.9667, "lon": 72.8333},
        "मुंबई": {"name": "Mumbai Offshore Sector", "lat": 18.9667, "lon": 72.8333},
        "बॉम्बे": {"name": "Mumbai Offshore Sector", "lat": 18.9667, "lon": 72.8333},
        
        # Goa
        "goa": {"name": "Goa Coastal Waters (Mormugao)", "lat": 15.4989, "lon": 73.8278},
        "mormugao": {"name": "Goa Coastal Waters (Mormugao)", "lat": 15.4989, "lon": 73.8278},
        "panaji": {"name": "Goa Coastal Waters (Mormugao)", "lat": 15.4989, "lon": 73.8278},
        "गोवा": {"name": "Goa Coastal Waters (Mormugao)", "lat": 15.4989, "lon": 73.8278},
        "गोंय": {"name": "Goa Coastal Waters (Mormugao)", "lat": 15.4989, "lon": 73.8278},
        "पणजी": {"name": "Goa Coastal Waters (Mormugao)", "lat": 15.4989, "lon": 73.8278},
        
        # Rameshwaram
        "rameshwaram": {"name": "Rameshwaram Coastal Waters", "lat": 9.2876, "lon": 79.3129},
        "rameswaram": {"name": "Rameshwaram Coastal Waters", "lat": 9.2876, "lon": 79.3129},
        "रामेश्वरम": {"name": "Rameshwaram Coastal Waters", "lat": 9.2876, "lon": 79.3129},
        "रामेश्वर": {"name": "Rameshwaram Coastal Waters", "lat": 9.2876, "lon": 79.3129},
        "இராமேசுவரம்": {"name": "Rameshwaram Coastal Waters", "lat": 9.2876, "lon": 79.3129},

        # Kochi
        "kochi": {"name": "Kochi Coastal Sector", "lat": 9.9667, "lon": 76.2667},
        "cochin": {"name": "Kochi Coastal Sector", "lat": 9.9667, "lon": 76.2667},
        "कोची": {"name": "Kochi Coastal Sector", "lat": 9.9667, "lon": 76.2667},
        "कोचीन": {"name": "Kochi Coastal Sector", "lat": 9.9667, "lon": 76.2667},
        "കൊച്ചി": {"name": "Kochi Coastal Sector", "lat": 9.9667, "lon": 76.2667},
        
        # Mangalore
        "mangalore": {"name": "New Mangalore Offshore", "lat": 12.9242, "lon": 74.8190},
        "mangaluru": {"name": "New Mangalore Offshore", "lat": 12.9242, "lon": 74.8190},
        "मंगलोर": {"name": "New Mangalore Offshore", "lat": 12.9242, "lon": 74.8190},
        "मंगळूर": {"name": "New Mangalore Offshore", "lat": 12.9242, "lon": 74.8190},
        "ಮಂಗಳೂರು": {"name": "New Mangalore Offshore", "lat": 12.9242, "lon": 74.8190},

        # Vizhinjam
        "vizhinjam": {"name": "Vizhinjam Deepwater Sector", "lat": 8.3760, "lon": 76.9910},
        "विळिंजम": {"name": "Vizhinjam Deepwater Sector", "lat": 8.3760, "lon": 76.9910},

        # Tuticorin
        "tuticorin": {"name": "Tuticorin Marine Corridor", "lat": 8.7642, "lon": 78.1348},
        "thoothukudi": {"name": "Tuticorin Marine Corridor", "lat": 8.7642, "lon": 78.1348},
        "तुतिकोरीन": {"name": "Tuticorin Marine Corridor", "lat": 8.7642, "lon": 78.1348},
        "தூத்துக்குடி": {"name": "Tuticorin Marine Corridor", "lat": 8.7642, "lon": 78.1348},

        # Chennai
        "chennai": {"name": "Chennai Coastal Waters", "lat": 13.0827, "lon": 80.2707},
        "madras": {"name": "Chennai Coastal Waters", "lat": 13.0827, "lon": 80.2707},
        "चेन्नई": {"name": "Chennai Coastal Waters", "lat": 13.0827, "lon": 80.2707},
        "मद्रास": {"name": "Chennai Coastal Waters", "lat": 13.0827, "lon": 80.2707},
        "சென்னை": {"name": "Chennai Coastal Waters", "lat": 13.0827, "lon": 80.2707},

        # Visakhapatnam
        "visakhapatnam": {"name": "Visakhapatnam Zone", "lat": 17.6868, "lon": 83.2185},
        "vizag": {"name": "Visakhapatnam Zone", "lat": 17.6868, "lon": 83.2185},
        "विशाखापट्टणम": {"name": "Visakhapatnam Zone", "lat": 17.6868, "lon": 83.2185},
        "विझाग": {"name": "Visakhapatnam Zone", "lat": 17.6868, "lon": 83.2185},
        "విశాఖపట్నం": {"name": "Visakhapatnam Zone", "lat": 17.6868, "lon": 83.2185},

        # Kanyakumari
        "kanyakumari": {"name": "Kanyakumari Cape Zone", "lat": 8.0883, "lon": 77.5385},
        "कन्याकुमारी": {"name": "Kanyakumari Cape Zone", "lat": 8.0883, "lon": 77.5385},
        "கன்னியாகுமரி": {"name": "Kanyakumari Cape Zone", "lat": 8.0883, "lon": 77.5385},

        # Paradip
        "paradip": {"name": "Paradip Coastal Sector", "lat": 20.3165, "lon": 86.6114},
        "पारादीप": {"name": "Paradip Coastal Sector", "lat": 20.3165, "lon": 86.6114},

        # Kolkata / Haldia
        "kolkata": {"name": "Haldia / Sundarbans Marine Sector", "lat": 22.0257, "lon": 88.0583},
        "haldia": {"name": "Haldia / Sundarbans Marine Sector", "lat": 22.0257, "lon": 88.0583},
        "कोलकाता": {"name": "Haldia / Sundarbans Marine Sector", "lat": 22.0257, "lon": 88.0583},
        "हल्दिया": {"name": "Haldia / Sundarbans Marine Sector", "lat": 22.0257, "lon": 88.0583},

        # Veraval
        "veraval": {"name": "Veraval Offshore Bank", "lat": 20.9000, "lon": 70.3667},
        "वेरावळ": {"name": "Veraval Offshore Bank", "lat": 20.9000, "lon": 70.3667},
        "वेरावल": {"name": "Veraval Offshore Bank", "lat": 20.9000, "lon": 70.3667},

        # Kandla
        "kandla": {"name": "Gulf of Kutch (Kandla)", "lat": 23.0033, "lon": 70.2189},
        "कांडला": {"name": "Gulf of Kutch (Kandla)", "lat": 23.0033, "lon": 70.2189},

        # Coastal Maharashtra (Malvan, Alibaug, Khandala reference)
        "malvan": {"name": "Malvan Coastal Waters", "lat": 16.0558, "lon": 73.4668},
        "मालवण": {"name": "Malvan Coastal Waters", "lat": 16.0558, "lon": 73.4668},
        "alibaug": {"name": "Alibaug Coastal Sector", "lat": 18.6414, "lon": 72.8722},
        "अलिबाग": {"name": "Alibaug Coastal Sector", "lat": 18.6414, "lon": 72.8722},
        "खंडाळा": {"name": "Coastal Western Ghats / Konkan Sector", "lat": 18.7500, "lon": 73.3667},

        # Additional Key Ports and Coastal Sectors
        "karwar": {"name": "Karwar Coastal Sector", "lat": 14.8136, "lon": 74.1298},
        "कारवार": {"name": "Karwar Coastal Sector", "lat": 14.8136, "lon": 74.1298},
        "porbandar": {"name": "Porbandar Coastal Waters", "lat": 21.6417, "lon": 69.6293},
        "पोरबंदर": {"name": "Porbandar Coastal Waters", "lat": 21.6417, "lon": 69.6293},
        "daman": {"name": "Daman Coastal Zone", "lat": 20.3974, "lon": 72.8328},
        "दमण": {"name": "Daman Coastal Zone", "lat": 20.3974, "lon": 72.8328},
        "diu": {"name": "Diu Coastal Waters", "lat": 20.7144, "lon": 70.9874},
        "दीव": {"name": "Diu Coastal Waters", "lat": 20.7144, "lon": 70.9874},
        "digha": {"name": "Digha Marine Sector", "lat": 21.6266, "lon": 87.5074},
        "दिघा": {"name": "Digha Marine Sector", "lat": 21.6266, "lon": 87.5074},
        "puri": {"name": "Puri Coastal Sector", "lat": 19.8135, "lon": 85.8312},
        "पुरी": {"name": "Puri Coastal Sector", "lat": 19.8135, "lon": 85.8312},
        "port blair": {"name": "Andaman Marine Sector (Port Blair)", "lat": 11.6234, "lon": 92.7265},
        "andaman": {"name": "Andaman Islands Marine Sector", "lat": 11.6234, "lon": 92.7265},
        "अंदमान": {"name": "Andaman Islands Marine Sector", "lat": 11.6234, "lon": 92.7265},
        "lakshadweep": {"name": "Lakshadweep Archipelago Sector", "lat": 10.5667, "lon": 72.6417},
        "लक्षद्वीप": {"name": "Lakshadweep Archipelago Sector", "lat": 10.5667, "lon": 72.6417}
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
        Explicit coordinates and specific city/port names in the CURRENT query ALWAYS override prior session location.
        """
        # Normalize any Devanagari numerals (०-९) to ASCII 0-9
        normalized_query = query.translate(self.DEVANAGARI_DIGITS)
        q_lower = normalized_query.lower()
        detected_lang = LanguageService.detect_language(query)

        # Retrieve prior session context if multi-turn
        prior: Optional[StructuredContext] = self._session_contexts.get(session_id) if session_id else None

        # 1. Coordinate & Location Extraction for THIS query
        # PRIORITY 1: Explicit Coordinates in THIS query MUST win
        coord_regex = re.compile(
            r'(?:lat(?:itude)?\s*[:=]?\s*)?(-?\d+(?:\.\d+)?)\s*(?:°|deg)?\s*([NSns])?\s*[,;\s/|]+\s*(?:lon(?:gitude)?\s*[:=]?\s*)?(-?\d+(?:\.\d+)?)\s*(?:°|deg)?\s*([EWew])?',
            re.IGNORECASE
        )
        coord_match = coord_regex.search(normalized_query)

        has_query_coords = False
        lat: Optional[float] = None
        lon: Optional[float] = None
        loc_name: Optional[str] = None
        location_source: Optional[str] = None

        if coord_match:
            try:
                raw_lat = float(coord_match.group(1))
                lat_hemi = (coord_match.group(2) or '').upper()
                if lat_hemi == 'S':
                    raw_lat = -abs(raw_lat)
                elif lat_hemi == 'N':
                    raw_lat = abs(raw_lat)

                raw_lon = float(coord_match.group(3))
                lon_hemi = (coord_match.group(4) or '').upper()
                if lon_hemi == 'W':
                    raw_lon = -abs(raw_lon)
                elif lon_hemi == 'E':
                    raw_lon = abs(raw_lon)

                if -90 <= raw_lat <= 90 and -180 <= raw_lon <= 180:
                    lat = round(raw_lat, 4)
                    lon = round(raw_lon, 4)
                    loc_name = f"Coordinates ({lat:.2f}°N, {lon:.2f}°E)"
                    location_source = "explicit_coordinates"
                    has_query_coords = True
                    print(f"[LOCATION] lat={lat} lon={lon} source=explicit_coordinates", flush=True)
            except (ValueError, TypeError):
                pass

        # PRIORITY 2: If no coordinates, check if user mentioned a known location in THIS query
        has_query_location = False
        if not has_query_coords:
            for key, info in sorted(self.KNOWN_LOCATIONS.items(), key=lambda x: len(x[0]), reverse=True):
                # Match word boundary or full substring for Indic scripts
                pattern = r'(?:\b|_|^)' + re.escape(key) + r'(?:\b|_|$)'
                if re.search(pattern, q_lower) or (len(key) >= 3 and key in q_lower):
                    lat = info["lat"]
                    lon = info["lon"]
                    loc_name = info["name"]
                    location_source = "extracted_location"
                    has_query_location = True
                    print(f"[LOCATION] lat={lat} lon={lon} source=extracted_location name='{loc_name}'", flush=True)
                    break

        # PRIORITY 3: If neither coordinates nor location was stated in THIS query, use caller or prior
        if not has_query_coords and not has_query_location:
            # If caller coordinates were supplied and differ from default Mumbai (e.g. user selected map pin):
            if current_lat is not None and current_lon is not None and (current_lat != 18.9667 or current_lon != 72.8333):
                lat = current_lat
                lon = current_lon
                loc_name = f"Sector ({lat:.2f}°N, {lon:.2f}°E)"
                location_source = "caller_coordinates"
            elif prior:
                lat = prior.latitude
                lon = prior.longitude
                loc_name = prior.location_name
                location_source = prior.location_source
                print(f"[LOCATION] Inherited prior session location lat={lat} lon={lon} source={location_source}", flush=True)
            else:
                lat = current_lat
                lon = current_lon
                loc_name = f"Sector ({lat:.2f}°N, {lon:.2f}°E)"
                location_source = "caller_coordinates"

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

        # 4. Target Time & Departure Hour (Forecast detection)
        now_utc = datetime.now(timezone.utc)
        target_time = "current"
        departure_hour = None
        is_forecast = False

        is_tomorrow = any(w in q_lower for w in ["tomorrow", "tommorrow", "tomorow", "tmrw", "उद्या", "कल"])
        
        # Check relative hour offsets: "next 1 hr", "next 2 hours", "next hour", "in 1 hr", "पुढील १ तास", "अगले 1 घंटे"
        next_hr_match = re.search(r'(?:next|in|पुढील|अगले)\s*(\d{1,2})?\s*(?:hr|hour|hrs|hours|तास|घंटे)', q_lower)
        
        # Time of day detection
        is_morning = any(w in q_lower for w in ["morning", "moring", "dawn", "सकाळी", "सुबह", "प्रभात"])
        is_afternoon = any(w in q_lower for w in ["afternoon", "noon", "दुपारी", "दोपहर"])
        is_evening = any(w in q_lower for w in ["evening", "dusk", "सायंकाळी", "संध्याकाळी", "शाम"])
        is_night = any(w in q_lower for w in ["night", "रात्री", "रात"])

        # Match specific departure hour (e.g. 5 AM, 6 AM, 8 AM, 06:00, ६ वाजता, सकाळी ६, सुबह 6)
        if "6 am" in q_lower or "6:00" in q_lower or "6am" in q_lower or "सकाळी 6" in q_lower or "6 वाजता" in q_lower or "सुबह 6" in q_lower:
            departure_hour = 6
        elif "5 am" in q_lower or "5:00" in q_lower or "5am" in q_lower or "सकाळी 5" in q_lower or "5 वाजता" in q_lower or "सुबह 5" in q_lower:
            departure_hour = 5
        elif "8 am" in q_lower or "8:00" in q_lower or "8am" in q_lower or "सकाळी 8" in q_lower or "8 वाजता" in q_lower or "सुबह 8" in q_lower:
            departure_hour = 8
        elif "10 am" in q_lower or "10:00" in q_lower or "10am" in q_lower or "सकाळी 10" in q_lower or "10 वाजता" in q_lower or "सुबह 10" in q_lower:
            departure_hour = 10
        elif is_morning:
            departure_hour = 6
        elif is_afternoon:
            departure_hour = 14
        elif is_evening:
            departure_hour = 18
        elif is_night:
            departure_hour = 21

        if is_tomorrow:
            is_forecast = True
            dep_hr = departure_hour if departure_hour is not None else 6
            target_time = f"tomorrow {dep_hr:02d}:00"
        elif next_hr_match or "next hr" in q_lower or "next hour" in q_lower:
            is_forecast = True
            offset_h = int(next_hr_match.group(1)) if (next_hr_match and next_hr_match.group(1)) else 1
            target_dt = now_utc + timedelta(hours=offset_h)
            departure_hour = target_dt.hour
            target_time = f"today {target_dt.hour:02d}:00"
        elif departure_hour is not None:
            is_forecast = True
            target_time = f"today {departure_hour:02d}:00"

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
            needs_ecosystem_reasoning=(has_ecosystem or intent == "ecosystem_reasoning"),
            location_source=location_source,
            is_forecast=is_forecast
        )

        # Store in session memory
        if session_id:
            self._session_contexts[session_id] = ctx

        return ctx

    def clear_session(self, session_id: str):
        if session_id in self._session_contexts:
            del self._session_contexts[session_id]
