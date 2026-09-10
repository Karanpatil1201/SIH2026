import React, { useEffect, useState } from 'react';
import {
  Anchor, LayoutDashboard, Bot, BarChart3, Fish, Map,
  Bell, Server, LogIn, LogOut, ChevronDown, Radio, Globe, LocateFixed, FileText
} from 'lucide-react';
import { PersonaType, UserResponse } from '../types';
import { GLOBAL_MARINE_LOCATIONS } from '../data/globalMarineLocations';
import { LANGUAGES, useLanguage } from '../i18n';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  activePersona: PersonaType;
  setActivePersona: (p: PersonaType) => void;
  selectedRegion: string;
  setSelectedRegion: (r: string) => void;
  user: UserResponse | null;
  onOpenLogin: () => void;
  onLogout: () => void;
  onPrintReport: () => void;
  onShowJSONAPI: () => void;
  onOpenReport: () => void;
  alertCount?: number;
}

const TABS = [
  { id: 'dashboard', label: 'Overview',       icon: LayoutDashboard },
  { id: 'safety',    label: 'Live Safety',    icon: LocateFixed, badge: 'GPS' },
  { id: 'agents',    label: 'AI Assistant',   icon: Bot,   badge: 'AI' },
  { id: 'charts',    label: 'Ocean State',    icon: BarChart3 },
  { id: 'fishing',   label: 'Fishing Zones',  icon: Fish },
  { id: 'map',       label: 'Map Explorer',   icon: Map },
  { id: 'cyclone',   label: 'Alerts',         icon: Bell },
  { id: 'sources',   label: 'Data Sources',   icon: Server },
];

const TAB_TRANSLATION_KEYS: Record<string, Parameters<ReturnType<typeof useLanguage>['t']>[0]> = {
  dashboard: 'overview', safety: 'liveSafety', agents: 'aiAssistant', charts: 'oceanState',
  fishing: 'fishingZones', map: 'mapExplorer', cyclone: 'alerts', sources: 'dataSources'
};

const PERSONAS: { role: PersonaType; label: string; emoji: string }[] = [
  { role: 'Fisherman',  label: 'Fisherman',  emoji: '🎣' },
  { role: 'Shipping',   label: 'Operator',   emoji: '🚢' },
  { role: 'Disaster',   label: 'Disaster Ops', emoji: '🌪️' },
  { role: 'Researcher', label: 'Traveler',   emoji: '🔬' },
  { role: 'Admin',      label: 'Admin',      emoji: '🛡️' },
];

