"""
VARUNA Marine Knowledge RAG Engine — Retrieval-Augmented Generation with Gemini synthesis.
Retrieves relevant documents from the marine knowledge base and uses Gemini AI
to synthesize coherent, authoritative answers.
"""

from typing import List, Dict, Any
from app.models.schemas import RAGQueryResponse, RAGCitation

class MarineKnowledgeRAG:
    """
    Retrieval-Augmented Generation (RAG) system for marine documentation,
    INCOIS safety guidelines, cyclone protocols, and oceanographic literature.
    """

    KNOWLEDGE_BASE = [
        {
            "id": "DOC-INCOIS-01",
            "title": "INCOIS Marine Safety & High Wave Advisory Guidelines 2025",
            "category": "INCOIS",
            "content": "When significant wave heights exceed 3.5 meters along coastal zones, small fishing craft (<15m) are strictly prohibited from venturing into open sea. Port operations must evaluate tug boat assistance for vessels over 10,000 DWT."
        },
        {
            "id": "DOC-CYCLONE-02",
            "title": "NDMA Cyclone Disaster Preparedness Protocol for Maritime Ports",
            "category": "CYCLONE",
            "content": "Stage 3 Pre-Cyclone Alert (Yellow Message) requires all vessels anchored at roadstead to drop secondary anchors or move to deep sea anchorage at least 15 nautical miles offshore if central atmospheric pressure drops below 995 hPa."
        },
        {
            "id": "DOC-NAV-03",
            "title": "Indian Ocean Maritime Navigation Safety Standards & Route Risk Protocols",
            "category": "NAVIGATION",
            "content": "Sailing through Arabian Sea summer monsoon current shears requires adjusting engine RPM to compensate for 1.5-2.2 knot surface current drag. Vessels navigating from Mumbai to Goa should maintain a 12 nautical mile offshore margin."
        },
        {
            "id": "DOC-PFZ-04",
            "title": "Potential Fishing Zone (PFZ) Identification Methodology",
            "category": "RESEARCH",
            "content": "Potential Fishing Zones are identified at the intersection of Sea Surface Temperature (SST) thermal fronts and Chlorophyll-a concentration boundaries (>0.5 mg/m³). Fish aggregation occurs along these nutrient-rich oceanic fronts."
        },
        {
            "id": "DOC-VESSEL-05",
            "title": "DG Shipping Circular: Vessel Classification & Sea State Operating Limits",
            "category": "NAVIGATION",
            "content": "Artisanal fishing craft under 12 meters LOA are prohibited from operating when wave heights exceed 2.0 meters or wind speeds exceed 20 knots (37 km/h). Coastal vessels (12-25m) have a wave height limit of 3.0 meters. Commercial shipping (>25m) may operate up to sea state 6 (4.0-6.0m waves) with reduced speed protocols."
        },
        {
            "id": "DOC-SAR-06",
            "title": "Indian Coast Guard SAR (Search & Rescue) Maritime Protocols",
            "category": "SAFETY",
            "content": "All vessels operating beyond 12 nautical miles from the coastline must carry EPIRB (Emergency Position Indicating Radio Beacon) and maintain VHF Channel 16 watch. Distress calls must include vessel position, number of persons aboard, nature of distress, and type of assistance required."
        },
        {
            "id": "DOC-CORAL-07",
            "title": "MoEFCC Coral Reef Protection Guidelines for Indian Waters",
            "category": "ENVIRONMENT",
            "content": "Marine activities within 500 meters of designated coral reef zones (Gulf of Mannar, Lakshadweep, Andaman) are restricted when Degree Heating Weeks (DHW) exceed 4.0 °C-weeks. Anchoring is prohibited within coral reef buffer zones. Bleaching Alert Level 2 triggers mandatory vessel speed reduction to <5 knots within 2 nautical miles of reef systems."
        }
    ]

    @classmethod
    def query_knowledge(cls, question: str, top_k: int = 3) -> RAGQueryResponse:
        """
        Retrieve relevant documents and synthesize answer using Gemini AI.
        Falls back to concatenated excerpts if Gemini is unavailable.
        """
        # Lazy import to avoid circular dependency
        from app.services.gemini_service import gemini_service

        q_words = set(question.lower().split())
        scored_docs = []

        for doc in cls.KNOWLEDGE_BASE:
            text_words = set(doc["content"].lower().split() + doc["title"].lower().split())
            overlap = len(q_words.intersection(text_words))
            score = round(float(overlap / max(len(q_words), 1)), 2)

            # Boost score for domain-matched queries
            q_lower = question.lower()
            if "wave" in q_lower and doc["category"] == "INCOIS":
                score += 0.5
            if "cyclone" in q_lower and doc["category"] == "CYCLONE":
                score += 0.5
            if "route" in q_lower and doc["category"] == "NAVIGATION":
                score += 0.5
            if "fish" in q_lower and doc["category"] == "RESEARCH":
                score += 0.5
            if "vessel" in q_lower and doc["category"] == "NAVIGATION":
                score += 0.4
            if "coral" in q_lower and doc["category"] == "ENVIRONMENT":
                score += 0.5
            if "rescue" in q_lower and doc["category"] == "SAFETY":
                score += 0.5
            if any(kw in q_lower for kw in ["limit", "threshold", "prohibited", "restriction"]):
                score += 0.2  # Boost regulatory docs

            scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        top_matches = scored_docs[:top_k]

        citations: List[RAGCitation] = []
        retrieved_docs = []
        for s, doc in top_matches:
            citations.append(RAGCitation(
                document_title=doc["title"],
                category=doc["category"],
                snippet=doc["content"],
                relevance_score=min(0.98, max(0.65, s))
            ))
            retrieved_docs.append({
                "title": doc["title"],
                "category": doc["category"],
                "content": doc["content"]
            })

        # Use Gemini to synthesize a coherent answer from retrieved documents
        answer = gemini_service.generate_rag_response(
            question=question,
            retrieved_documents=retrieved_docs
        )

        return RAGQueryResponse(
            question=question,
            answer=answer,
            citations=citations
        )
