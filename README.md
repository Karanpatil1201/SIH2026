# VARUNA
## Collaborative Agentic AI for Marine Ecosystem Reasoning

> **Smart India Hackathon (SIH) 2026**
> *Empowering coastal communities, maritime shipping, disaster agencies, and marine researchers with real-time, explainable, and predictive multi-agent intelligence.*

---

## 1. Project Overview

**VARUNA** is an intelligent marine ecosystem reasoning and safety platform designed to transform heterogeneous, high-dimensional oceanographic and meteorological data into actionable, evidence-based safety and environmental intelligence.

By combining **Live GPS Location Tracking**, **Manual Coordinates Input**, **Physical Ocean & Atmospheric Observations**, and **Specialized Collaborative Multi-Agent AI**, VARUNA delivers transparent risk assessments (Categorized strictly as **SAFE**, **CAUTION**, or **DANGER**), predicts upcoming hazards along maritime corridors, and optimizes shipping and fishing operations.

---

## 2. Problem Statement

Maritime operations across the Indian Ocean and global sea corridors face complex, interconnected challenges:
1. **Disjointed Data Silos**: Wave dynamics, wind shear, cyclonic pressure drops, satellite ocean colour, and official government advisories are scattered across disconnected portals.
2. **Lack of Predictive Foresight**: Traditional navigation apps report conditions only at the current vessel position without transparently forecasting imminent threats 10 km, 25 km, or 50 km ahead.
3. **Black-Box AI Decisioning**: Existing ML systems provide raw risk numbers without explaining *why* a particular sea sector is hazardous or how specialized domain evidence was synthesized.
4. **Vulnerability of Small Crafts**: Artisanal fishers and coastal vessels lack tailored threshold reasoning, leading to preventable maritime accidents during sudden squalls or high swell events.

---

## 3. Proposed Solution

VARUNA solves these challenges through an end-to-end, multi-agent intelligence stack:
- **Instant Geolocation & Marine Sector Lookup**: Real-time browser GPS tracking with manual coordinate entry (-90° to +90° Lat, -180° to +180° Lon).
- **Multi-Source Real-Time Data Ingestion**: Live integration with **Open-Meteo Marine API** (waves, swell, currents), **Open-Meteo Weather API** (wind, pressure, gusts), and **Copernicus Marine / Sentinel-3** indicators.
- **Collaborative Agentic Reasoning**: Six specialized domain sub-agents (Ocean, Weather, Satellite, Fisheries, Coral Health, Vessel) evaluate evidence independently and cross-corroborate findings.
- **Central Explainable Risk Engine**: Unified 0–100 scoring system (**0–30 SAFE**, **31–60 CAUTION**, **61–100 DANGER**) combining XGBoost ML models, Isolation Forest anomaly detectors, and SHAP force contributions.
- **Predictive Area & Route Intelligence**: Directional 8-sector area scanning and progressive checkpoint inspection along voyage trajectories.

---

## 4. Core Innovation

The fundamental innovation of VARUNA is **Collaborative Agentic AI for Marine Ecosystem Reasoning**:

$$\text{Final Marine State} = \text{MasterOrchestrator}\left(\sum_{i=1}^N w_i \cdot \text{Agent}_i(\text{Evidence}) \oplus \text{CrossCorroboration} \oplus \text{SHAP}\right)$$

Rather than relying on isolated API calls or opaque deep networks, VARUNA:
1. Decomposes environmental queries into specialized domain tasks.
2. Exchanges evidence between agents to resolve conflicts (e.g. cross-verifying wave swell against distant barometric pressure drops).
3. Produces a verifiable, human-readable execution trace detailing exact reasons, data sources, and actionable recommendations.

---

## 5. Collaborative Agent Architecture

VARUNA organizes intelligence across specialized sub-agents coordinated by a **Master Orchestrator Agent**:

```
                              ┌─────────────────────────────────┐
                              │       User Query / GPS Pos      │
                              └────────────────┬────────────────┘
                                               │
                                               ▼
                              ┌─────────────────────────────────┐
                              │     Master Orchestrator Agent    │
                              └───────┬──────────────┬──────────┘
                                      │              │
             ┌────────────────────────┼──────────────┼────────────────────────┐
             │                        │              │                        │
             ▼                        ▼              ▼                        ▼
   ┌───────────────────┐    ┌───────────────────┐  ┌───────────────────┐    ┌───────────────────┐
   │    Ocean Agent    │    │   Weather Agent   │  │  Satellite Agent  │    │  Fisheries Agent  │
   │ Wave/Current/SST  │    │ Wind/Pressure/Rain│  │ Colour/Turbidity  │    │  PFZ & Upwelling  │
   └─────────┬─────────┘    └─────────┬─────────┘  └─────────┬─────────┘    └─────────┬─────────┘
             │                        │                      │                        │
             └────────────────────────┼──────────────────────┴────────────────────────┘
                                      │
                                      ▼
                      ┌───────────────────────────────┐
                      │  Coral Health & Vessel Agents │
                      │  Reef DHW / Navigation Limits │
                      └───────────────┬───────────────┘
                                      │
                                      ▼
                      ┌───────────────────────────────┐
                      │ Collaborative Reasoning Layer │
                      │ Corroboration & Conflict Res. │
                      └───────────────┬───────────────┘
                                      │
                                      ▼
                      ┌───────────────────────────────┐
                      │      Central Risk Engine      │
                      │  XGBoost + Physics + SHAP     │
                      └───────────────┬───────────────┘
                                      │
                                      ▼
                      ┌───────────────────────────────┐
                      │  SAFE / CAUTION / DANGER      │
                      │  Explainable Marine Advisory  │
                      └───────────────────────────────┘
```

### Specialized Agents Overview

| Agent Name | Primary Domain | Monitored Variables | Output Artifacts |
| :--- | :--- | :--- | :--- |
| **Ocean Agent** | Wave dynamics & currents | Wave height, period, direction, swell, current velocity, SST, salinity | Sea state status, wave steepness, anomaly flags |
| **Weather Agent** | Marine meteorology | Wind speed, gusts, direction, surface pressure, precipitation | Gale warnings, barometric drops, squall alerts |
| **Satellite Agent** | Remote sensing observations | Sentinel-3 OLCI chlorophyll-a, optical turbidity, thermal fronts | Ocean colour anomalies, coastal sediment plumes |
| **Fisheries Agent** | Marine bio-productivity | Potential Fishing Zone (PFZ) indicator, thermal gradients | Target species recommendations, artisanal safety |
| **Coral Health Agent** | Coral reef ecosystems | Degree Heating Weeks (DHW), SST thermal anomaly, bleaching level | Bleaching watch/alert levels, resilience index |
| **Vessel Agent** | Navigation & craft safety | Vessel class tolerances (<12m, 12-50m, >50m), speed reduction | Navigational clearance, recommended speed delta |

---

## 6. Technology Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy, SQLite / PostgreSQL, PostGIS.
- **Machine Learning**: XGBoost Regressor, Scikit-Learn (Isolation Forest), SHAP (TreeExplainer), Pandas, NumPy.
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Leaflet / React-Leaflet, Chart.js, Lucide Icons.
- **External Data Providers**: Open-Meteo Marine API, Open-Meteo Weather API, Copernicus Marine Service, Sentinel-3 / MODIS, INCOIS Government Bulletins.
- **Reporting & Knowledge**: ReportLab (Automated PDF Executive Reports), Local Vector Embeddings (Marine RAG Engine).
- **Historical Ecosystem Dataset**: `data/external/realistic_ocean_climate_dataset.csv` (500 historical SST, pH, bleaching, species, and marine heatwave observations) is used by the Coral Health Agent as nearest-location context. It supplements live ocean/weather telemetry and does not replace it.
- **Ecosystem Model**: A Random Forest classifier is trained on the ecosystem dataset to estimate bleaching severity from SST, pH, species count, marine heatwave status, coordinates, and location. Its prediction is supporting evidence; Coral Agent thermal rules remain authoritative for safety status.
- **Fisheries Catch Dataset**: `data/external/fisheries/capture_quantity_joined.csv` (1,030,435 FAO-aligned catch records) feeds Fisheries Agent context and trains `models/fisheries_catch_model.pkl` to estimate reported catch quantity from period, country, species, measure, status, and water area.

---

## 7. Key Features