export const Navbar: React.FC<NavbarProps> = ({
  activeTab, setActiveTab,
  activePersona, setActivePersona,
  selectedRegion, setSelectedRegion,
  user, onOpenLogin, onLogout,
  onPrintReport, onShowJSONAPI, onOpenReport,
  alertCount = 0,
}) => {
  const [showPersonaMenu, setShowPersonaMenu] = useState(false);
  const [showRegionMenu, setShowRegionMenu] = useState(false);
  const [showLanguageMenu, setShowLanguageMenu] = useState(false);
  const [currentTime, setCurrentTime] = useState(() => new Date());
  const { language, setLanguage, t } = useLanguage();

  useEffect(() => {
    const clock = window.setInterval(() => setCurrentTime(new Date()), 1000);
    return () => window.clearInterval(clock);
  }, []);

  const currentPersona = PERSONAS.find(p => p.role === activePersona);
  const currentLocation = GLOBAL_MARINE_LOCATIONS.find(l => l.id === selectedRegion);

  const oceans  = GLOBAL_MARINE_LOCATIONS.filter(l => l.category === 'Ocean');
  const seas    = GLOBAL_MARINE_LOCATIONS.filter(l => l.category === 'Sea');
  const beaches = GLOBAL_MARINE_LOCATIONS.filter(l => l.category === 'Beach');
  const ports   = GLOBAL_MARINE_LOCATIONS.filter(l => l.category === 'Port');

  return (
    <header className="sticky top-0 z-50" style={{ background: '#ffffff', borderBottom: '1px solid rgba(37,99,235,0.14)', boxShadow: '0 1px 20px rgba(29,78,216,0.08)' }}>
      {/* ── Top Bar ──────────────────────────────────────────────── */}
      <div className="px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between gap-4">

        {/* Logo */}
        <div className="flex items-center space-x-3 shrink-0">
          <div className="p-2 rounded-xl" style={{ background: 'linear-gradient(135deg, #2563eb, #1d4ed8)', border: '1px solid rgba(37,99,235,0.40)' }}>
            <Anchor className="w-5 h-5 text-white stroke-[2.5]" />
          </div>
          <div>
            <div className="font-black text-lg tracking-wider text-blue-900 leading-none">VARUNA</div>
            <div className="text-[10px] text-blue-400 font-medium">{t('marineIntelligence')}</div>
          </div>
        </div>

        {/* Center: Location selector */}
        <div className="hidden md:flex items-center relative">
          <button
            onClick={() => { setShowRegionMenu(v => !v); setShowPersonaMenu(false); }}
            className="flex items-center space-x-2 px-3 py-1.5 rounded-xl text-xs font-bold text-blue-700 hover:text-blue-900 transition-all"
            style={{ background: '#eff6ff', border: '1px solid rgba(37,99,235,0.20)' }}
          >
            <Globe className="w-3.5 h-3.5 text-blue-500" />
            <span className="max-w-[160px] truncate text-blue-800">{currentLocation?.name ?? t('selectRegion')}</span>
            <ChevronDown className={`w-3.5 h-3.5 transition-transform ${showRegionMenu ? 'rotate-180' : ''}`} />
          </button>

          {/* Region dropdown */}
          {showRegionMenu && (
            <div
              className="absolute top-full left-0 mt-1 w-64 rounded-xl py-1 shadow-2xl shadow-blue-200/60 z-50 max-h-72 overflow-y-auto"
              style={{ background: '#ffffff', border: '1px solid rgba(37,99,235,0.18)' }}
            >
              {[
                { label: '🌍 Oceans', items: oceans },
                { label: '⚓ Seas & Gulfs', items: seas },
                { label: '🏖️ Beaches', items: beaches },
                { label: '🚢 Ports', items: ports },
              ].map(group => (
                <div key={group.label}>
                  <div className="px-3 pt-2 pb-1 text-[9px] font-mono font-bold uppercase tracking-widest text-blue-400">{group.label}</div>
                  {group.items.map(loc => (
                    <button
                      key={loc.id}
                      onClick={() => { setSelectedRegion(loc.id); setShowRegionMenu(false); }}
                      className={`w-full text-left px-3 py-1.5 text-xs font-medium transition-colors ${
                        selectedRegion === loc.id ? 'text-blue-700 bg-blue-50 font-bold' : 'text-slate-600 hover:text-blue-700 hover:bg-blue-50'
                      }`}
                    >
                      {loc.name}
                    </button>
                  ))}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right controls */}
        <div className="flex items-center space-x-2 shrink-0">

          {/* Persona pills */}
          <div className="hidden lg:flex items-center space-x-1 p-1 rounded-xl" style={{ background: '#eff6ff', border: '1px solid rgba(37,99,235,0.15)' }}>
            {PERSONAS.slice(0, 3).map(p => (
              <button
                key={p.role}
                onClick={() => setActivePersona(p.role)}
                className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all flex items-center space-x-1 ${
                  activePersona === p.role
                    ? 'bg-blue-600 text-white shadow-sm shadow-blue-300'
                    : 'text-blue-500 hover:text-blue-700 hover:bg-blue-100'
                }`}
              >
                <span>{p.emoji}</span>
                <span>{p.label}</span>
              </button>
            ))}

            {/* More personas dropdown */}
            <div className="relative">
              <button
                onClick={() => { setShowPersonaMenu(v => !v); setShowRegionMenu(false); }}
                className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all flex items-center space-x-1 ${
                  ['Disaster','Researcher','Admin'].includes(activePersona)
                    ? 'bg-blue-600 text-white'
                    : 'text-blue-500 hover:text-blue-700 hover:bg-blue-100'
                }`}
              >
                <span>More</span>
                <ChevronDown className="w-3 h-3" />
              </button>
              {showPersonaMenu && (
                <div
                  className="absolute top-full right-0 mt-1 w-40 rounded-xl py-1 shadow-2xl shadow-blue-200/60 z-50"
                  style={{ background: '#ffffff', border: '1px solid rgba(37,99,235,0.18)' }}
                >
                  {PERSONAS.slice(2).map(p => (
                    <button
                      key={p.role}
                      onClick={() => { setActivePersona(p.role); setShowPersonaMenu(false); }}
                      className={`w-full text-left px-3 py-1.5 text-xs font-medium flex items-center space-x-2 transition-colors ${
                        activePersona === p.role ? 'text-blue-700 bg-blue-50 font-bold' : 'text-slate-600 hover:text-blue-700 hover:bg-blue-50'
                      }`}
                    >
                      <span>{p.emoji}</span>
                      <span>{p.label}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Generate Report Button */}
          <button
            onClick={onOpenReport}
            className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-white hover:opacity-90 transition-all"
            style={{ background: 'linear-gradient(135deg,#2563eb,#1d4ed8)', border: '1px solid #1d4ed8', boxShadow: '0 2px 10px rgba(37,99,235,0.30)' }}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Report</span>
          </button>

          {/* Live Telemetry badge */}
          <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg text-[11px] font-bold text-emerald-700"
               style={{ background: 'rgba(16, 185, 129, 0.10)', border: '1px solid rgba(16, 185, 129, 0.30)' }}>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
            <Radio className="w-3 h-3" />
            <span>LIVE TELEMETRY</span>
          </div>

          <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-blue-50 border border-blue-200 text-blue-800 font-mono text-[11px] font-bold tabular-nums" title="Current UTC time">
            <span className="text-blue-500">{t('utc')}</span>
            <span>{currentTime.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })}</span>
          </div>

          <div className="relative">
            <button
              onClick={() => { setShowLanguageMenu(value => !value); setShowRegionMenu(false); setShowPersonaMenu(false); }}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-blue-50 border border-blue-200 text-blue-800 text-[11px] font-bold"
              aria-label="Choose dashboard language"
            >
              <Globe className="w-3.5 h-3.5 text-blue-500" />
              <span>{LANGUAGES.find(item => item.code === language)?.nativeLabel}</span>
              <ChevronDown className="w-3 h-3" />
            </button>
            {showLanguageMenu && (
              <div className="absolute right-0 top-full mt-1 w-48 rounded-xl bg-white border border-blue-200 shadow-xl z-50 py-1">
                {LANGUAGES.map(item => (
                  <button
                    key={item.code}
                    onClick={() => { setLanguage(item.code); setShowLanguageMenu(false); }}
                    className={`w-full text-left px-3 py-2 text-xs transition-colors ${language === item.code ? 'bg-blue-50 text-blue-700 font-bold' : 'text-slate-700 hover:bg-blue-50'}`}
                  >
                    {item.nativeLabel} <span className="text-slate-400">({item.label})</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Auth */}
          {user ? (
            <div className="flex items-center space-x-1.5 pl-2 pr-1 py-1 rounded-xl text-xs"
                 style={{ background: '#eff6ff', border: '1px solid rgba(37,99,235,0.20)' }}>
              <div className="w-6 h-6 rounded-full font-black text-[11px] flex items-center justify-center text-white"
                   style={{ background: '#2563eb' }}>
                {user.username.charAt(0).toUpperCase()}
              </div>
              <span className="hidden md:block text-blue-700 font-medium max-w-[80px] truncate">{user.username}</span>
              <button onClick={onLogout} className="p-1 text-blue-300 hover:text-red-500 transition-colors">
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenLogin}
              className="px-3 py-1.5 rounded-xl text-xs font-bold text-white hover:opacity-90 transition-all flex items-center space-x-1.5"
              style={{ background: '#2563eb', border: '1px solid #1d4ed8' }}
            >
              <LogIn className="w-3.5 h-3.5" />
              <span>{t('signIn')}</span>
            </button>
          )}
        </div>
      </div>

      {/* ── Tab Bar ──────────────────────────────────────────────── */}
      <div className="px-4 sm:px-6 lg:px-8 overflow-x-auto" style={{ borderTop: '1px solid rgba(37,99,235,0.10)' }}>
        <nav className="flex items-center space-x-1 py-2 min-w-max">
          {TABS.map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-[12px] font-semibold whitespace-nowrap transition-all relative ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-200'
                    : 'text-slate-500 hover:text-blue-700 hover:bg-blue-50'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-white' : 'text-blue-400'}`} />
                <span>{t(TAB_TRANSLATION_KEYS[tab.id] ?? 'overview')}</span>
                {tab.badge && (
                  <span className={`text-[9px] font-black px-1 rounded ${isActive ? 'bg-white/20 text-white' : 'bg-blue-100 text-blue-600'}`}>
                    {tab.badge}
                  </span>
                )}
                {tab.id === 'cyclone' && alertCount > 0 && (
                  <span className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full bg-red-500 text-white text-[9px] font-black flex items-center justify-center">
                    {alertCount}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
