"""
VARUNA Marine Spatial GIS Data
Provides precise geographic polygon and polyline definitions for:
1. International Maritime Boundary Lines (IMBL)
2. Restricted Waters & Naval Exclusion Zones
3. Marine Protected Areas (MPAs)
4. Ecologically Sensitive Marine Zones (ESZs)
"""

from typing import List, Dict, Any

# ── 1. International Maritime Boundary Lines (Polylines) ─────────────────────
IMBL_BOUNDARIES = [
    {
        "id": "IMBL_IN_PK",
        "name": "India - Pakistan International Maritime Boundary",
        "region": "Arabian Sea (Gujarat / Sir Creek Offshore)",
        "coordinates": [
            [23.58, 68.10],
            [23.40, 67.80],
            [23.15, 67.40],
            [22.80, 66.80],
            [22.40, 66.20],
            [21.80, 65.50],
            [21.00, 64.50]
        ],
        "warning_threshold_km": 15.0,
        "critical_threshold_km": 5.0,
        "advisory": "Approaching India-Pakistan IMBL. Unlicensed vessels risk interdiction."
    },
    {
        "id": "IMBL_IN_LK",
        "name": "India - Sri Lanka International Maritime Boundary",
        "region": "Palk Strait & Gulf of Mannar",
        "coordinates": [
            [10.08, 79.86],
            [9.75, 79.54],
            [9.42, 79.38],
            [9.10, 79.25],
            [8.80, 79.05],
            [8.40, 78.85],
            [7.90, 78.50]
        ],
        "warning_threshold_km": 12.0,
        "critical_threshold_km": 4.0,
        "advisory": "Approaching India-Sri Lanka IMBL (Katchatheevu / Palk Bay). Cross-border fishing strictly prohibited."
    },
    {
        "id": "IMBL_IN_BD",
        "name": "India - Bangladesh International Maritime Boundary",
        "region": "Bay of Bengal (Sundarbans Offshore)",
        "coordinates": [
            [21.65, 89.15],
            [21.30, 89.25],
            [20.80, 89.40],
            [20.20, 89.60],
            [19.50, 89.90]
        ],
        "warning_threshold_km": 10.0,
        "critical_threshold_km": 3.0,
        "advisory": "Approaching India-Bangladesh Maritime Boundary line."
    },
    {
        "id": "IMBL_IN_MV",
        "name": "India - Maldives International Maritime Boundary",
        "region": "Eight Degree Channel (Lakshadweep / Minicoy)",
        "coordinates": [
            [7.85, 71.50],
            [7.50, 72.50],
            [7.15, 73.50],
            [6.80, 74.50]
        ],
        "warning_threshold_km": 12.0,
        "critical_threshold_km": 4.0,
        "advisory": "Approaching India-Maldives EEZ Boundary corridor."
    }
]

