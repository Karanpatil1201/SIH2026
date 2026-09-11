import React, { useState, useRef, useEffect } from 'react';
import {
  Bot, Send, Search, CheckCircle2, BookOpen, ExternalLink, Sparkles,
  Layers, Volume2, VolumeX, Copy, Check, User, ArrowRight, ShieldAlert,
  Compass, Fish, Flame, RefreshCw, Radio, Trash2, History, AlertTriangle,
  Clock, CheckCircle, XCircle, MapPin, Anchor, Cpu, Mic, MicOff, Globe,
  Brain, Dna, Swords, Sliders, Target
} from 'lucide-react';
import { AgentTraceResponse, RAGQueryResponse } from '../types';

interface AgentChatRAGProps {
  lat: number;
  lon: number;
  username?: string; // Current logged-in user — scopes chat history per user
  onChatAgent: (
    query: string,
    lat: number,
    lon: number,
    conversationHistory?: Array<{ role: 'user' | 'assistant'; text: string }>
  ) => Promise<AgentTraceResponse>;
  onQueryRAG: (question: string) => Promise<RAGQueryResponse>;
}

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  trace?: AgentTraceResponse;
  rag?: RAGQueryResponse;
}

const BASE_HISTORY_KEY = 'varuna_agent_chat_history_v2';
const MAX_STORED_MESSAGES = 40;

const VOICE_LANGUAGES = [
  { code: 'auto', label: 'Auto Detect (Multilingual)', flag: '🌐' },
  { code: 'mr-IN', label: 'मराठी (Marathi)', flag: '🇮🇳' },
  { code: 'hi-IN', label: 'हिन्दी (Hindi)', flag: '🇮🇳' },
  { code: 'en-IN', label: 'English (India)', flag: '🇮🇳' },
  { code: 'ta-IN', label: 'தமிழ் (Tamil)', flag: '🇮🇳' },
  { code: 'te-IN', label: 'తెలుగు (Telugu)', flag: '🇮🇳' },
  { code: 'kn-IN', label: 'ಕನ್ನಡ (Kannada)', flag: '🇮🇳' },
  { code: 'ml-IN', label: 'മലയാളം (Malayalam)', flag: '🇮🇳' },
  { code: 'bn-IN', label: 'বাংলা (Bengali)', flag: '🇮🇳' },
  { code: 'gu-IN', label: 'ગુજરાતી (Gujarati)', flag: '🇮🇳' },
];

// Returns a user-scoped localStorage key so each account has isolated chat history
const getUserChatKey = (username?: string) =>
  username ? `${BASE_HISTORY_KEY}_${username}` : BASE_HISTORY_KEY;