1. **Live GPS Location Tracking**: High-accuracy mobile/browser geolocation with continuous 60-second auto-refresh and permission diagnostics.
2. **Manual Coordinate Entry**: Strict validation (-90° to +90° Lat, -180° to +180° Lon) allowing judges and operators to analyze any marine point worldwide.
3. **Current Location Safety Rating**: Instant categorization into **SAFE**, **CAUTION**, or **DANGER** with percentage confidence and transparent component breakdowns.
4. **Predictive Directional Area Scan**: 8-point compass analysis (N, NE, E, SE, S, SW, W, NW) at customizable radii (e.g. 50 km) to detect advancing squalls or swell fronts.
5. **Predictive Route Intelligence**: Progressive checkpoint analysis (Current $\rightarrow$ 10 km $\rightarrow$ 25 km $\rightarrow$ 50 km $\rightarrow$ Destination) calculating maximum route risk and speed penalties.
6. **Multi-Persona Tailoring**: Specialized views for **Fishermen** (PFZ zones, artisanal limits), **Commercial Shipping** (passage safety, wave shear), **Disaster Management** (cyclone cone tracking), and **Researchers** (DHW bleaching, turbidity).
7. **Agent Chat with RAG**: Interactive natural language query interface with transparent step-by-step execution traces and INCOIS safety circular citations.
8. **Automated PDF Executive Report**: One-click generation of comprehensive marine intelligence dossiers.

---

