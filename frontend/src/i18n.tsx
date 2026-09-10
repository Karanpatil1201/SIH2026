import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

export type LanguageCode = 'en' | 'hi' | 'ta' | 'te' | 'bn' | 'mr' | 'ml' | 'kn';

export const LANGUAGES: Array<{ code: LanguageCode; label: string; nativeLabel: string }> = [
  { code: 'en', label: 'English', nativeLabel: 'English' },
  { code: 'hi', label: 'Hindi', nativeLabel: 'हिन्दी' },
  { code: 'ta', label: 'Tamil', nativeLabel: 'தமிழ்' },
  { code: 'te', label: 'Telugu', nativeLabel: 'తెలుగు' },
  { code: 'bn', label: 'Bengali', nativeLabel: 'বাংলা' },
  { code: 'mr', label: 'Marathi', nativeLabel: 'मराठी' },
  { code: 'ml', label: 'Malayalam', nativeLabel: 'മലയാളം' },
  { code: 'kn', label: 'Kannada', nativeLabel: 'ಕನ್ನಡ' },
];

type TranslationKey =
  | 'marineIntelligence' | 'overview' | 'liveSafety' | 'aiAssistant' | 'oceanState'
  | 'fishingZones' | 'mapExplorer' | 'alerts' | 'dataSources' | 'report' | 'more'
  | 'liveTelemetry' | 'selectRegion' | 'signIn' | 'utc' | 'currentTime'
  | 'criticalAlert' | 'loading' | 'recommendedSpecies' | 'oceanMetrics'
  | 'pfzRating' | 'safetyAdvisory' | 'highCatchProbability' | 'confidence';

