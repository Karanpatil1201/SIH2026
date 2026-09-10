from app.agents.language_service import LanguageService

def test_language_detection_marathi():
    marathi_query = "उद्या समुद्रात जाणे सुरक्षित आहे का? मला शिफारस सांगा."
    lang = LanguageService.detect_language(marathi_query)
    assert lang == "mr"

def test_language_detection_hindi():
    hindi_query = "कल समुद्र में जाना सुरक्षित है क्या? मुझे रास्ता बताओ."
    lang = LanguageService.detect_language(hindi_query)
    assert lang == "hi"

def test_language_detection_tamil():
    tamil_query = "நாளை கடலுக்கு செல்வது பாதுகாப்பானதா?"
    lang = LanguageService.detect_language(tamil_query)
    assert lang == "ta"

def test_language_detection_telugu():
    telugu_query = "రేపు సముద్రంలోకి వెళ్లడం సురక్షితమేనా?"
    lang = LanguageService.detect_language(telugu_query)
    assert lang == "te"

def test_language_detection_kannada():
    kannada_query = "ನಾಳೆ ಸಮುದ್ರಕ್ಕೆ ಹೋಗುವುದು ಸುರಕ್ಷಿತವೇ?"
    lang = LanguageService.detect_language(kannada_query)
    assert lang == "kn"

def test_language_detection_malayalam():
    malayalam_query = "നാളെ കടലിൽ പോകുന്നത് സുരക്ഷിതമാണോ?"
    lang = LanguageService.detect_language(malayalam_query)
    assert lang == "ml"

def test_language_detection_bengali():
    bengali_query = "কাল সমুদ্রে যাওয়া কি নিরাপদ?"
    lang = LanguageService.detect_language(bengali_query)
    assert lang == "bn"

def test_language_detection_english():
    english_query = "Is it safe to go sailing tomorrow morning from Mumbai to Goa?"
    lang = LanguageService.detect_language(english_query)
    assert lang == "en"

def test_localized_response_generation():
    resp_mr = LanguageService.get_localized_response_template(
        lang="mr",
        risk_level="SAFE",
        risk_score=24.5,
        location_name="रत्नागिरी सागरी क्षेत्र",
        departure_rec="सकाळी ०८:३०",
        pfz_rec="PFZ Bravo",
        route_rec="Route B (सुरक्षित मार्ग)",
        key_reasons=["लाटांची उंची १.२ मीटर", "हवेचा वेग शांत"]
    )
    assert "वरुण" in resp_mr
    assert "सुरक्षित" in resp_mr
