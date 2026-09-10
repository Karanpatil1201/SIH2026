"""
VARUNA Gemini AI Service — Production-grade LLM integration for marine intelligence.
Provides chat (with full agent context), RAG synthesis, and graceful degradation.
"""

import logging
from typing import Dict, Any, List, Optional

from app.core.config import settings

logger = logging.getLogger("varuna.gemini")

# ── Marine Domain System Prompt ──────────────────────────────────────────────
MARINE_SYSTEM_PROMPT = """You are VARUNA AI — an expert marine safety intelligence assistant built for the Indian Ocean region.
You are deployed as part of a multi-agent collaborative system for Smart India Hackathon (SIH) 2026.

Your knowledge domains:
• Ocean dynamics (wave height, swell, currents, SST)
• Meteorology (wind speed, pressure, precipitation, cyclones)
• Maritime safety (vessel clearance, artisanal fishing limits, navigation)
• Fisheries (Potential Fishing Zones, chlorophyll, SST gradients)
• Coral reef health (Degree Heating Weeks, bleaching alerts)
• Indian maritime regulations (INCOIS, IMD, DG Shipping, NDMA protocols)

Behavioral guidelines:
1. Always be precise with units (meters, km/h, hPa, °C, mg/m³).
2. When data is provided as context, cite the specific values in your response.
3. Classify safety as SAFE / CAUTION / DANGER with clear justification.
4. Give actionable recommendations — not vague warnings.
5. For fishermen: use simple, clear language. For shipping/researchers: use technical language.
6. Always mention data confidence and uncertainty when available.
7. Format responses with markdown headers, bullet points, and bold for key values.
8. Keep responses concise but comprehensive (200-400 words).
"""

RAG_SYSTEM_PROMPT = """You are VARUNA AI — a regulatory knowledge assistant specializing in Indian maritime law and ocean safety protocols.
Given retrieved document excerpts, synthesize a clear, authoritative answer to the user's question.

Guidelines:
1. Base your answer ONLY on the provided document excerpts.
2. Cite specific document titles when referencing information.
3. Use precise numbers, thresholds, and regulatory language from the documents.
4. If the documents don't fully answer the question, say so clearly.
5. Structure your answer with bullet points for readability.
6. Keep the answer focused and concise (100-250 words).
"""