const translations: Record<LanguageCode, Record<TranslationKey, string>> = {
  en: {
    marineIntelligence: 'Marine Intelligence', overview: 'Overview', liveSafety: 'Live Safety', aiAssistant: 'AI Assistant', oceanState: 'Ocean State', fishingZones: 'Fishing Zones', mapExplorer: 'Map Explorer', alerts: 'Alerts', dataSources: 'Data Sources', report: 'Report', more: 'More', liveTelemetry: 'LIVE TELEMETRY', selectRegion: 'Select Region', signIn: 'Sign In', utc: 'UTC', currentTime: 'Current UTC time', criticalAlert: 'Critical Alert', loading: 'Loading live data...', recommendedSpecies: 'Recommended Target Species', oceanMetrics: 'Oceanographic Front Metrics', pfzRating: 'PFZ Indicator Rating', safetyAdvisory: 'Fisherman Safety & Operational Advisory', highCatchProbability: 'High Catch Probability', confidence: 'Confidence',
  },
  hi: {
    marineIntelligence: 'समुद्री बुद्धिमत्ता', overview: 'अवलोकन', liveSafety: 'लाइव सुरक्षा', aiAssistant: 'AI सहायक', oceanState: 'समुद्री स्थिति', fishingZones: 'मछली पकड़ने के क्षेत्र', mapExplorer: 'मानचित्र', alerts: 'चेतावनियाँ', dataSources: 'डेटा स्रोत', report: 'रिपोर्ट', more: 'अधिक', liveTelemetry: 'लाइव टेलीमेट्री', selectRegion: 'क्षेत्र चुनें', signIn: 'साइन इन', utc: 'UTC', currentTime: 'वर्तमान UTC समय', criticalAlert: 'महत्वपूर्ण चेतावनी', loading: 'लाइव डेटा लोड हो रहा है...', recommendedSpecies: 'अनुशंसित मछली प्रजातियाँ', oceanMetrics: 'समुद्री मापदंड', pfzRating: 'PFZ संकेतक रेटिंग', safetyAdvisory: 'मछुआरा सुरक्षा और संचालन सलाह', highCatchProbability: 'अधिक पकड़ की संभावना', confidence: 'विश्वसनीयता',
  },
  ta: {
    marineIntelligence: 'கடல் நுண்ணறிவு', overview: 'மேலோட்டம்', liveSafety: 'நேரடி பாதுகாப்பு', aiAssistant: 'AI உதவியாளர்', oceanState: 'கடல் நிலை', fishingZones: 'மீன்பிடி மண்டலங்கள்', mapExplorer: 'வரைபடம்', alerts: 'எச்சரிக்கைகள்', dataSources: 'தரவு ஆதாரங்கள்', report: 'அறிக்கை', more: 'மேலும்', liveTelemetry: 'நேரடி டெலிமெட்ரி', selectRegion: 'மண்டலத்தைத் தேர்வு செய்க', signIn: 'உள்நுழை', utc: 'UTC', currentTime: 'தற்போதைய UTC நேரம்', criticalAlert: 'முக்கிய எச்சரிக்கை', loading: 'நேரடி தரவு ஏற்றப்படுகிறது...', recommendedSpecies: 'பரிந்துரைக்கப்பட்ட மீன் இனங்கள்', oceanMetrics: 'கடல் அளவீடுகள்', pfzRating: 'PFZ குறியீட்டு மதிப்பீடு', safetyAdvisory: 'மீனவர் பாதுகாப்பு மற்றும் செயல்பாட்டு ஆலோசனை', highCatchProbability: 'அதிக பிடிப்பு வாய்ப்பு', confidence: 'நம்பகத்தன்மை',
  },
  te: {
    marineIntelligence: 'సముద్ర మేధస్సు', overview: 'అవలోకనం', liveSafety: 'లైవ్ భద్రత', aiAssistant: 'AI సహాయకుడు', oceanState: 'సముద్ర స్థితి', fishingZones: 'చేపల వేట ప్రాంతాలు', mapExplorer: 'మ్యాప్', alerts: 'హెచ్చరికలు', dataSources: 'డేటా మూలాలు', report: 'నివేదిక', more: 'మరిన్ని', liveTelemetry: 'లైవ్ టెలిమెట్రీ', selectRegion: 'ప్రాంతాన్ని ఎంచుకోండి', signIn: 'సైన్ ఇన్', utc: 'UTC', currentTime: 'ప్రస్తుత UTC సమయం', criticalAlert: 'ముఖ్య హెచ్చరిక', loading: 'లైవ్ డేటా లోడ్ అవుతోంది...', recommendedSpecies: 'సిఫార్సు చేసిన చేప జాతులు', oceanMetrics: 'సముద్ర కొలతలు', pfzRating: 'PFZ సూచిక రేటింగ్', safetyAdvisory: 'మత్స్యకారుల భద్రతా సలహా', highCatchProbability: 'అధిక క్యాచ్ అవకాశం', confidence: 'నమ్మకం',
  },
  bn: {
    marineIntelligence: 'সামুদ্রিক বুদ্ধিমত্তা', overview: 'সংক্ষিপ্ত বিবরণ', liveSafety: 'লাইভ নিরাপত্তা', aiAssistant: 'AI সহকারী', oceanState: 'সমুদ্রের অবস্থা', fishingZones: 'মাছ ধরার অঞ্চল', mapExplorer: 'মানচিত্র', alerts: 'সতর্কতা', dataSources: 'ডেটা উৎস', report: 'রিপোর্ট', more: 'আরও', liveTelemetry: 'লাইভ টেলিমেট্রি', selectRegion: 'অঞ্চল নির্বাচন করুন', signIn: 'সাইন ইন', utc: 'UTC', currentTime: 'বর্তমান UTC সময়', criticalAlert: 'গুরুত্বপূর্ণ সতর্কতা', loading: 'লাইভ ডেটা লোড হচ্ছে...', recommendedSpecies: 'প্রস্তাবিত মাছের প্রজাতি', oceanMetrics: 'সমুদ্রের পরিমাপ', pfzRating: 'PFZ সূচক রেটিং', safetyAdvisory: 'জেলে নিরাপত্তা ও পরিচালন পরামর্শ', highCatchProbability: 'উচ্চ মাছ ধরার সম্ভাবনা', confidence: 'বিশ্বাসযোগ্যতা',
  },
  mr: {
    marineIntelligence: 'सागरी बुद्धिमत्ता', overview: 'आढावा', liveSafety: 'थेट सुरक्षा', aiAssistant: 'AI सहाय्यक', oceanState: 'समुद्राची स्थिती', fishingZones: 'मासेमारी क्षेत्रे', mapExplorer: 'नकाशा', alerts: 'सूचना', dataSources: 'डेटा स्रोत', report: 'अहवाल', more: 'अधिक', liveTelemetry: 'लाइव्ह टेलीमेट्री', selectRegion: 'प्रदेश निवडा', signIn: 'साइन इन', utc: 'UTC', currentTime: 'सध्याची UTC वेळ', criticalAlert: 'महत्त्वाची सूचना', loading: 'लाइव्ह डेटा लोड होत आहे...', recommendedSpecies: 'शिफारस केलेल्या माशांच्या प्रजाती', oceanMetrics: 'समुद्र मोजमाप', pfzRating: 'PFZ निर्देशक रेटिंग', safetyAdvisory: 'मच्छीमार सुरक्षा व कार्यवाही सल्ला', highCatchProbability: 'जास्त पकड होण्याची शक्यता', confidence: 'विश्वास',
  },
  ml: {
    marineIntelligence: 'സമുദ്ര ബുദ്ധി', overview: 'അവലോകനം', liveSafety: 'തത്സമയ സുരക്ഷ', aiAssistant: 'AI സഹായി', oceanState: 'സമുദ്ര സ്ഥിതി', fishingZones: 'മത്സ്യബന്ധന മേഖലകൾ', mapExplorer: 'ഭൂപടം', alerts: 'അറിയിപ്പുകൾ', dataSources: 'ഡാറ്റ ഉറവിടങ്ങൾ', report: 'റിപ്പോർട്ട്', more: 'കൂടുതൽ', liveTelemetry: 'തത്സമയ ടെലിമെട്രി', selectRegion: 'മേഖല തിരഞ്ഞെടുക്കുക', signIn: 'സൈൻ ഇൻ', utc: 'UTC', currentTime: 'നിലവിലെ UTC സമയം', criticalAlert: 'പ്രധാന അറിയിപ്പ്', loading: 'തത്സമയ ഡാറ്റ ലോഡ് ചെയ്യുന്നു...', recommendedSpecies: 'ശുപാർശ ചെയ്യുന്ന മത്സ്യ ഇനങ്ങൾ', oceanMetrics: 'സമുദ്ര അളവുകൾ', pfzRating: 'PFZ സൂചിക റേറ്റിംഗ്', safetyAdvisory: 'മത്സ്യത്തൊഴിലാളി സുരക്ഷാ ഉപദേശം', highCatchProbability: 'ഉയർന്ന പിടിത്ത സാധ്യത', confidence: 'വിശ്വാസ്യത',
  },
  kn: {
    marineIntelligence: 'ಸಮುದ್ರ ಬುದ್ಧಿಮತ್ತೆ', overview: 'ಅವಲೋಕನ', liveSafety: 'ಲೈವ್ ಸುರಕ್ಷತೆ', aiAssistant: 'AI ಸಹಾಯಕ', oceanState: 'ಸಮುದ್ರ ಸ್ಥಿತಿ', fishingZones: 'ಮೀನುಗಾರಿಕೆ ವಲಯಗಳು', mapExplorer: 'ನಕ್ಷೆ', alerts: 'ಎಚ್ಚರಿಕೆಗಳು', dataSources: 'ಡೇಟಾ ಮೂಲಗಳು', report: 'ವರದಿ', more: 'ಇನ್ನಷ್ಟು', liveTelemetry: 'ಲೈವ್ ಟೆಲಿಮೆಟ್ರಿ', selectRegion: 'ಪ್ರದೇಶ ಆಯ್ಕೆಮಾಡಿ', signIn: 'ಸೈನ್ ಇನ್', utc: 'UTC', currentTime: 'ಪ್ರಸ್ತುತ UTC ಸಮಯ', criticalAlert: 'ಮುಖ್ಯ ಎಚ್ಚರಿಕೆ', loading: 'ಲೈವ್ ಡೇಟಾ ಲೋಡ್ ಆಗುತ್ತಿದೆ...', recommendedSpecies: 'ಶಿಫಾರಸು ಮಾಡಿದ ಮೀನು ಜಾತಿಗಳು', oceanMetrics: 'ಸಮುದ್ರ ಮಾಪನಗಳು', pfzRating: 'PFZ ಸೂಚಕ ರೇಟಿಂಗ್', safetyAdvisory: 'ಮೀನುಗಾರರ ಸುರಕ್ಷತಾ ಸಲಹೆ', highCatchProbability: 'ಹೆಚ್ಚಿನ ಹಿಡಿತದ ಸಾಧ್ಯತೆ', confidence: 'ವಿಶ್ವಾಸಾರ್ಹತೆ',
  },
};

interface LanguageContextValue {
  language: LanguageCode;
  setLanguage: (language: LanguageCode) => void;
  t: (key: TranslationKey) => string;
}

const LanguageContext = createContext<LanguageContextValue | null>(null);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<LanguageCode>(() => {
    const stored = localStorage.getItem('varuna_language') as LanguageCode | null;
    return stored && translations[stored] ? stored : 'en';
  });

  const setLanguage = (nextLanguage: LanguageCode) => {
    setLanguageState(nextLanguage);
    localStorage.setItem('varuna_language', nextLanguage);
    document.documentElement.lang = nextLanguage;
  };

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  const value = useMemo(() => ({ language, setLanguage, t: (key: TranslationKey) => translations[language][key] }), [language]);
  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
};

export const useLanguage = (): LanguageContextValue => {
  const context = useContext(LanguageContext);
  if (!context) throw new Error('useLanguage must be used inside LanguageProvider');
  return context;
};