const FormattedMessage: React.FC<{ content: string; isUser: boolean }> = ({ content, isUser }) => {
  if (isUser) {
    return <span className="font-medium text-white">{content}</span>;
  }

  // Parse inline markdown tokens: bold (**text** or __text__), code (`text`), italic (*text* or _text_)
  const parseInline = (text: string): React.ReactNode[] => {
    const parts: React.ReactNode[] = [];
    const regex = /(\*\*([^*]+)\*\*|__([^_]+)__|`([^`]+)`|\*([^*]+)\*|_([^_]+)_)/g;
    let lastIndex = 0;
    let match: RegExpExecArray | null;

    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parts.push(text.substring(lastIndex, match.index));
      }
      const boldText = match[2] || match[3];
      const codeText = match[4];
      const italicText = match[5] || match[6];

      if (boldText) {
        parts.push(
          <strong key={`b_${match.index}`} className="font-bold text-cyan-300">
            {boldText}
          </strong>
        );
      } else if (codeText) {
        parts.push(
          <code key={`c_${match.index}`} className="px-1.5 py-0.5 rounded bg-slate-900 text-cyan-300 font-mono text-xs border border-slate-800">
            {codeText}
          </code>
        );
      } else if (italicText) {
        parts.push(
          <em key={`i_${match.index}`} className="italic text-slate-300">
            {italicText}
          </em>
        );
      }
      lastIndex = regex.lastIndex;
    }
    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex));
    }
    return parts.length > 0 ? parts : [text];
  };

  const lines = content.split('\n');
  const renderedElements: React.ReactNode[] = [];

  lines.forEach((line, idx) => {
    let trimmed = line.trim();
    if (!trimmed) {
      renderedElements.push(<div key={`empty_${idx}`} className="h-1.5" />);
      return;
    }

    // Horizontal Rule dividers (---, ***, ___)
    if (/^(\-{3,}|\*{3,}|_{3,})$/.test(trimmed)) {
      renderedElements.push(<hr key={`hr_${idx}`} className="border-slate-800/80 my-2.5" />);
      return;
    }

    // Headings #, ##, ###, ####, etc.
    const headingMatch = trimmed.match(/^(#{1,6})\s+(.*)$/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      const headingText = headingMatch[2];
      if (level === 1) {
        renderedElements.push(
          <h2 key={`h1_${idx}`} className="text-sm sm:text-base font-extrabold text-cyan-400 mt-2.5 mb-1 flex items-center space-x-1.5">
            <span>{parseInline(headingText)}</span>
          </h2>
        );
      } else if (level === 2) {
        renderedElements.push(
          <h3 key={`h2_${idx}`} className="text-xs sm:text-sm font-bold text-blue-300 mt-2 mb-1">
            {parseInline(headingText)}
          </h3>
        );
      } else {
        renderedElements.push(
          <h4 key={`h3_${idx}`} className="text-xs sm:text-sm font-bold text-teal-300 uppercase tracking-wide mt-2 mb-1 pb-0.5 border-b border-slate-800/80">
            {parseInline(headingText)}
          </h4>
        );
      }
      return;
    }

    // Bullet points (*, -, +, •, ▸)
    if (/^(\*|\-|\+|\•|\▸)\s+/.test(trimmed)) {
      const bulletText = trimmed.replace(/^(\*|\-|\+|\•|\▸)\s+/, '');
      renderedElements.push(
        <div key={`li_${idx}`} className="flex items-start space-x-2 pl-1.5 text-slate-200 text-xs sm:text-sm my-1">
          <span className="text-cyan-400 font-bold text-xs mt-0.5 select-none">▸</span>
          <span className="flex-1 leading-relaxed">{parseInline(bulletText)}</span>
        </div>
      );
      return;
    }

    // Numbered lists (1. , 2. )
    const numMatch = trimmed.match(/^(\d+)[\.\)]\s+(.*)$/);
    if (numMatch) {
      renderedElements.push(
        <div key={`num_${idx}`} className="flex items-start space-x-2 pl-1.5 text-slate-200 text-xs sm:text-sm my-1">
          <span className="text-cyan-400 font-mono font-bold text-xs mt-0.5 select-none">{numMatch[1]}.</span>
          <span className="flex-1 leading-relaxed">{parseInline(numMatch[2])}</span>
        </div>
      );
      return;
    }

    // Standard paragraph
    renderedElements.push(
      <p key={`p_${idx}`} className="text-xs sm:text-sm text-slate-200 leading-relaxed my-0.5">
        {parseInline(trimmed)}
      </p>
    );
  });

  return <div className="space-y-0.5">{renderedElements}</div>;
};

export const AgentChatRAG: React.FC<AgentChatRAGProps> = ({ lat, lon, username, onChatAgent, onQueryRAG }) => {
  const [activeSubMode, setActiveSubMode] = useState<'chat' | 'rag'>('chat');
  const [chatQuery, setChatQuery] = useState<string>('');
  const [ragQuery, setRagQuery] = useState<string>('');
  const [chatLoading, setChatLoading] = useState<boolean>(false);
  const [ragLoading, setRagLoading] = useState<boolean>(false);
  const [activeTraceTab, setActiveTraceTab] = useState<Record<string, 'dag' | 'evidence' | 'pfz' | 'departure' | 'why' | 'dna' | 'dissent' | 'timeline' | 'triggers'>>({});

  // Audio Speech synthesis state
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Voice to Text (Speech Recognition) state
  const [isListening, setIsListening] = useState<boolean>(false);
  const [speechLang, setSpeechLang] = useState<string>('auto');
  const [speechError, setSpeechError] = useState<string | null>(null);
  const [isLangMenuOpen, setIsLangMenuOpen] = useState<boolean>(false);
  const recognitionRef = useRef<any>(null);

  // Build the welcome message for the current user
  const buildWelcome = (user?: string): ChatMessage => ({
    id: `welcome_${Date.now()}`,
    sender: 'assistant',
    text: `🌊 **VARUNA Marine Decision Intelligence Copilot**\n${user ? `Welcome, **${user}**!` : 'Welcome!'} I am your collaborative multi-agent assistant for sector (${lat.toFixed(2)}° N, ${lon.toFixed(2)}° E).\n\nAsk in English, हिन्दी, मराठी, தமிழ், తెలుగు, ಕನ್ನಡ, മലയാളം, or বাংলা.`,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  });

  // Chat Message History — loaded from user-scoped localStorage key
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    try {
      const stored = localStorage.getItem(getUserChatKey(username));
      if (stored) return JSON.parse(stored) as ChatMessage[];
    } catch (error) {
      console.warn('[VARUNA Chat] Could not restore chat history', error);
    }
    return [buildWelcome(username)];
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // When user changes (login/logout/switch), clear chat and start fresh
  const prevUsernameRef = useRef<string | undefined>(username);
  useEffect(() => {
    if (prevUsernameRef.current !== username) {
      prevUsernameRef.current = username;
      // Try to restore this user's existing history first
      try {
        const stored = localStorage.getItem(getUserChatKey(username));
        if (stored) {
          const parsed = JSON.parse(stored) as ChatMessage[];
          if (parsed.length > 0) {
            setMessages(parsed);
            return;
          }
        }
      } catch { /* ignore */ }
      // No history for this user — show fresh welcome
      setMessages([buildWelcome(username)]);
    }
  }, [username]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Persist messages to user-scoped key
  useEffect(() => {
    try {
      localStorage.setItem(getUserChatKey(username), JSON.stringify(messages.slice(-MAX_STORED_MESSAGES)));
    } catch (error) {
      console.warn('[VARUNA Chat] Could not save chat history', error);
    }
  }, [messages, username]);

  const clearChatHistory = () => {
    localStorage.removeItem(getUserChatKey(username));
    setMessages([buildWelcome(username)]);
  };

  // Official SIH Demo Scenarios
  const quickDemoScenarios = [
    {
      title: '🎣 1. Fisherman Ratnagiri (PFZ + Route + 6 AM)',
      prompt: 'I am a fisherman near Ratnagiri. Can I go fishing tomorrow at 6 AM? Find the nearest good PFZ and show me the safest route.'
    },
    {
      title: '⏰ 2. What about 8 AM instead?',
      prompt: 'What about 8 AM departure instead?'
    },
    {
      title: '🇮🇳 3. मराठी (Explain in Marathi)',
      prompt: 'उद्या समुद्रात जाणे सुरक्षित आहे का? मला शिफारस सांगा.'
    },
    {
      title: '🚫 4. Geofence & Route Rejection',
      prompt: 'Show me the safest route from Mumbai to Goa and check restricted naval waters.'
    },
    {
      title: '📉 5. Ecosystem & Fish Decline',
      prompt: 'Why has fish productivity decreased in this region?'
    },
    {
      title: '⚡ 6. Lightning & Cyclone Hazard',
      prompt: 'Are there any active lightning or cyclone alerts near my coordinates?'
    }
  ];

  const handleSendChat = async (inputQuery?: string) => {
    const queryToUse = inputQuery || chatQuery;
    if (!queryToUse.trim()) return;

    const userMsgId = `user_${Date.now()}`;
    const userMsg: ChatMessage = {
      id: userMsgId,
      sender: 'user',
      text: queryToUse,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    if (!inputQuery) setChatQuery('');
    setChatLoading(true);

    try {
      const conversationHistory = messages
        .filter(message => message.sender === 'user' || message.sender === 'assistant')
        .slice(-8)
        .map(message => ({
          role: message.sender,
          text: message.text
        }));

      // Extract coordinates if user explicitly stated them in query
      let queryLat = lat;
      let queryLon = lon;
      const devanagariDigits: Record<string, string> = {
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
        '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
      };
      const normalizedQuery = queryToUse.replace(/[०-९]/g, d => devanagariDigits[d] || d);
      const coordMatch = normalizedQuery.match(/(?:lat(?:itude)?\s*[:=]?\s*)?(-?\d+(?:\.\d+)?)\s*(?:°|deg)?\s*([NSns])?\s*[,;\s/|]+\s*(?:lon(?:gitude)?\s*[:=]?\s*)?(-?\d+(?:\.\d+)?)\s*(?:°|deg)?\s*([EWew])?/i);
      if (coordMatch) {
        let pLat = parseFloat(coordMatch[1]);
        const latHemi = (coordMatch[2] || '').toUpperCase();
        if (latHemi === 'S') pLat = -Math.abs(pLat);
        else if (latHemi === 'N') pLat = Math.abs(pLat);

        let pLon = parseFloat(coordMatch[3]);
        const lonHemi = (coordMatch[4] || '').toUpperCase();
        if (lonHemi === 'W') pLon = -Math.abs(pLon);
        else if (lonHemi === 'E') pLon = Math.abs(pLon);

        if (!isNaN(pLat) && !isNaN(pLon) && pLat >= -90 && pLat <= 90 && pLon >= -180 && pLon <= 180) {
          queryLat = Number(pLat.toFixed(4));
          queryLon = Number(pLon.toFixed(4));
        }
      } else {
        const qLower = normalizedQuery.toLowerCase();
        const coastalCities: Record<string, [number, number]> = {
          'kanyakumari': [8.0883, 77.5385],
          'कन्याकुमारी': [8.0883, 77.5385],
          'கன்னியாகுமரி': [8.0883, 77.5385],
          'mumbai': [18.9667, 72.8333],
          'bombay': [18.9667, 72.8333],
          'मुंबई': [18.9667, 72.8333],
          'ratnagiri': [16.9902, 73.2980],
          'रत्नागिरी': [16.9902, 73.2980],
          'goa': [15.4989, 73.8278],
          'panaji': [15.4989, 73.8278],
          'गोवा': [15.4989, 73.8278],
          'rameshwaram': [9.2876, 79.3129],
          'रामेश्वरम': [9.2876, 79.3129],
          'kochi': [9.9667, 76.2667],
          'cochin': [9.9667, 76.2667],
          'कोची': [9.9667, 76.2667],
          'chennai': [13.0827, 80.2707],
          'चेन्नई': [13.0827, 80.2707],
          'mangalore': [12.9242, 74.8190],
          'visakhapatnam': [17.6868, 83.2185],
          'vizag': [17.6868, 83.2185],
          'paradip': [20.3165, 86.6114],
          'kolkata': [22.0257, 88.0583],
          'veraval': [20.9000, 70.3667],
          'kandla': [23.0033, 70.2189],
          'alibaug': [18.6414, 72.8722],
          'malvan': [16.0558, 73.4668],
          'karwar': [14.8136, 74.1298],
          'porbandar': [21.6417, 69.6293],
          'daman': [20.3974, 72.8328],
          'diu': [20.7144, 70.9874],
          'puri': [19.8135, 85.8312],
          'port blair': [11.6234, 92.7265],
          'andaman': [11.6234, 92.7265],
          'lakshadweep': [10.5667, 72.6417]
        };
        for (const [cityName, coords] of Object.entries(coastalCities)) {
          if (qLower.includes(cityName)) {
            queryLat = coords[0];
            queryLon = coords[1];
            break;
          }
        }
      }

      const traceRes = await onChatAgent(queryToUse, queryLat, queryLon, conversationHistory);
      const assistantMsg: ChatMessage = {
        id: `asst_${Date.now()}`,
        sender: 'assistant',
        text: traceRes.final_answer,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        trace: traceRes
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      console.error('Chat error', err);
    } finally {
      setChatLoading(false);
    }
  };

  const handleSearchRAG = async (inputQuery?: string) => {
    const queryToUse = inputQuery || ragQuery;
    if (!queryToUse.trim()) return;

    const userMsgId = `user_rag_${Date.now()}`;
    const userMsg: ChatMessage = {
      id: userMsgId,
      sender: 'user',
      text: `[Knowledge Search]: ${queryToUse}`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    if (!inputQuery) setRagQuery('');
    setRagLoading(true);

    try {
      const ragRes = await onQueryRAG(queryToUse);
      const assistantMsg: ChatMessage = {
        id: `asst_rag_${Date.now()}`,
        sender: 'assistant',
        text: `### 📖 INCOIS & DG Shipping Regulatory Answer\n${ragRes.answer}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        rag: ragRes
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      console.error('RAG error', err);
    } finally {
      setRagLoading(false);
    }
  };

  const handleSpeakText = (text: string) => {
    if ('speechSynthesis' in window) {
      if (isSpeaking) {
        window.speechSynthesis.cancel();
        setIsSpeaking(false);
        return;
      }
      const plainText = text.replace(/[*#`]/g, '');
      const utterance = new SpeechSynthesisUtterance(plainText);
      utterance.rate = 1.0;
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      setIsSpeaking(true);
      window.speechSynthesis.speak(utterance);
    }
  };

  // Clean up speech recognition on unmount
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch { /* ignore */ }
      }
    };
  }, []);

  const toggleListening = () => {
    if (isListening) {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch { /* ignore */ }
      }
      setIsListening(false);
      return;
    }

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setSpeechError('Voice recognition is not supported in this browser. Please use Chrome, Edge, or Safari.');
      setTimeout(() => setSpeechError(null), 5000);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;

      if (speechLang !== 'auto') {
        recognition.lang = speechLang;
      } else {
        recognition.lang = navigator.language || 'en-IN';
      }

      recognition.onstart = () => {
        setIsListening(true);
        setSpeechError(null);
      };

      recognition.onresult = (event: any) => {
        let interimText = '';
        let finalText = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalText += transcript;
          } else {
            interimText += transcript;
          }
        }

        const currentText = finalText || interimText;
        if (currentText.trim()) {
          if (activeSubMode === 'chat') {
            setChatQuery(currentText);
          } else {
            setRagQuery(currentText);
          }
        }
      };

      recognition.onerror = (event: any) => {
        console.warn('[VARUNA Voice] Speech recognition error:', event.error);
        if (event.error === 'not-allowed') {
          setSpeechError('Microphone access denied. Please allow microphone permissions.');
        } else if (event.error !== 'no-speech') {
          setSpeechError(`Voice error: ${event.error}`);
        }
        setIsListening(false);
        setTimeout(() => setSpeechError(null), 4000);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.error('Failed to start speech recognition:', err);
      setIsListening(false);
      setSpeechError('Unable to access microphone');
      setTimeout(() => setSpeechError(null), 4000);
    }
  };

  const handleCopyText = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="space-y-4 text-slate-100 selection:bg-cyan-500 selection:text-slate-950">
      {/* Console Header */}
      <div className="bg-[#07192c] border border-slate-800 p-4 rounded-3xl flex flex-wrap items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 shadow-lg shadow-cyan-500/20 text-white">
            <Bot className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="font-extrabold text-white text-base">VARUNA Autonomous Marine Decision AI</h3>
              <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-cyan-950 text-cyan-400 border border-cyan-800">
                11-Agent Collaborative DAG
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">Multilingual Intent Reasoning, Geofencing & INCOIS RAG</p>
          </div>
        </div>

        <div className="flex items-center space-x-1.5 bg-[#05111d] p-1 rounded-2xl border border-slate-800">
          <button
            onClick={() => setActiveSubMode('chat')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
              activeSubMode === 'chat'
                ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Multi-Agent Command Chat
          </button>
          <button
            onClick={() => setActiveSubMode('rag')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
              activeSubMode === 'rag'
                ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Regulatory RAG Engine
          </button>
          <button
            onClick={clearChatHistory}
            title="Clear Chat History"
            className="p-1.5 rounded-xl text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* SIH Official 1-Click Demo Scenarios Bar */}
      <div className="bg-[#05111d] border border-slate-800 p-3 rounded-2xl space-y-2">
        <div className="flex items-center space-x-2 text-xs font-bold text-slate-400 font-mono uppercase tracking-wider">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>SIH 2026 Presentation Demo Scenarios:</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {quickDemoScenarios.map((s, idx) => (
            <button
              key={idx}
              disabled={chatLoading}
              onClick={() => handleSendChat(s.prompt)}
              className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 hover:border-cyan-500/50 transition-all flex items-center space-x-1 shadow-sm"
            >
              <span>{s.title}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="bg-[#05111d] border border-slate-800 rounded-3xl p-4 min-h-[460px] max-h-[620px] overflow-y-auto space-y-4 shadow-inner">
        {messages.map((msg) => {
          const isUser = msg.sender === 'user';
          const trace = msg.trace;
          const msgTab = activeTraceTab[msg.id] || 'dag';

          return (
            <div key={msg.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[90%] md:max-w-[80%] rounded-3xl p-4 space-y-3 ${
                isUser
                  ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-tr-sm shadow-lg'
                  : 'bg-[#081b2e] border border-slate-800 text-slate-200 rounded-tl-sm shadow-xl'
              }`}>
                {/* Header info */}
                <div className="flex items-center justify-between text-[11px] opacity-75 font-mono border-b border-white/10 pb-1.5">
                  <div className="flex items-center space-x-1.5">
                    {isUser ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5 text-cyan-400" />}
                    <span className="font-bold">{isUser ? 'Navigator' : 'VARUNA Multi-Agent AI'}</span>
                    {!isUser && trace?.detected_language && (
                      <span className="px-1.5 py-0.2 rounded text-[9px] font-bold bg-cyan-950 text-cyan-400 border border-cyan-800 uppercase">
                        {trace.detected_language}
                      </span>
                    )}
                  </div>
                  <span>{msg.timestamp}</span>
                </div>

                {/* Message Body */}
                <div className="text-sm font-sans leading-relaxed">
                  <FormattedMessage content={msg.text} isUser={isUser} />
                </div>

                {/* Agent Observability Details & Tabs (If trace exists) */}
                {!isUser && trace && (
                  <div className="pt-2 border-t border-slate-800/80 space-y-3">
                    {/* Trace Tabs */}
                    <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
                      <button
                        onClick={() => setActiveTraceTab(prev => ({ ...prev, [msg.id]: 'dag' }))}
                        className={`px-2.5 py-1 rounded-lg font-bold flex items-center space-x-1 transition-all ${
                          msgTab === 'dag' ? 'bg-cyan-500 text-slate-950' : 'bg-slate-900 text-slate-400 hover:text-white'
                        }`}
                      >
                        <Cpu className="w-3 h-3" />
                        <span>Agent Execution DAG ({trace.execution_steps?.length || 0})</span>
                      </button>

                      {trace.pfz_candidates && trace.pfz_candidates.length > 0 && (
                        <button
                          onClick={() => setActiveTraceTab(prev => ({ ...prev, [msg.id]: 'pfz' }))}
                          className={`px-2.5 py-1 rounded-lg font-bold flex items-center space-x-1 transition-all ${
                            msgTab === 'pfz' ? 'bg-emerald-500 text-slate-950' : 'bg-slate-900 text-slate-400 hover:text-white'
                          }`}
                        >
                          <Fish className="w-3 h-3" />
                          <span>Candidate PFZs ({trace.pfz_candidates.length})</span>
                        </button>
                      )}

                      {trace.departure_optimization && (
                        <button
                          onClick={() => setActiveTraceTab(prev => ({ ...prev, [msg.id]: 'departure' }))}
                          className={`px-2.5 py-1 rounded-lg font-bold flex items-center space-x-1 transition-all ${
                            msgTab === 'departure' ? 'bg-amber-500 text-slate-950' : 'bg-slate-900 text-slate-400 hover:text-white'
                          }`}
                        >
                          <Clock className="w-3 h-3" />
                          <span>Departure Time Risk</span>
                        </button>
                      )}

                      {trace.why_engine && (
                        <button
                          onClick={() => setActiveTraceTab(prev => ({ ...prev, [msg.id]: 'why' }))}
                          className={`px-2.5 py-1 rounded-lg font-bold flex items-center space-x-1 transition-all ${
                            msgTab === 'why' ? 'bg-purple-600 text-white shadow-sm' : 'bg-slate-900 text-slate-400 hover:text-white'
                          }`}
                        >
                          <Brain className="w-3 h-3" />
                          <span>Marine WHY</span>
                        </button>
                      )}

                      {trace.decision_dna && (
                        <button
                          onClick={() => setActiveTraceTab(prev => ({ ...prev, [msg.id]: 'dna' }))}
                          className={`px-2.5 py-1 rounded-lg font-bold flex items-center space-x-1 transition-all ${
                            msgTab === 'dna' ? 'bg-indigo-600 text-white shadow-sm' : 'bg-slate-900 text-slate-400 hover:text-white'
                          }`}
                        >
                          <Dna className="w-3 h-3" />
                          <span>🧬 Decision DNA</span>
                        </button>
                      )}

                      {trace.agent_dissent && (
                        <button
                          onClick={() => setActiveTraceTab(prev => ({ ...prev, [msg.id]: 'dissent' }))}
                          className={`px-2.5 py-1 rounded-lg font-bold flex items-center space-x-1 transition-all ${
                            msgTab === 'dissent' ? 'bg-rose-600 text-white shadow-sm' : 'bg-slate-900 text-slate-400 hover:text-white'
                          }`}
                        >
                          <Swords className="w-3 h-3" />
                          <span>⚔️ Agent Dissent</span>
                        </button>
                      )}

                      {trace.timeline && (
                        <button
                          onClick={() => setActiveTraceTab(prev => ({ ...prev, [msg.id]: 'timeline' }))}
                          className={`px-2.5 py-1 rounded-lg font-bold flex items-center space-x-1 transition-all ${
                            msgTab === 'timeline' ? 'bg-blue-600 text-white shadow-sm' : 'bg-slate-900 text-slate-400 hover:text-white'
                          }`}
                        >
                          <History className="w-3 h-3" />
                          <span>⏳ Timeline</span>
                        </button>
                      )}

                      <button
                        onClick={() => setActiveTraceTab(prev => ({ ...prev, [msg.id]: 'evidence' }))}
                        className={`px-2.5 py-1 rounded-lg font-bold flex items-center space-x-1 transition-all ${
                          msgTab === 'evidence' ? 'bg-blue-500 text-white' : 'bg-slate-900 text-slate-400 hover:text-white'
                        }`}
                      >
                        <BookOpen className="w-3 h-3" />
                        <span>Evidence Provenance</span>
                      </button>
                    </div>

                    {/* Tab 1: Agent Execution DAG */}
                    {msgTab === 'dag' && (
                      <div className="bg-slate-950 p-3 rounded-2xl border border-slate-800 space-y-2 text-xs">
                        <div className="font-bold text-slate-400 text-[10px] uppercase font-mono tracking-wider">
                          Autonomous Multi-Agent Execution Graph
                        </div>
                        <div className="space-y-1.5">
                          {trace.execution_steps?.map((step, sIdx) => {
                            const isDone = step.status === 'COMPLETED' || step.status === 'SUCCESS';
                            const isWarn = step.status === 'WARNING';
                            const isFall = step.status === 'FALLBACK';
                            return (
                              <div key={sIdx} className="flex items-start justify-between p-2 rounded-xl bg-slate-900/80 border border-slate-800/80">
                                <div className="flex items-start space-x-2">
                                  <div className="mt-0.5">
                                    {isDone && <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />}
                                    {isWarn && <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />}
                                    {isFall && <Radio className="w-3.5 h-3.5 text-cyan-400" />}
                                  </div>
                                  <div>
                                    <div className="font-bold text-slate-200">{step.agent_name}</div>
                                    <div className="text-[11px] text-slate-400">{step.action_taken}</div>
                                  </div>
                                </div>
                                <span className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold uppercase ${
                                  isDone ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' :
                                  isWarn ? 'bg-amber-950 text-amber-400 border border-amber-800' : 'bg-cyan-950 text-cyan-400'
                                }`}>
                                  {step.status}
                                </span>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Tab 2: Candidate PFZs */}
                    {msgTab === 'pfz' && trace.pfz_candidates && (
                      <div className="bg-slate-950 p-3 rounded-2xl border border-slate-800 space-y-2 text-xs">
                        <div className="font-bold text-slate-400 text-[10px] uppercase font-mono tracking-wider">
                          Candidate Potential Fishing Zones (Ranked by Safety & Potential)
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                          {trace.pfz_candidates.map((pfz: any, pIdx: number) => {
                            const isRec = pfz.recommendation_badge === 'RECOMMENDED';
                            const isRej = pfz.recommendation_badge === 'REJECTED' || pfz.in_restricted_waters;
                            return (
                              <div key={pIdx} className={`p-2.5 rounded-xl border ${
                                isRec ? 'bg-emerald-950/40 border-emerald-500/50' :
                                isRej ? 'bg-red-950/40 border-red-500/50' : 'bg-slate-900 border-slate-800'
                              } space-y-1.5`}>
                                <div className="flex items-center justify-between">
                                  <span className="font-extrabold text-white text-xs">{pfz.name}</span>
                                  <span className={`px-1.5 py-0.2 rounded text-[9px] font-bold ${
                                    isRec ? 'bg-emerald-500 text-slate-950' :
                                    isRej ? 'bg-red-500 text-white' : 'bg-amber-500 text-slate-950'
                                  }`}>
                                    {pfz.recommendation_badge}
                                  </span>
                                </div>
                                <div className="text-[11px] text-slate-300 space-y-0.5">
                                  <div>Distance: <b>{pfz.distance_km} km</b></div>
                                  <div>Potential: <b>{pfz.fishing_potential_score}/100</b></div>
                                  <div>Wave Risk: <b>{pfz.wave_height_m}m (Score: {pfz.risk_score}/100)</b></div>
                                </div>
                                <div className="text-[10px] text-slate-400 italic">{pfz.recommendation_reason}</div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Tab 3: Departure Optimization */}
                    {msgTab === 'departure' && trace.departure_optimization && (
                      <div className="bg-slate-950 p-3 rounded-2xl border border-slate-800 space-y-2 text-xs">
                        <div className="font-bold text-slate-400 text-[10px] uppercase font-mono tracking-wider">
                          Departure Time Risk Timeline (Wave & Wind Trend)
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-6 gap-2">
                          {trace.departure_optimization.departure_windows?.map((win: any, wIdx: number) => {
                            const isSafe = win.status === 'SAFE';
                            const isDanger = win.status === 'DANGER';
                            const isOpt = win.hour === trace.departure_optimization.recommended_window;
                            return (
                              <div key={wIdx} className={`p-2 rounded-xl text-center border ${
                                isOpt ? 'bg-cyan-950/60 border-cyan-400 shadow-md shadow-cyan-500/20' :
                                isSafe ? 'bg-slate-900 border-emerald-500/40' :
                                isDanger ? 'bg-slate-900 border-red-500/40' : 'bg-slate-900 border-slate-800'
                              }`}>
                                <div className="font-extrabold text-white text-xs">{win.hour}</div>
                                <div className="text-[10px] text-slate-400 font-mono">{win.wave_h}m waves</div>
                                <div className={`mt-1 text-[10px] font-bold ${
                                  isSafe ? 'text-emerald-400' : isDanger ? 'text-red-400' : 'text-amber-400'
                                }`}>
                                  Risk: {win.risk}/100
                                </div>
                                {isOpt && <div className="text-[9px] font-black text-cyan-400 mt-0.5">★ OPTIMAL</div>}
                              </div>
                            );
                          })}
                        </div>
                        <div className="text-[11px] text-cyan-300 font-medium p-2 rounded-lg bg-cyan-950/30 border border-cyan-800/40">
                          {trace.departure_optimization.recommendation}
                        </div>
                      </div>
                    )}

                    {/* Tab 4: Evidence Sources */}
                    {msgTab === 'evidence' && (
                      <div className="bg-slate-950 p-3 rounded-2xl border border-slate-800 space-y-2 text-xs">
                        <div className="font-bold text-slate-400 text-[10px] uppercase font-mono tracking-wider">
                          Data Trust & Source Provenance
                        </div>
                        <div className="space-y-1.5">
                          {trace.evidence_sources?.map((src, srcIdx) => (
                            <div key={srcIdx} className="flex items-center justify-between p-2 rounded-xl bg-slate-900/80 border border-slate-800/80 text-[11px]">
                              <div>
                                <span className="font-bold text-white">{src.name}</span>
                                <span className="text-slate-400 ml-2">({src.role})</span>
                              </div>
                              <div className="flex items-center space-x-2">
                                <span className="px-1.5 py-0.2 rounded text-[9px] font-mono font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                                  {src.freshness || 'LIVE'}
                                </span>
                                <span className="text-slate-400 text-[10px]">Trust: {(src.trust ? src.trust * 100 : 95).toFixed(0)}%</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Tab: Marine WHY Engine */}
                    {msgTab === 'why' && trace.why_engine && (
                      <div className="bg-slate-950 p-3.5 rounded-2xl border border-purple-900/40 space-y-2.5 text-xs">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-purple-400 text-[10px] uppercase font-mono tracking-wider">
                            Marine WHY Engine — Causal Reasoning
                          </span>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            trace.why_engine.recommendation === 'RECOMMENDED' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' :
                            trace.why_engine.recommendation === 'CAUTION' ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                            'bg-red-950 text-red-400 border border-red-800'
                          }`}>
                            {trace.why_engine.recommendation}
                          </span>
                        </div>
                        <p className="text-slate-300 leading-relaxed">{trace.why_engine.summary_why}</p>
                        <div className="space-y-1 pt-1">
                          <div className="font-bold text-slate-400 text-[10px] uppercase font-mono">Primary Contributing Factors:</div>
                          {trace.why_engine.primary_factors.map((factor, fIdx) => (
                            <div key={fIdx} className="text-slate-300 flex items-start space-x-1.5">
                              <span className="text-purple-400 font-bold">•</span>
                              <span>{factor}</span>
                            </div>
                          ))}
                        </div>
                        <div className="pt-2 border-t border-slate-900 flex justify-between text-[10px] text-slate-400">
                          <span>Supporting: <b>{trace.why_engine.supporting_agents?.join(', ') || 'All'}</b></span>
                          <span>Confidence: <b>{Math.round(trace.why_engine.confidence * 100)}%</b></span>
                        </div>
                      </div>
                    )}

                    {/* Tab: Decision DNA */}
                    {msgTab === 'dna' && trace.decision_dna && (
                      <div className="bg-slate-950 p-3.5 rounded-2xl border border-indigo-900/40 space-y-2.5 text-xs">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-indigo-400 text-[10px] uppercase font-mono tracking-wider">
                            🧬 Decision DNA Blueprint ({trace.decision_dna.decision_id})
                          </span>
                          <span className="font-mono text-[10px] text-slate-400">
                            Risk: {Math.round(trace.decision_dna.risk_score)}/100 | Conf: {Math.round(trace.decision_dna.confidence * 100)}%
                          </span>
                        </div>
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                          {Object.entries(trace.decision_dna.agents || {}).map(([ag, st]) => (
                            <div key={ag} className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-center">
                              <div className="text-[10px] font-mono text-slate-400 uppercase">{ag}</div>
                              <div className={`text-[11px] font-bold ${
                                st === 'SAFE' || st === 'RECOMMENDED' ? 'text-emerald-400' :
                                st === 'DANGER' || st === 'AVOID' ? 'text-red-400' : 'text-amber-400'
                              }`}>{st}</div>
                            </div>
                          ))}
                        </div>
                        <div className="space-y-1 pt-1">
                          <div className="font-bold text-slate-400 text-[10px] uppercase font-mono">Major Factors:</div>
                          {trace.decision_dna.major_factors.map((m, mIdx) => (
                            <div key={mIdx} className="text-slate-300">• {m}</div>
                          ))}
                        </div>
                        {trace.what_would_change && (
                          <div className="p-2 rounded-xl bg-indigo-950/30 border border-indigo-900/40 text-[11px] text-slate-300 space-y-1">
                            <div className="font-bold text-indigo-300">Conditions that would change this decision:</div>
                            {trace.what_would_change.slice(0, 2).map((tr, trIdx) => (
                              <div key={trIdx}>• {tr}</div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Tab: Agent Dissent & Conflict Resolution */}
                    {msgTab === 'dissent' && trace.agent_dissent && (
                      <div className="bg-slate-950 p-3.5 rounded-2xl border border-rose-900/40 space-y-2.5 text-xs">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-rose-400 text-[10px] uppercase font-mono tracking-wider">
                            ⚔️ Agent Dissent & Multi-Agent Arbitration
                          </span>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            trace.agent_dissent.has_conflict ? 'bg-amber-950 text-amber-400 border border-amber-800' : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                          }`}>
                            {trace.agent_dissent.has_conflict ? 'CONFLICT RESOLVED' : 'UNANIMOUS'}
                          </span>
                        </div>
                        <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 text-slate-300 leading-relaxed">
                          {trace.agent_dissent.conflict_detected}
                        </div>
                        {trace.agent_dissent.has_conflict && (
                          <div className="p-2.5 rounded-xl bg-rose-950/20 border border-rose-900/40 text-slate-300 space-y-1">
                            <div className="font-bold text-rose-300 text-[11px]">Orchestrator Resolution: {trace.agent_dissent.resolution_strategy}</div>
                            <div className="text-[11px] text-slate-400">{trace.agent_dissent.resolution_rationale}</div>
                          </div>
                        )}
                        <div className="space-y-1">
                          {trace.agent_dissent.agent_opinions?.slice(0, 4).map((op, oIdx) => (
                            <div key={oIdx} className="flex items-center justify-between p-1.5 rounded-lg bg-slate-900/50 text-[11px]">
                              <span className="font-bold text-slate-200">{op.agent}</span>
                              <span className="font-mono text-slate-400">{op.decision}</span>
                              <span className="text-slate-400 truncate max-w-[200px]">{op.key_evidence}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Tab: Marine Timeline */}
                    {msgTab === 'timeline' && trace.timeline && (
                      <div className="bg-slate-950 p-3.5 rounded-2xl border border-blue-900/40 space-y-2.5 text-xs">
                        <div className="font-bold text-blue-400 text-[10px] uppercase font-mono tracking-wider">
                          ⏳ Marine Temporal Timeline: Past → Present → Future
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                          {trace.timeline.timeline_stages?.map((stage, stIdx) => (
                            <div key={stIdx} className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                              <div className="flex justify-between font-bold">
                                <span className="text-white">{stage.stage}</span>
                                <span className={`text-[10px] ${
                                  stage.risk_level === 'SAFE' ? 'text-emerald-400' :
                                  stage.risk_level === 'DANGER' ? 'text-red-400' : 'text-amber-400'
                                }`}>{stage.risk_level} ({Math.round(stage.risk_score)})</span>
                              </div>
                              <div className="text-[10px] text-slate-400">Wave: {stage.wave_height_m}m | Wind: {stage.wind_speed_kmh} km/h</div>
                              <div className="text-[10px] text-slate-500 italic">{stage.notes}</div>
                            </div>
                          ))}
                        </div>
                        <p className="text-[11px] text-blue-300 font-medium p-2 rounded-lg bg-blue-950/30 border border-blue-900/40">
                          {trace.timeline.temporal_reasoning}
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {/* Copy / Speak Controls */}
                <div className="flex items-center justify-end space-x-2 pt-1">
                  <button
                    onClick={() => handleSpeakText(msg.text)}
                    className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                    title="Read Aloud"
                  >
                    {isSpeaking ? <VolumeX className="w-3.5 h-3.5 text-cyan-400" /> : <Volume2 className="w-3.5 h-3.5" />}
                  </button>
                  <button
                    onClick={() => handleCopyText(msg.id, msg.text)}
                    className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                    title="Copy Answer"
                  >
                    {copiedId === msg.id ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>
            </div>
          );
        })}

        {chatLoading && (
          <div className="flex justify-start">
            <div className="rounded-3xl p-3 bg-[#081b2e] border border-slate-800 text-slate-300 text-xs flex items-center space-x-2">
              <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
              <span>Coordinating 11 specialized marine agents across GIS, ocean physics, and safety guardrails...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Voice-to-Text Live Listening Indicator */}
      {isListening && (
        <div className="flex items-center justify-between px-4 py-2.5 bg-gradient-to-r from-red-950/90 via-slate-900 to-blue-950/90 border border-red-500/40 rounded-2xl animate-pulse text-xs text-red-200 shadow-xl backdrop-blur-md">
          <div className="flex items-center space-x-2.5">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
            </span>
            <span className="font-bold text-white tracking-wide">Listening...</span>
            <span className="text-slate-300 hidden sm:inline">
              Speak in {VOICE_LANGUAGES.find(l => l.code === speechLang)?.label || 'any language'} (e.g. Marathi, Hindi, English)
            </span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-1 h-3 bg-red-400 rounded-full animate-bounce [animation-delay:0ms]"></span>
            <span className="w-1 h-5 bg-red-400 rounded-full animate-bounce [animation-delay:150ms]"></span>
            <span className="w-1 h-3 bg-red-400 rounded-full animate-bounce [animation-delay:300ms]"></span>
            <span className="w-1 h-6 bg-red-400 rounded-full animate-bounce [animation-delay:450ms]"></span>
            <button
              onClick={toggleListening}
              className="ml-3 px-2.5 py-1 rounded-lg bg-red-500/20 hover:bg-red-500/40 text-red-100 text-[11px] font-bold border border-red-500/50 transition-colors"
            >
              Done Speaking
            </button>
          </div>
        </div>
      )}

      {/* Voice Error Notification */}
      {speechError && (
        <div className="px-4 py-2 bg-red-950/80 border border-red-500/40 rounded-2xl text-xs text-red-300 flex items-center justify-between">
          <span>{speechError}</span>
          <button onClick={() => setSpeechError(null)} className="text-red-400 hover:text-white text-xs font-bold ml-2">✕</button>
        </div>
      )}

      {/* ChatGPT-style Input Bar with Voice-to-Text and Send Button */}
      <div className="bg-[#07192c] border border-slate-800 p-2 sm:p-2.5 rounded-full flex items-center space-x-2 shadow-2xl relative">
        {/* Language selector for Voice-to-Text */}
        <div className="relative pl-1">
          <button
            type="button"
            onClick={() => setIsLangMenuOpen(!isLangMenuOpen)}
            className="px-2.5 py-1.5 rounded-full bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-medium flex items-center space-x-1.5 border border-slate-700/60 transition-colors"
            title="Choose Voice-to-Text Language"
          >
            <span>{VOICE_LANGUAGES.find(l => l.code === speechLang)?.flag || '🌐'}</span>
            <span className="hidden sm:inline text-[11px] font-mono font-semibold">{speechLang.toUpperCase().split('-')[0]}</span>
          </button>
          
          {isLangMenuOpen && (
            <div className="absolute bottom-full mb-2 left-0 w-60 bg-slate-900 border border-slate-700 rounded-2xl p-1.5 shadow-2xl z-50 text-xs space-y-0.5">
              <div className="px-2.5 py-1 text-[10px] font-bold uppercase text-slate-400 font-mono tracking-wider">
                Voice Input Language
              </div>
              {VOICE_LANGUAGES.map(lang => (
                <button
                  key={lang.code}
                  type="button"
                  onClick={() => {
                    setSpeechLang(lang.code);
                    setIsLangMenuOpen(false);
                  }}
                  className={`w-full text-left px-2.5 py-1.5 rounded-xl flex items-center justify-between text-xs transition-colors ${
                    speechLang === lang.code
                      ? 'bg-blue-600 text-white font-bold'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  <span className="flex items-center space-x-2">
                    <span>{lang.flag}</span>
                    <span>{lang.label}</span>
                  </span>
                  {speechLang === lang.code && <Check className="w-3.5 h-3.5 text-white" />}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Text Input */}
        <input
          type="text"
          value={activeSubMode === 'chat' ? chatQuery : ragQuery}
          onChange={(e) => activeSubMode === 'chat' ? setChatQuery(e.target.value) : setRagQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              activeSubMode === 'chat' ? handleSendChat() : handleSearchRAG();
            }
          }}
          placeholder={
            isListening
              ? '🎙️ Listening... speak now...'
              : activeSubMode === 'chat'
              ? 'Ask VARUNA in English, हिन्दी, मराठी, தமிழ், తెలుగు, ಕನ್ನಡ, മലയാളം, বাংলা...'
              : 'Search INCOIS, DG Shipping circulars & regulatory notices...'
          }
          className="flex-1 bg-transparent px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none font-medium"
        />

        {/* Voice-to-Text Microphone Button (matching screenshot) */}
        <button
          type="button"
          onClick={toggleListening}
          className={`p-2 rounded-full transition-all flex items-center justify-center ${
            isListening
              ? 'bg-red-500 text-white shadow-lg shadow-red-500/50 animate-pulse scale-105'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
          title={isListening ? 'Stop listening (Voice-to-Text)' : 'Voice to Text (Click and speak query)'}
          aria-label="Voice to text"
        >
          {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
        </button>

        {/* Circular Blue Send Button (matching screenshot) */}
        <button
          type="button"
          onClick={() => activeSubMode === 'chat' ? handleSendChat() : handleSearchRAG()}
          disabled={chatLoading || ragLoading || (!chatQuery.trim() && activeSubMode === 'chat') || (!ragQuery.trim() && activeSubMode === 'rag')}
          className="w-10 h-10 rounded-full bg-[#0084ff] hover:bg-[#0073e6] active:scale-95 text-white flex items-center justify-center transition-all shadow-md shadow-blue-500/30 flex-shrink-0 disabled:opacity-40 disabled:hover:bg-[#0084ff]"
          title="Send Query"
          aria-label="Send Query"
        >
          {chatLoading || ragLoading ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <ArrowRight className="w-5 h-5 stroke-[2.5]" />
          )}
        </button>
      </div>
    </div>
  );
};