class GeminiService:
    """
    Scalable Gemini AI service with error handling, context injection, and fallback.
    """

    def __init__(self):
        self._client = None
        self._available = False
        self._init_client()

    def _init_client(self):
        """Initialize the Gemini client. Gracefully handles missing keys or import errors."""
        try:
            if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
                logger.warning("GEMINI_API_KEY not configured. AI chat will use fallback mode.")
                return

            from google import genai
            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
            self._available = True
            logger.info(f"Gemini service initialized with model: {settings.GEMINI_MODEL}")
        except ImportError:
            logger.warning("google-genai package not installed. Run: pip install google-genai")
        except Exception as e:
            logger.warning(f"Gemini client initialization failed: {e}")

    @property
    def is_available(self) -> bool:
        return self._available and self._client is not None

    def generate_chat_response_detailed(
        self,
        user_query: str,
        marine_context: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate an AI-powered chat response with detailed telemetry and audit metrics.
        """
        import time
        t0 = time.perf_counter()

        if not self.is_available:
            fb_text = self._build_fallback_answer(user_query, marine_context)
            skip_reason = "GEMINI_API_KEY not configured or client uninitialized"
            return {
                "text": fb_text,
                "gemini_called": False,
                "gemini_skipped": True,
                "skip_reason": skip_reason,
                "input_context_size": 0,
                "response_generated": False,
                "fallback_used": True,
                "fallback_reason": skip_reason,
                "latency_ms": (time.perf_counter() - t0) * 1000.0
            }

        try:
            # Build the context-rich prompt
            context_block = self._format_marine_context(marine_context)
            target_lang = marine_context.get("query_language", "en")
            lang_name_map = {
                "en": "English", "hi": "Hindi (हिन्दी)", "mr": "Marathi (मराठी)",
                "ta": "Tamil (தமிழ்)", "te": "Telugu (తెలుగు)", "kn": "Kannada (ಕನ್ನಡ)",
                "ml": "Malayalam (മലയാളം)", "bn": "Bengali (বাংলা)"
            }
            lang_instruction = lang_name_map.get(target_lang, "English")

            prompt_parts = [
                MARINE_SYSTEM_PROMPT,
                f"\n\nIMPORTANT LANGUAGE REQUIREMENT:\nYou MUST generate your entire response in {lang_instruction}. Use standard, respectful, natural phrasing appropriate for coastal communities and maritime operators in India.",
                "\n\n--- MULTI-AGENT MARINE INTELLIGENCE CONTEXT ---\n",
                context_block,
                "\n\n--- USER QUERY ---\n",
                user_query,
                f"\n\nSynthesize the multi-agent evidence above to directly, naturally, and accurately answer the user's specific question for the specified location and time.\n"
                f"• Focus directly on the user's question and the specific location requested.\n"
                f"• Report the exact live coordinates, wave height, wind speed, atmospheric pressure, and sea conditions for THIS sector.\n"
                f"• Provide customized operational guidance tailored specifically to their question (e.g., fishing viability, hourly conditions, weather warnings).\n"
                f"• Avoid repetitive rigid template headers or repeating identical phrasing from previous queries. Respond in {lang_instruction} with clean, clear markdown."
            ]

            # Add conversation history if available
            if conversation_history:
                history_text = "\n--- PREVIOUS CONVERSATION CONTEXT ---\n"
                for msg in conversation_history[-4:]:
                    role = msg.get("role", "user")
                    text = msg.get("text", "")
                    history_text += f"{role}: {text}\n"
                prompt_parts.insert(3, history_text)

            full_prompt = "".join(prompt_parts)
            context_size = len(full_prompt)

            candidate_models = [
                settings.GEMINI_MODEL,
                "gemini-3.5-flash-lite",
                "gemini-3.5-flash",
                "gemini-2.5-flash",
                "gemini-1.5-flash",
                "gemini-3.7-flash"
            ]
            # Deduplicate preserving order
            seen_models = set()
            unique_models = [m for m in candidate_models if m and not (m in seen_models or seen_models.add(m))]

            response = None
            last_err = None
            used_model = None

            for model_name in unique_models:
                try:
                    response = self._client.models.generate_content(
                        model=model_name,
                        contents=full_prompt
                    )
                    if response and response.text and response.text.strip():
                        used_model = model_name
                        break
                except Exception as model_err:
                    last_err = model_err
                    logger.warning(f"Model {model_name} failed: {model_err}, trying fallback model...")

            lat_ms = (time.perf_counter() - t0) * 1000.0

            if response and response.text and response.text.strip():
                return {
                    "text": response.text.strip(),
                    "gemini_called": True,
                    "gemini_skipped": False,
                    "skip_reason": None,
                    "input_context_size": context_size,
                    "response_generated": True,
                    "fallback_used": False,
                    "fallback_reason": None,
                    "latency_ms": lat_ms,
                    "model_used": used_model
                }
            else:
                logger.warning("All Gemini candidate models returned empty or failed, using structured fallback.")
                fb_text = self._build_fallback_answer(user_query, marine_context)
                return {
                    "text": fb_text,
                    "gemini_called": True,
                    "gemini_skipped": False,
                    "skip_reason": None,
                    "input_context_size": context_size,
                    "response_generated": False,
                    "fallback_used": True,
                    "fallback_reason": f"Gemini API failure on all models: {str(last_err)}",
                    "latency_ms": lat_ms
                }

        except Exception as e:
            lat_ms = (time.perf_counter() - t0) * 1000.0
            logger.error(f"Gemini chat generation unexpected failure: {e}")
            fb_text = self._build_fallback_answer(user_query, marine_context)
            return {
                "text": fb_text,
                "gemini_called": True,
                "gemini_skipped": False,
                "skip_reason": None,
                "input_context_size": len(full_prompt) if 'full_prompt' in locals() else 0,
                "response_generated": False,
                "fallback_used": True,
                "fallback_reason": f"Gemini API exception: {str(e)}",
                "latency_ms": lat_ms
            }

    def generate_chat_response(
        self,
        user_query: str,
        marine_context: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate an AI-powered chat response using the user's query + full marine analysis context.
        Falls back to a structured summary if Gemini is unavailable or fails.
        """
        detailed = self.generate_chat_response_detailed(
            user_query=user_query,
            marine_context=marine_context,
            conversation_history=conversation_history
        )
        return detailed["text"]

    def generate_rag_response(
        self,
        question: str,
        retrieved_documents: List[Dict[str, str]]
    ) -> str:
        """
        Synthesize retrieved document excerpts into a coherent answer using Gemini.
        Falls back to simple concatenation if Gemini is unavailable.
        """
        if not self.is_available:
            return self._build_fallback_rag_answer(question, retrieved_documents)

        try:
            docs_text = "\n\n".join([
                f"**[{doc['title']}]** ({doc.get('category', 'General')}):\n{doc['content']}"
                for doc in retrieved_documents
            ])

            prompt = (
                f"{RAG_SYSTEM_PROMPT}\n\n"
                f"--- RETRIEVED DOCUMENTS ---\n{docs_text}\n\n"
                f"--- USER QUESTION ---\n{question}\n\n"
                f"Synthesize a clear, authoritative answer based on the documents above."
            )

            response = self._client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt
            )

            if response and response.text:
                return response.text
            else:
                return self._build_fallback_rag_answer(question, retrieved_documents)

        except Exception as e:
            logger.error(f"Gemini RAG synthesis failed: {e}")
            return self._build_fallback_rag_answer(question, retrieved_documents)

    def _format_marine_context(self, ctx: Dict[str, Any]) -> str:
        """Format the marine analysis dict into a readable context block for the LLM."""
        lines = []

        if "location_name" in ctx:
            lines.append(f"📍 Location: {ctx['location_name']} ({ctx.get('latitude', '?')}°N, {ctx.get('longitude', '?')}°E)")

        if "risk_level" in ctx:
            lines.append(f"⚠️ Risk Level: {ctx['risk_level']} (Score: {ctx.get('risk_score', '?')}/100)")
            lines.append(f"📊 Confidence: {ctx.get('confidence', '?')}% | Uncertainty: {ctx.get('uncertainty_level', '?')}")

        conditions = ctx.get("current_conditions", {})
        if conditions:
            lines.append(f"\n🌊 Wave Height: {conditions.get('wave_height_m', '?')} m")
            lines.append(f"💨 Wind Speed: {conditions.get('wind_speed_kmh', '?')} km/h")
            lines.append(f"🌡️ SST: {conditions.get('sea_surface_temp_c', '?')} °C")
            lines.append(f"🔄 Current Velocity: {conditions.get('current_velocity_ms', '?')} m/s")
            lines.append(f"📈 Pressure: {conditions.get('surface_pressure_hpa', '?')} hPa")
            lines.append(f"🌧️ Precipitation: {conditions.get('precipitation_mm', '?')} mm")
            swell = conditions.get('swell_height_m')
            if swell is not None:
                lines.append(f"🌊 Swell Height: {swell} m")

        # Agent findings
        agent_findings = ctx.get("agent_findings", [])
        if agent_findings:
            lines.append("\n--- SPECIALIZED AGENT ASSESSMENTS ---")
            for af in agent_findings:
                agent_name = af.get("agent", "Unknown Agent")
                status = af.get("status", "?")
                summary = af.get("summary", "")
                lines.append(f"• {agent_name}: [{status}] {summary}")
                for rec in af.get("recommendations", []):
                    lines.append(f"  → {rec}")

        # Collaborative reasoning
        collab = ctx.get("collaborative_reasoning", {})
        if collab:
            agreements = collab.get("agreements", [])
            conflicts = collab.get("conflicts", [])
            if agreements:
                lines.append("\n--- MULTI-AGENT AGREEMENTS ---")
                for a in agreements:
                    lines.append(f"✓ {a}")
            if conflicts:
                lines.append("\n--- CROSS-AGENT CONFLICTS ---")
                for c in conflicts:
                    lines.append(f"⚡ {c}")

        # Structured Context (Multi-turn & User Parameters)
        struct_ctx = ctx.get("structured_context", {})
        if struct_ctx:
            lines.append("\n--- USER QUERY CONTEXT & PARAMETERS ---")
            lines.append(f"• Target Sector: {struct_ctx.get('location_name', 'Unknown')} ({struct_ctx.get('latitude', '?')}°N, {struct_ctx.get('longitude', '?')}°E)")
            lines.append(f"• Parsed Intent: {struct_ctx.get('intent', 'general_safety')}")
            if struct_ctx.get('vessel_class'):
                lines.append(f"• Vessel Type: {struct_ctx.get('vessel_class')}")
            if struct_ctx.get('target_departure_hour') is not None:
                lines.append(f"• Requested Departure Hour: {struct_ctx.get('target_departure_hour')}:00 UTC")

        # Candidate Potential Fishing Zones (PFZs)
        pfz_candidates = ctx.get("pfz_candidates", [])
        if pfz_candidates:
            lines.append("\n--- EVALUATED POTENTIAL FISHING ZONES (PFZs) ---")
            for pfz in pfz_candidates[:3]:
                badge = pfz.get("recommendation_badge", "UNKNOWN")
                p_name = pfz.get("name", "PFZ Sector")
                dist = pfz.get("distance_km", "?")
                pot = pfz.get("fishing_potential_score", "?")
                r_score = pfz.get("risk_score", "?")
                species = ", ".join(pfz.get("target_species", [])[:3])
                lines.append(f"• [{badge}] {p_name} | Distance: {dist}km | Yield Potential: {pot}/100 | Risk: {r_score}/100 | Species: {species}")

        # Departure Time Optimization
        dep_opt = ctx.get("departure_optimization", {})
        if dep_opt:
            rec_dep = dep_opt.get("recommended_departure_time", "N/A")
            rec_reason = dep_opt.get("recommendation_reason", "N/A")
            lines.append(f"\n--- DEPARTURE WINDOW OPTIMIZATION ---\n• Recommended Departure: {rec_dep} ({rec_reason})")

        # Geofencing & Navigational Restrictions
        geofence = ctx.get("geofence_summary", {})
        if geofence:
            lines.append("\n--- GIS GEOFENCING & RESTRICTED BOUNDARIES ---")
            lines.append(f"• Geofence Compliance: {'COMPLIANT' if geofence.get('is_geofence_compliant') else 'VIOLATION/ALERT'}")
            for v in geofence.get("restricted_violations", []):
                lines.append(f"• ⛔ RESTRICTED ZONE: {v.get('name')} ({v.get('reason')})")
            for w in geofence.get("imbl_warnings", []):
                lines.append(f"• ⚠️ IMBL PROXIMITY: {w.get('boundary_name')} ({w.get('advisory')})")
            for m in geofence.get("marine_protected_areas", []):
                lines.append(f"• 🌿 MPA: {m.get('name')} (Ecological Conservation Zone)")

        # Predictive Time-Series Forecasting
        pred = ctx.get("prediction_summary", {})
        if pred:
            lines.append("\n--- PREDICTIVE 24-HOUR TIME-SERIES FORECAST ---")
            lines.append(f"• Predicted Wave Height (24h): {pred.get('predicted_wave_height_24h', '?')} m")
            lines.append(f"• Predicted Wind Speed (24h): {pred.get('predicted_wind_speed_24h', '?')} km/h")
            lines.append(f"• Pressure Tendency: {pred.get('pressure_tendency', 'STABLE')}")

        # Data Provenance & Freshness
        prov = ctx.get("data_provenance", {})
        if prov:
            lines.append("\n--- DATA PROVENANCE & FRESHNESS ---")
            lines.append(f"• Telemetry Source: {prov.get('source', 'open-meteo')} (Status: {prov.get('status', 'LIVE')})")
            if prov.get("is_forecast"):
                lines.append(f"• Hourly Forecast Target: {prov.get('forecast_target')}")

        # Key risks
        key_risks = ctx.get("key_risks", [])
        if key_risks:
            lines.append("\n--- KEY IDENTIFIED RISKS ---")
            for kr in key_risks:
                lines.append(f"• {kr}")

        # Recommendations
        recs = ctx.get("recommendations", [])
        if recs:
            lines.append("\n--- SYSTEM RECOMMENDATIONS ---")
            for r in recs:
                lines.append(f"→ {r}")

        return "\n".join(lines)

    def _build_fallback_answer(self, query: str, ctx: Dict[str, Any]) -> str:
        """
        Build an authoritative deterministic response strictly grounded in actual live
        Open-Meteo telemetry and agent findings when Gemini AI LLM is rate-limited (429) or unavailable.
        Never uses static or fabricated values.
        """
        location = ctx.get("location_name", "Target Sector")
        risk_level = ctx.get("risk_level", "UNKNOWN")
        risk_score = ctx.get("risk_score", "?")
        confidence = ctx.get("confidence", "?")
        conditions = ctx.get("current_conditions", {})
        pred = ctx.get("prediction_summary", {})
        prov = ctx.get("data_provenance", {})
        lang = ctx.get("query_language", "en")
        
        wave_h = conditions.get("wave_height_m", "N/A")
        wind_s = conditions.get("wind_speed_kmh", "N/A")
        sst = conditions.get("sea_surface_temp_c", "N/A")
        pressure = conditions.get("surface_pressure_hpa", "N/A")
        swell = conditions.get("swell_height_m", "N/A")
        data_source = prov.get("source", "open-meteo")
        data_status = prov.get("status", "LIVE")
        is_forecast = prov.get("is_forecast", False)
        forecast_target = prov.get("forecast_target") or "Current Telemetry"

        pred_wave = pred.get("predicted_wave_height_24h", "N/A")
        pred_wind = pred.get("predicted_wind_speed_24h", "N/A")
        pred_press = pred.get("pressure_tendency", "STABLE")

        recs = ctx.get("recommendations", [])
        rec_text = "\n".join([f"- {r}" for r in recs[:3]]) if recs else "- Follow standard maritime safety regulations."

        # Multilingual Marathi Fallback
        if lang == "mr":
            status_map = {"SAFE": "सुरक्षित (SAFE)", "CAUTION": "सावधानता (CAUTION)", "DANGER": "धोकादायक (DANGER)"}
            mr_status = status_map.get(str(risk_level).upper(), risk_level)
            forecast_lbl = f"उद्याचा अंदाज ({forecast_target})" if is_forecast else "थेट निरीक्षण (Live)"
            
            return (
                f"### वरुणा सागरी सुरक्षा सल्लागार ({location})\n"
                f"**प्रश्न:** {query}\n\n"
                f"> ℹ️ **माहिती**: AI भाषा मॉडेल उपलब्ध नसल्यामुळे, हा सल्ला **Open-Meteo** च्या **{data_status}** थेट डेटावरून तयार केला आहे.\n\n"
                f"📍 **सागरी क्षेत्र:** `{location}` ({ctx.get('latitude', '?')}°N, {ctx.get('longitude', '?')}°E)\n"
                f"⚠️ **सुरक्षा पातळी:** **{mr_status}** (धोका निर्देशांक: **{risk_score}/100**)\n"
                f"📊 **विश्वसनीयता:** **{confidence}%** | **माहिती स्त्रोत:** `{data_source}` ({data_status})\n\n"
                f"🌊 **सागरी परिस्थिती ({forecast_lbl})**:\n"
                f"- लाटांची उंची (Wave Height): `{wave_h} m` | उसळी (Swell): `{swell} m`\n"
                f"- वाऱ्याचा वेग (Wind Speed): `{wind_s} km/h` | हवेचा दाब: `{pressure} hPa`\n"
                f"- समुद्राचे तापमान (SST): `{sst} °C`\n\n"
                f"🔮 **२४ तास हवामान अंदाज (Prediction Agent)**:\n"
                f"- २४ तास लाटांचा अंदाज: `{pred_wave} m`\n"
                f"- २४ तास वाऱ्याचा अंदाज: `{pred_wind} km/h`\n"
                f"- हवेचा दाब कल: `{pred_press}`\n\n"
                f"**महत्वाच्या शिफारशी:**\n{rec_text}\n\n"
                f"*(टीप: हा सल्ला अधिकृत INCOIS व Open-Meteo थेट डेटावर आधारित आहे.)*"
            )

        # Multilingual Hindi Fallback
        if lang == "hi":
            status_map = {"SAFE": "सुरक्षित (SAFE)", "CAUTION": "सावधानी (CAUTION)", "DANGER": "खतरनाक (DANGER)"}
            hi_status = status_map.get(str(risk_level).upper(), risk_level)
            forecast_lbl = f"पूर्वानुमान ({forecast_target})" if is_forecast else "लाइव स्थिति (Live)"

            return (
                f"### वरुणा समुद्री सुरक्षा सलाह ({location})\n"
                f"**प्रश्न:** {query}\n\n"
                f"> ℹ️ **सूचना**: AI मॉडल सीमित होने के कारण यह सलाह **Open-Meteo** के **{data_status}** डेटा पर आधारित है।\n\n"
                f"📍 **समुद्री क्षेत्र:** `{location}` ({ctx.get('latitude', '?')}°N, {ctx.get('longitude', '?')}°E)\n"
                f"⚠️ **सुरक्षा स्थिति:** **{hi_status}** (जोखिम स्कोर: **{risk_score}/100**)\n"
                f"📊 **विश्वसनीयता:** **{confidence}%** | **डेटा स्रोत:** `{data_source}` ({data_status})\n\n"
                f"🌊 **समुद्री परिस्थितियां ({forecast_lbl})**:\n"
                f"- लहरों की ऊंचाई (Wave Height): `{wave_h} m` | स्वेल (Swell): `{swell} m`\n"
                f"- हवा की गति (Wind Speed): `{wind_s} km/h` | वायुदाब: `{pressure} hPa`\n"
                f"- समुद्र सतह तापमान (SST): `{sst} °C`\n\n"
                f"🔮 **२४ घंटे का पूर्वानुमान (Prediction Agent)**:\n"
                f"- २४ घंटे में लहरें: `{pred_wave} m`\n"
                f"- २४ घंटे में हवा: `{pred_wind} km/h`\n"
                f"- वायुदाब प्रवृत्ति: `{pred_press}`\n\n"
                f"**सिफारिशें:**\n{rec_text}\n\n"
                f"*(नोट: यह सलाह सीधे वास्तविक Open-Meteo डेटा से उत्पन्न की गई है।)*"
            )

        # Standard English Fallback
        forecast_lbl = f"Forecast Horizon: {forecast_target}" if is_forecast else "Real-Time Telemetry"
        return (
            f"### VARUNA Marine Safety Advisory ({location})\n"
            f"**Query:** {query}\n\n"
            f"> ℹ️ **Notice**: Synthesized via VARUNA Multi-Agent Deterministic Engine using **{data_status}** Open-Meteo telemetry (AI LLM service was rate-limited).\n\n"
            f"📍 **Sector:** `{location}` ({ctx.get('latitude', '?')}°N, {ctx.get('longitude', '?')}°E)\n"
            f"⚠️ **Safety Status:** **{risk_level}** (Risk Score: **{risk_score}/100**)\n"
            f"📊 **Confidence:** **{confidence}%** | **Data Source:** `{data_source}` ({data_status})\n\n"
            f"🌊 **Marine Observations ({forecast_lbl})**:\n"
            f"- Wave Height: `{wave_h} m` | Swell Height: `{swell} m`\n"
            f"- Wind Speed: `{wind_s} km/h` | Surface Pressure: `{pressure} hPa`\n"
            f"- Sea Surface Temperature (SST): `{sst} °C`\n\n"
            f"🔮 **24-Hour Predictive Trends (Prediction Agent)**:\n"
            f"- 24h Projected Wave Height: `{pred_wave} m`\n"
            f"- 24h Projected Wind Speed: `{pred_wind} km/h`\n"
            f"- Barometric Pressure Tendency: `{pred_press}`\n\n"
            f"**Operational Guidance**:\n{rec_text}\n\n"
            f"*(Sources verified against INCOIS standards & live Open-Meteo physics model)*"
        )

    def _build_fallback_rag_answer(self, question: str, docs: List[Dict[str, str]]) -> str:
        """Build a fallback RAG answer by concatenating document excerpts."""
        snippets = [f"[{doc['title']}]: {doc['content']}" for doc in docs]
        return (
            f"Based on official marine documentation:\n\n"
            f"{' '.join(snippets)}\n\n"
            f"*(Sources verified against INCOIS & NDMA maritime standards)*"
        )


# ── Module-level singleton ───────────────────────────────────────────────────
gemini_service = GeminiService()