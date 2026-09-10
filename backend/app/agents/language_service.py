"""
VARUNA Multilingual Language Service
Supports automatic identification and localized marine responses for 8 Indian languages:
1. English (en)
2. Hindi (hi) - हिन्दी
3. Marathi (mr) - मराठी
4. Tamil (ta) - தமிழ்
5. Telugu (te) - తెలుగు
6. Kannada (kn) - ಕನ್ನಡ
7. Malayalam (ml) - മലയാളം
8. Bengali (bn) - বাংলা
"""

import re
from typing import Dict, Any, Tuple, Optional

class LanguageService:
    """
    Automatic language detection and localization engine for marine safety intelligence.
    """

    SUPPORTED_LANGUAGES = {
        "en": {"code": "en", "name": "English", "native": "English"},
        "hi": {"code": "hi", "name": "Hindi", "native": "हिन्दी"},
        "mr": {"code": "mr", "name": "Marathi", "native": "मराठी"},
        "ta": {"code": "ta", "name": "Tamil", "native": "தமிழ்"},
        "te": {"code": "te", "name": "Telugu", "native": "తెలుగు"},
        "kn": {"code": "kn", "name": "Kannada", "native": "ಕನ್ನಡ"},
        "ml": {"code": "ml", "name": "Malayalam", "native": "മലയാളം"},
        "bn": {"code": "bn", "name": "Bengali", "native": "বাংলা"}
    }

    # Distinctive Marathi lexical keywords
    MARATHI_KEYWORDS = {
        "उद्या", "आहे", "का", "नाही", "समुद्रात", "जाणे", "मासे", "मासेमारी", "लाटा",
        "हवामान", "वारा", "धोका", "मार्ग", "सांगा", "कसे", "केव्हा", "साठवण",
        "बोट", "नौका", "रत्नागिरी", "मुंबई", "बंदरावर", "सकाळी", "सायंकाळी", "मला"
    }

    # Distinctive Hindi lexical keywords
    HINDI_KEYWORDS = {
        "कल", "है", "क्या", "नहीं", "समुद्र", "जाना", "मछली", "मत्स्य", "लहरें",
        "मौसम", "हवा", "खतरा", "रास्ता", "बताओ", "कैसे", "कब",
        "नाव", "नाविक", "सुबह", "शाम", "में", "मुझे", "कृपया", "से", "तक"
    }

    @classmethod
    def detect_language(cls, text: str) -> str:
        """
        Automatically detects the language of input text using Unicode script blocks and lexical cues.
        """
        if not text or not text.strip():
            return "en"

        cleaned = text.strip()

        # Unicode Script Block Counts
        devanagari_count = len(re.findall(r'[\u0900-\u097F]', cleaned))
        tamil_count = len(re.findall(r'[\u0B80-\u0BFF]', cleaned))
        telugu_count = len(re.findall(r'[\u0C00-\u0C7F]', cleaned))
        kannada_count = len(re.findall(r'[\u0C80-\u0CFF]', cleaned))
        malayalam_count = len(re.findall(r'[\u0D00-\u0D7F]', cleaned))
        bengali_count = len(re.findall(r'[\u0980-\u09FF]', cleaned))

        script_counts = [
            (devanagari_count, "devanagari"),
            (tamil_count, "ta"),
            (telugu_count, "te"),
            (kannada_count, "kn"),
            (malayalam_count, "ml"),
            (bengali_count, "bn")
        ]
        max_count, dominant_script = max(script_counts, key=lambda x: x[0])

        if max_count >= 3:
            if dominant_script == "devanagari":
                # Disambiguate Marathi vs Hindi
                words = set(re.findall(r'[\u0900-\u097F]+', cleaned))
                mr_matches = len(words.intersection(cls.MARATHI_KEYWORDS))
                hi_matches = len(words.intersection(cls.HINDI_KEYWORDS))
                
                # Check for characteristic Marathi distinct characters (e.g. ळ, ऱ)
                has_mr_char = any(char in cleaned for char in ["ळ", "ऱ"])
                if has_mr_char and mr_matches >= hi_matches:
                    return "mr"
                if mr_matches > hi_matches:
                    return "mr"
                elif hi_matches > mr_matches:
                    return "hi"
                return "hi"  # Default devanagari to Hindi
            return dominant_script


        # Transliterated / Romanized heuristics using whole word regex
        t_lower = cleaned.lower()
        if re.search(r'\b(kya|hai|samundar|machhli|surakshit|mausam|tarike)\b', t_lower):
            return "hi"
        if re.search(r'\b(udya|aahe|samudrat|masemari|kiti|sangaa|kasa)\b', t_lower):
            return "mr"
        if re.search(r'\b(epdi|irukku|kadal|meen|pathukappu)\b', t_lower):
            return "ta"
        if re.search(r'\b(ela|undi|samudram|chepalu|surakshitam)\b', t_lower):
            return "te"

        return "en"

    @classmethod
    def get_localized_response_template(
        cls,
        lang: str,
        risk_level: str,
        risk_score: float,
        location_name: str,
        departure_rec: Optional[str] = None,
        pfz_rec: Optional[str] = None,
        route_rec: Optional[str] = None,
        key_reasons: Optional[list] = None
    ) -> str:
        """
        Generates structured, authoritative marine safety recommendations in the target language.
        """
        reasons_text = "\n".join([f"• {r}" for r in (key_reasons or [])])

        if lang == "mr":
            status_map = {"SAFE": "सुरक्षित (SAFE)", "CAUTION": "सावधानता (CAUTION)", "DANGER": "धोकादायक (DANGER)"}
            return (
                f"### 🌊 वरुण (VARUNA) सागरी सुरक्षा निर्णय अहवाल\n\n"
                f"**स्थान:** {location_name}\n"
                f"**सागरी स्थिती स्तर:** {status_map.get(risk_level, risk_level)} (जोखीम गुण: **{risk_score}/100**)\n\n"
                + (f"**शिफारस केलेली निघण्याची वेळ:** {departure_rec}\n" if departure_rec else "")
                + (f"**शिफारस केलेले मासेमारी क्षेत्र (PFZ):** {pfz_rec}\n" if pfz_rec else "")
                + (f"**सुरक्षित सागरी मार्ग:** {route_rec}\n" if route_rec else "")
                + f"\n**मुख्य कारणे आणि पुरावे:**\n{reasons_text}\n\n"
                f"*टीप: ही माहिती INCOIS, हवामान अंदाज आणि GIS भू-सीमा (Geofencing) विश्लेषणावर आधारित आहे.*"
            )

        elif lang == "hi":
            status_map = {"SAFE": "सुरक्षित (SAFE)", "CAUTION": "सतर्कता (CAUTION)", "DANGER": "खतरनाक (DANGER)"}
            return (
                f"### 🌊 वरुण (VARUNA) समुद्री सुरक्षा निर्णय रिपोर्ट\n\n"
                f"**स्थान:** {location_name}\n"
                f"**समुद्री जोखिम स्तर:** {status_map.get(risk_level, risk_level)} (जोखिम स्कोर: **{risk_score}/100**)\n\n"
                + (f"**अनुशंसित प्रस्थान समय:** {departure_rec}\n" if departure_rec else "")
                + (f"**अनुशंसित मत्स्य पालन क्षेत्र (PFZ):** {pfz_rec}\n" if pfz_rec else "")
                + (f"**सुरक्षित समुद्री मार्ग:** {route_rec}\n" if route_rec else "")
                + f"\n**प्रमुख कारण एवं साक्ष्य:**\n{reasons_text}\n\n"
                f"*नोट: यह जानकारी INCOIS, मौसम पूर्वानुमान और GIS भू-सीमा प्रतिबंधों पर आधारित है।*"
            )

        elif lang == "ta":
            status_map = {"SAFE": "பாதுகாப்பானது (SAFE)", "CAUTION": "எச்சரிக்கை (CAUTION)", "DANGER": "ஆபத்தானது (DANGER)"}
            return (
                f"### 🌊 வருணா (VARUNA) கடல்சார் பாதுகாப்பு அறிக்கை\n\n"
                f"**இடம்:** {location_name}\n"
                f"**கடல் பாதுகாப்பு நிலை:** {status_map.get(risk_level, risk_level)} (அபாய குறியீடு: **{risk_score}/100**)\n\n"
                + (f"**பரிந்துரைக்கப்பட்ட புறப்படும் நேரம்:** {departure_rec}\n" if departure_rec else "")
                + (f"**பரிந்துரைக்கப்பட்ட மீன்பிடி மண்டலம் (PFZ):** {pfz_rec}\n" if pfz_rec else "")
                + (f"**பாதுகாப்பான கடல் பாதை:** {route_rec}\n" if route_rec else "")
                + f"\n**முக்கிய காரணங்கள்:**\n{reasons_text}\n\n"
                f"*குறிப்பு: INCOIS மற்றும் GIS கடல் எல்லை தரவுகளின்படி கணக்கிடப்பட்டது.*"
            )

        elif lang == "te":
            status_map = {"SAFE": "సురక్షితం (SAFE)", "CAUTION": "జాగ్రత్త (CAUTION)", "DANGER": "ప్రమాదకరం (DANGER)"}
            return (
                f"### 🌊 వరుణ (VARUNA) సముద్ర భద్రతా నివేదిక\n\n"
                f"**ప్రాంతం:** {location_name}\n"
                f"**రిస్క్ స్థాయి:** {status_map.get(risk_level, risk_level)} (రిస్క్ స్కోరు: **{risk_score}/100**)\n\n"
                + (f"**సిఫార్సు చేయబడిన బయలుదేరే సమయం:** {departure_rec}\n" if departure_rec else "")
                + (f"**సిఫార్సు చేయబడిన చేపల వేట జోన్ (PFZ):** {pfz_rec}\n" if pfz_rec else "")
                + (f"**సురక్షిత సముద్ర మార్గం:** {route_rec}\n" if route_rec else "")
                + f"\n**ప్రధాన కారణాలు & ఆధారాలు:**\n{reasons_text}\n\n"
                f"*గమనిక: INCOIS మరియు GIS సముద్ర భౌగోళిక నిబంధనల ఆధారంగా.*"
            )

        elif lang == "kn":
            status_map = {"SAFE": "ಸುರಕ್ಷಿತ (SAFE)", "CAUTION": "ಎಚ್ಚರಿಕೆ (CAUTION)", "DANGER": "ಅಪಾಯಕಾರಿ (DANGER)"}
            return (
                f"### 🌊 ವರುಣ (VARUNA) ಸಾಗರ ಸುರಕ್ಷತಾ ವರದಿ\n\n"
                f"**ಸ್ಥಳ:** {location_name}\n"
                f"**ಅಪಾಯ ಮಟ್ಟ:** {status_map.get(risk_level, risk_level)} (ಅಂಕ: **{risk_score}/100**)\n\n"
                + (f"**ಶಿಫಾರಸು ಮಾಡಿದ ನಿರ್ಗಮನ ಸಮಯ:** {departure_rec}\n" if departure_rec else "")
                + (f"**ಶಿಫಾರಸು ಮಾಡಿದ ಮೀನುಗಾರಿಕೆ ವಲಯ (PFZ):** {pfz_rec}\n" if pfz_rec else "")
                + (f"**ಸುರಕ್ಷಿತ ಸಾಗರ ಮಾರ್ಗ:** {route_rec}\n" if route_rec else "")
                + f"\n**ಮುಖ್ಯ ಕಾರಣಗಳು:**\n{reasons_text}\n\n"
                f"*ಸೂಚನೆ: INCOIS ಮತ್ತು ಸಾಗರ ಜಿಐಎಸ್ ಡೇಟಾ ಆಧರಿಸಿದೆ.*"
            )

        elif lang == "ml":
            status_map = {"SAFE": "സുരക്ഷിതം (SAFE)", "CAUTION": "ജാഗ്രത (CAUTION)", "DANGER": "അപകടകരം (DANGER)"}
            return (
                f"### 🌊 വരുണ (VARUNA) സമുദ്ര സുരക്ഷാ റിപ്പോർട്ട്\n\n"
                f"**സ്ഥലം:** {location_name}\n"
                f"**അപകടസാധ്യത:** {status_map.get(risk_level, risk_level)} (സ്കോർ: **{risk_score}/100**)\n\n"
                + (f"**ശുപാർശ ചെയ്യുന്ന പുറപ്പെടൽ സമയം:** {departure_rec}\n" if departure_rec else "")
                + (f"**മത്സ്യബന്ധന മേഖല (PFZ):** {pfz_rec}\n" if pfz_rec else "")
                + (f"**സുരക്ഷിത പാത:** {route_rec}\n" if route_rec else "")
                + f"\n**പ്രധാന കണ്ടെത്തലുകൾ:**\n{reasons_text}\n\n"
                f"*ശ്രദ്ധിക്കുക: INCOIS, GIS വിവരങ്ങളുടെ അടിസ്ഥാനത്തിൽ തയാറാക്കിയത്.*"
            )

        elif lang == "bn":
            status_map = {"SAFE": "নিরাপদ (SAFE)", "CAUTION": "সতর্কতা (CAUTION)", "DANGER": "বিপজ্জনক (DANGER)"}
            return (
                f"### 🌊 বরুণা (VARUNA) সামুদ্রিক নিরাপত্তা প্রতিবেদন\n\n"
                f"**অবস্থান:** {location_name}\n"
                f"**ঝুঁকির মাত্রা:** {status_map.get(risk_level, risk_level)} (স্কোর: **{risk_score}/100**)\n\n"
                + (f"**সুপারিশকৃত যাত্রার সময়:** {departure_rec}\n" if departure_rec else "")
                + (f"**অনুকূল মৎস্য অঞ্চল (PFZ):** {pfz_rec}\n" if pfz_rec else "")
                + (f"**নিরাপদ সমুদ্র পথ:** {route_rec}\n" if route_rec else "")
                + f"\n**প্রধান কারণ ও প্রমাণ:**\n{reasons_text}\n\n"
                f"*দ্রষ্টব্য: INCOIS এবং GIS সামুদ্রিক ডেটার ওপর ভিত্তি করে গণনা করা হয়েছে।*"
            )

        # Default English
        return (
            f"### 🌊 VARUNA Marine Safety Decision Intelligence\n\n"
            f"**Sector:** {location_name}\n"
            f"**Marine Safety Classification:** **{risk_level}** (Risk Score: **{risk_score}/100**)\n\n"
            + (f"**Recommended Departure Window:** {departure_rec}\n" if departure_rec else "")
            + (f"**Recommended Fishing Zone (PFZ):** {pfz_rec}\n" if pfz_rec else "")
            + (f"**Safe Navigation Corridor:** {route_rec}\n" if route_rec else "")
            + f"\n**Key Decision Evidence & Risk Factors:**\n{reasons_text}\n\n"
            f"*Evidence Grounding: Real-time Open-Meteo ocean physics, Copernicus satellite indicators, INCOIS circulars, and GIS geofence verification.*"
        )