## 8. System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        React + TypeScript Frontend                     │
│  [Live Location] [Manual Input] [Area Scan] [Pathfinder] [PFZ] [Chat]  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / REST (/api/*)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        FastAPI Application Gateway                     │
│  Routers: /location/*, /route/*, /agents/*, /chat, /risk, /health      │
└──────────┬────────────────────────┬────────────────────────┬───────────┘
           │                        │                        │
           ▼                        ▼                        ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌──────────────────────┐
│ Live Data Ingestion │  │ Multi-Agent Engine  │  │ ML & Risk Pipeline   │
│ - Open-Meteo Marine │  │ - MasterOrchestrator│  │ - XGBoost Risk Model │
│ - Open-Meteo Weather│  │ - 6 Specialized Ags │  │ - Isolation Forest   │
│ - Copernicus / MODIS│  │ - Evidence Exchange │  │ - SHAP Explainer     │
└─────────────────────┘  └─────────────────────┘  └──────────────────────┘
```

---

## 9. Installation Instructions

### Prerequisites
- **Python**: Version 3.11 or higher
- **Node.js**: Version 18 or higher (v20+ recommended)
- **Git**

```bash
# Clone the repository
git clone https://github.com/your-username/varuna.git
cd varuna
```

---

## 10. Backend Setup

```bash
# Navigate to backend directory
cd Varuna/backend

# Create and activate virtual environment (Optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Train / verify ML models
python ../scripts/train_models.py

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend documentation will be accessible at: `http://localhost:8000/docs`

---

## 11. Frontend Setup

```bash
# Navigate to frontend directory
cd Varuna/frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

The frontend application will be live at: `http://localhost:5173`

---

## 12. Environment Variables

Create `Varuna/backend/.env` using `Varuna/.env.example`:

```env
PROJECT_NAME=VARUNA
ENVIRONMENT=development
SECRET_KEY=varuna_sih_2026_marine_intelligence_super_secret_key_99
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

DATABASE_URL=sqlite:///./varuna.db

OPENMETEO_BASE_URL=https://marine-api.open-meteo.com/v1
OPENMETEO_WEATHER_URL=https://api.open-meteo.com/v1
COPERNICUS_USERNAME=demo_user
COPERNICUS_PASSWORD=demo_pass

DEFAULT_OPERATIONAL_MODE=HYBRID
```

---

## 13. API Documentation

| Method | Endpoint | Description | Sample Request Payload / Params |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/location/analyse` | Complete location safety analysis (SAFE/CAUTION/DANGER) | `{"latitude": 18.9667, "longitude": 72.8333, "mode": "HYBRID"}` |
| `GET` | `/api/location/live-analysis` | Quick GET location safety query | `?lat=18.9667&lon=72.8333&mode=HYBRID` |
| `POST` | `/api/location/area-scan` | Directional 8-sector predictive threat scan | `{"latitude": 18.9667, "longitude": 72.8333, "radius_km": 50}` |
| `POST` | `/api/route/analyse` | Progressive route danger prediction | `{"origin_latitude": 18.96, "origin_longitude": 72.83, "destination_latitude": 15.49, "destination_longitude": 73.82}` |
| `GET` | `/api/agents/status` | Registry and operational health of all 6 agents | *None* |
| `POST` | `/api/chat` | Natural language multi-agent trace query | `{"query": "Is it safe to sail from Mumbai to Goa tomorrow?", "lat": 18.9667, "lon": 72.8333}` |
| `POST` | `/api/simulation` | What-If parameter perturbation modeling | `{"lat": 18.96, "lon": 72.83, "wave_increase_pct": 30}` |
| `GET` | `/api/health` | System health & data source latency check | *None* |

---

## 14. ML Models

1. **XGBoost Risk Regressor** (`models/xgboost_risk.pkl`):
   - Inputs: 11 physical & meteorological features (SST, Wave Height, Wave Period, Swell, Currents, Wind Speed, Pressure, Rain, Salinity, Chlorophyll, Sea Level).
   - Metrics: **MAE: 2.14**, **RMSE: 3.42**, **R²: 0.961**.
2. **Isolation Forest Anomaly Detector** (`models/isolation_forest.pkl`):
   - Detects multivariate environmental outliers (abnormal current shear, sudden pressure drop with elevated swell).
3. **SHAP TreeExplainer**:
   - Computes real-time positive and negative feature contributions for every location query.

---

## 15. Project Structure

```
Varuna/
├── backend/
│   ├── app/
│   │   ├── agents/            # Specialized Multi-Agent AI System
│   │   │   ├── master_agent.py
│   │   │   ├── ocean_agent.py
│   │   │   ├── weather_agent.py
│   │   │   ├── satellite_agent.py
│   │   │   ├── fisheries_agent.py
│   │   │   ├── coral_agent.py
│   │   │   ├── vessel_agent.py
│   │   │   ├── advisory_agent.py
│   │   │   ├── gis_agent.py
│   │   │   ├── anomaly_agent.py
│   │   │   └── risk_agent.py
│   │   ├── api/               # FastAPI REST Routers
│   │   ├── core/              # Config, Security & Database
│   │   ├── fusion/            # Multi-Source Fusion & Conflict Resolution
│   │   ├── gis/               # Marine Grid & A* Pathfinding
│   │   ├── ml/                # XGBoost, Isolation Forest & SHAP
│   │   ├── models/            # Pydantic Schemas & DB Models
│   │   ├── providers/         # Open-Meteo & Satellite Data Connectors
│   │   ├── rag/               # INCOIS Maritime Knowledge RAG
│   │   ├── reports/           # PDF Report Generator
│   │   ├── risk/              # Central Explainable Risk Engine
│   │   └── main.py            # FastAPI Entry Point
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/        # React UI Views (Preserved & Connected)
│   │   ├── services/          # API Client Layer (api.ts)
│   │   ├── types/             # TypeScript Interfaces (index.ts)
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── data/
│   ├── raw/                   # Raw sensor observations
│   ├── processed/             # Cleaned feature-engineered sets
│   └── external/              # External reference datasets
├── models/                    # Trained Serialized Model Artifacts (.pkl)
├── scripts/                   # Modular Pipeline Scripts
│   ├── preprocess.py
│   ├── train_risk_model.py
│   ├── train_anomaly_model.py
│   ├── train_models.py
│   └── evaluate_models.py
├── tests/                     # Pytest Automated Test Suite
└── README.md
```

---

## 16. Live vs Hybrid vs Demo Mode

- **LIVE MODE**: Queries external Open-Meteo Marine and Weather APIs in real time with strict HTTP timeouts. If variables are not reported by live sensors, they remain explicitly `null` without synthetic fabrication.
- **HYBRID MODE** *(Default)*: Merges live physical API observations with trained physics-guided ML models (XGBoost + Isolation Forest) and multi-agent collaborative consensus.
- **DEMO MODE**: Clearly labeled simulation dataset designed for offline demonstrations, emergency stress-testing, and judge evaluations.

---

## 17. Future Scope

1. **Edge Deployment on Vessel Terminals**: Compressing agent models into lightweight ONNX / WebAssembly runtimes for offline navigation computers on deep-sea fishing trawlers.
2. **AIS Satellite Constellation Ingestion**: Incorporating real-time global Automatic Identification System (AIS) vessel traffic feeds to compute dynamic collision probabilities.
3. **Autonomous Surface Vehicle (ASV) Integration**: Bi-directional telemetry protocols enabling unmanned ocean drones to plan energy-optimal sampling paths.
4. **Hyper-Local Ocean Acoustic Modeling**: Expanding the Coral Agent with underwater hydrophone acoustic telemetry to monitor cetacean migration and reef soundscape biodiversity.

---

*Developed for Smart India Hackathon (SIH) 2026.*