# ── 2. Restricted Waters & Naval / Industrial Exclusion Zones (Polygons) ──────
RESTRICTED_ZONES = [
    {
        "id": "RESTRICTED_MUMBAI_NAVAL",
        "name": "Mumbai Harbour Naval & BARC Exclusion Zone",
        "category": "DEFENCE_SECURITY",
        "polygon": [
            [18.90, 72.80],
            [18.98, 72.82],
            [19.03, 72.92],
            [18.96, 72.96],
            [18.88, 72.88]
        ],
        "penalty_weight": 1000.0,
        "hard_block": True,
        "reason": "Restricted military & atomic research security area. Civilian transit prohibited."
    },
    {
        "id": "RESTRICTED_MUMBAI_HIGH_NORTH",
        "name": "Mumbai High Offshore Oil Rig Field (North Sector)",
        "category": "OIL_GAS_SAFETY",
        "polygon": [
            [19.50, 71.20],
            [19.80, 71.20],
            [19.80, 71.55],
            [19.50, 71.55]
        ],
        "penalty_weight": 500.0,
        "hard_block": True,
        "reason": "ONGC offshore drilling platforms & 500m safety exclusion perimeter."
    },
    {
        "id": "RESTRICTED_MUMBAI_HIGH_SOUTH",
        "name": "Mumbai High Offshore Oil Rig Field (South Sector)",
        "category": "OIL_GAS_SAFETY",
        "polygon": [
            [18.80, 71.30],
            [19.20, 71.30],
            [19.20, 71.65],
            [18.80, 71.65]
        ],
        "penalty_weight": 500.0,
        "hard_block": True,
        "reason": "Active hydrocarbon production platforms with underwater pipeline network."
    },
    {
        "id": "RESTRICTED_VIZAG_NAVAL_RANGE",
        "name": "Eastern Naval Command Firing Range (Visakhapatnam)",
        "category": "DEFENCE_FIRING",
        "polygon": [
            [17.40, 83.40],
            [17.70, 83.50],
            [17.65, 83.85],
            [17.30, 83.75]
        ],
        "penalty_weight": 800.0,
        "hard_block": True,
        "reason": "Active naval live-fire exercise & submarine test corridor."
    },
    {
        "id": "RESTRICTED_CHANDIPUR_ITR",
        "name": "DRDO Chandipur Integrated Test Range Hazard Zone",
        "category": "DEFENCE_MISSILE_TEST",
        "polygon": [
            [21.20, 87.00],
            [21.55, 87.10],
            [21.45, 87.55],
            [21.05, 87.40]
        ],
        "penalty_weight": 1000.0,
        "hard_block": True,
        "reason": "Missile tracking and experimental sea impact sector."
    }
]

# ── 3. Marine Protected Areas (MPAs) (Polygons) ──────────────────────────────
MARINE_PROTECTED_AREAS = [
    {
        "id": "MPA_GULF_OF_MANNAR",
        "name": "Gulf of Mannar Marine National Park",
        "state": "Tamil Nadu",
        "category": "BIOSPHERE_RESERVE",
        "polygon": [
            [8.80, 78.10],
            [9.30, 78.80],
            [9.45, 79.30],
            [9.15, 79.40],
            [8.65, 78.30]
        ],
        "penalty_weight": 400.0,
        "hard_block": False,
        "restricted_commercial_fishing": True,
        "reason": "Protected coral reefs, sea cow (Dugong dugon) habitat, and pearl oyster banks."
    },
    {
        "id": "MPA_MALVAN_SANCTUARY",
        "name": "Malvan Marine Wildlife Sanctuary",
        "state": "Maharashtra (Sindhudurg)",
        "category": "MARINE_SANCTUARY",
        "polygon": [
            [15.95, 73.40],
            [16.12, 73.42],
            [16.12, 73.53],
            [15.95, 73.50]
        ],
        "penalty_weight": 350.0,
        "hard_block": False,
        "restricted_commercial_fishing": True,
        "reason": "Coral reef ecosystems, Sindhudurg fort submerged marine biodiversity zone."
    },
    {
        "id": "MPA_GAHIRMATHA",
        "name": "Gahirmatha Marine Wildlife Sanctuary",
        "state": "Odisha",
        "category": "TURTLE_CONSERVATION",
        "polygon": [
            [20.55, 86.85],
            [20.85, 87.05],
            [20.75, 87.35],
            [20.40, 87.10]
        ],
        "penalty_weight": 500.0,
        "hard_block": False,
        "restricted_commercial_fishing": True,
        "reason": "Mass nesting sanctuary for endangered Olive Ridley sea turtles (Arribada season)."
    },
    {
        "id": "MPA_GULF_OF_KUTCH",
        "name": "Marine National Park & Sanctuary (Gulf of Kutch)",
        "state": "Gujarat",
        "category": "CORAL_MANGROVE",
        "polygon": [
            [22.40, 69.20],
            [22.65, 69.40],
            [22.60, 69.85],
            [22.35, 69.70]
        ],
        "penalty_weight": 400.0,
        "hard_block": False,
        "restricted_commercial_fishing": True,
        "reason": "Intertidal coral reefs, 42 islands, and pristine mangrove estuary."
    }
]

# ── 4. Ecologically Sensitive Zones (ESZs) (Polygons) ─────────────────────────
ECOLOGICALLY_SENSITIVE_ZONES = [
    {
        "id": "ESZ_NETRANI_ISLAND",
        "name": "Netrani Island Coral Reef Conservation Zone",
        "state": "Karnataka (Murudeshwar)",
        "category": "CORAL_REEF",
        "polygon": [
            [13.98, 74.28],
            [14.05, 74.28],
            [14.05, 74.36],
            [13.98, 74.36]
        ],
        "penalty_weight": 300.0,
        "reason": "High biodiversity fringing coral reef with Whale Shark and Manta Ray aggregation."
    },
    {
        "id": "ESZ_GRANDE_ISLAND",
        "name": "Grande Island Coral & Dolphin Habitat",
        "state": "Goa (Mormugao)",
        "category": "CORAL_CETACEAN",
        "polygon": [
            [15.33, 73.74],
            [15.38, 73.74],
            [15.38, 73.80],
            [15.33, 73.80]
        ],
        "penalty_weight": 250.0,
        "reason": "Fringing patch reefs and Indo-Pacific humpback dolphin foraging corridor."
    },
    {
        "id": "ESZ_SUNDARBANS_BIOSPHERE",
        "name": "Sundarbans Marine Biosphere Buffer",
        "state": "West Bengal",
        "category": "MANGROVE_ESTUARY",
        "polygon": [
            [21.50, 88.30],
            [21.90, 88.30],
            [21.90, 89.10],
            [21.50, 89.10]
        ],
        "penalty_weight": 350.0,
        "reason": "UNESCO World Heritage mangrove delta and Estuarine Crocodile habitat."
    }
]

# ── 5. Standard Coastal Harbours & Landing Centers ───────────────────────────
COASTAL_PORTS_AND_HARBOURS = [
    {"name": "Mumbai Port (JNPT / Sassoon Dock)", "lat": 18.9667, "lon": 72.8333, "state": "Maharashtra"},
    {"name": "Ratnagiri (Mirkarwada Fishing Harbour)", "lat": 16.9902, "lon": 73.2980, "state": "Maharashtra"},
    {"name": "Mormugao Port (Goa)", "lat": 15.4989, "lon": 73.8278, "state": "Goa"},
    {"name": "New Mangalore Port / Malpe Harbour", "lat": 12.9242, "lon": 74.8190, "state": "Karnataka"},
    {"name": "Kochi Port / Thoppumpady Harbour", "lat": 9.9667, "lon": 76.2667, "state": "Kerala"},
    {"name": "Vizhinjam International Port", "lat": 8.3760, "lon": 76.9910, "state": "Kerala"},
    {"name": "Tuticorin (V.O. Chidambaranar Port)", "lat": 8.7642, "lon": 78.1348, "state": "Tamil Nadu"},
    {"name": "Chennai Port / Kasimedu Harbour", "lat": 13.0827, "lon": 80.2707, "state": "Tamil Nadu"},
    {"name": "Visakhapatnam Port", "lat": 17.6868, "lon": 83.2185, "state": "Andhra Pradesh"},
    {"name": "Paradip Port", "lat": 20.3165, "lon": 86.6114, "state": "Odisha"},
    {"name": "Kolkata / Haldia Port", "lat": 22.0257, "lon": 88.0583, "state": "West Bengal"},
    {"name": "Kandla Port (Deendayal Port)", "lat": 23.0033, "lon": 70.2189, "state": "Gujarat"},
    {"name": "Veraval Fishing Harbour", "lat": 20.9000, "lon": 70.3667, "state": "Gujarat"}
]
