import React from 'react';
import {
  LayoutDashboard, Bot, Map, LineChart, HelpCircle, Server,
  History, Anchor, ChevronRight, Code2, Printer, User, LogIn, LogOut,
  Sparkles, Layers, ShieldAlert, Fish, Flame, Navigation2
} from 'lucide-react';
import { PersonaType, UserResponse } from '../types';

import { GLOBAL_MARINE_LOCATIONS, GlobalMarineLocation } from '../data/globalMarineLocations';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  selectedRegion: string;
  setSelectedRegion: (region: string) => void;
  activePersona: PersonaType;
  setActivePersona: (persona: PersonaType) => void;
  user: UserResponse | null;
  onOpenLogin: () => void;
  onLogout: () => void;
  onPrintReport: () => void;
  onShowJSONAPI: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  selectedRegion,
  setSelectedRegion,
  activePersona,
  setActivePersona,
  user,
  onOpenLogin,
  onLogout,
  onPrintReport,
  onShowJSONAPI
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Executive Dashboard', icon: LayoutDashboard },
    { id: 'agents', label: 'Multi-Agent Architecture', icon: Bot },
    { id: 'map', label: 'Interactive Ocean Map', icon: Map },
    { id: 'routes', label: 'Route Pathfinder', icon: Navigation2 },
    { id: 'fishing', label: 'Fishing (PFZ) Advisory', icon: Fish },
    { id: 'cyclone', label: 'Cyclone & Anomalies', icon: Flame },
    { id: 'charts', label: 'Ocean Trend Charts', icon: LineChart },
    { id: 'why', label: 'Why VARUNA Said This', icon: HelpCircle },
    { id: 'sources', label: 'Information Sources', icon: Server },
    { id: 'twin', label: 'Digital Twin Simulator', icon: Layers },
    { id: 'ecosystem', label: 'Ecosystem Intelligence', icon: Sparkles },
  ];

  const personas: { role: PersonaType; label: string; emoji: string }[] = [
    { role: 'Fisherman', label: 'Fisherman', emoji: '🎣' },
    { role: 'Shipping', label: 'Shipping', emoji: '🚢' },
    { role: 'Disaster', label: 'Disaster Ops', emoji: '🌪️' },
    { role: 'Researcher', label: 'Researcher', emoji: '🔬' },
    { role: 'Admin', label: 'Admin', emoji: '🛡️' },
  ];

  // Group locations
  const oceans = GLOBAL_MARINE_LOCATIONS.filter(l => l.category === 'Ocean');
  const seas = GLOBAL_MARINE_LOCATIONS.filter(l => l.category === 'Sea');
  const beaches = GLOBAL_MARINE_LOCATIONS.filter(l => l.category === 'Beach');
  const ports = GLOBAL_MARINE_LOCATIONS.filter(l => l.category === 'Port');

  return (
    <aside className="w-64 bg-[#071428] border-r border-white/10 flex flex-col h-screen sticky top-0 shrink-0 select-none text-[#f0f6ff] z-40 overflow-y-auto shadow-2xl shadow-black/60">
      {/* Brand Header */}
      <div className="p-5 border-b border-white/10 flex items-center space-x-3" style={{background: 'linear-gradient(135deg, #0d1f3e 0%, #112b54 100%)'}}>
        <div className="p-2.5 rounded-xl shadow-lg" style={{background: 'rgba(255,255,255,0.12)', border: '1px solid rgba(255,255,255,0.20)'}}>
          <Anchor className="w-6 h-6 stroke-[2.5] text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-1.5">
            <span className="font-black text-xl tracking-wider text-white">VARUNA</span>
            <span className="text-[9px] font-mono px-1.5 py-0.5 rounded font-bold" style={{background: 'rgba(255,255,255,0.15)', color: 'rgba(255,255,255,0.90)', border: '1px solid rgba(255,255,255,0.25)'}}>
              GLOBAL
            </span>
          </div>
          <p className="text-[10px] text-white/60 font-medium tracking-tight">World Marine Intelligence</p>
        </div>
      </div>

      {/* Main Vertical Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        <div className="px-3 pb-2 text-[10px] font-mono font-bold uppercase tracking-wider text-white/40">
          Navigation Menu
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-bold transition-all ${
                isActive
                  ? 'bg-white text-[#071428] shadow-lg shadow-black/30'
                  : 'text-white/60 hover:text-white hover:bg-white/10'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-[#071428]' : 'text-sky-400'}`} />
                <span>{item.label}</span>
              </div>
              {isActive && <ChevronRight className="w-3.5 h-3.5 text-white" />}
            </button>
          );
        })}

        {/* Persona Selector */}
        <div className="pt-4 px-3 pb-2 text-[10px] font-mono font-bold uppercase tracking-wider text-white/30 border-t border-white/10 mt-4">
          Persona View Mode
        </div>
        <div className="grid grid-cols-2 gap-1.5 px-1">
          {personas.map((p) => {
            const isActive = activePersona === p.role;
            return (
              <button
                key={p.role}
                onClick={() => setActivePersona(p.role)}
                className={`py-1.5 px-2 rounded-lg text-[11px] font-medium flex items-center space-x-1 transition-all ${
                  isActive
                    ? 'bg-white/20 text-white border border-white/30 font-bold shadow-sm'
                    : 'text-white/50 hover:text-white hover:bg-white/10'
                }`}
              >
                <span>{p.emoji}</span>
                <span className="truncate">{p.label}</span>
              </button>
            );
          })}
        </div>
      </nav>

      {/* Selected Global Ocean & Beach Control Card */}
      <div className="p-3 border-t border-white/10 space-y-3 bg-[#0d1f3e]/60">
        <div>
          <label className="block text-[10px] font-mono font-bold uppercase tracking-wider text-white/40 mb-1">
            Global Sea / Beach / Port Location
          </label>
          <select
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
            className="w-full bg-white/10 border border-white/15 text-white text-xs font-bold rounded-lg p-2 focus:outline-none focus:border-white/40"
          >
            <optgroup label="🌍 Oceans (Global)">
              {oceans.map((o) => (
                <option key={o.id} value={o.id}>
                  🌊 {o.name}
                </option>
              ))}
            </optgroup>
            <optgroup label="⚓ Major Seas & Gulfs">
              {seas.map((s) => (
                <option key={s.id} value={s.id}>
                  ⛵ {s.name}
                </option>
              ))}
            </optgroup>
            <optgroup label="🏖️ Famous Beaches & Coasts">
              {beaches.map((b) => (
                <option key={b.id} value={b.id}>
                  🏝️ {b.name}
                </option>
              ))}
            </optgroup>
            <optgroup label="🚢 International Shipping Ports">
              {ports.map((p) => (
                <option key={p.id} value={p.id}>
                  ⚓ {p.name}
                </option>
              ))}
            </optgroup>
          </select>
        </div>

        {/* VARUNA IS READY Banner */}
        <div className="p-2.5 rounded-xl text-xs space-y-1" style={{background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.14)'}}>
          <div className="flex items-center space-x-1.5 text-white font-extrabold text-[11px]">
            <span className="w-2 h-2 rounded-full bg-white animate-ping" />
            <span>VARUNA IS READY</span>
          </div>
          <p className="text-[10px] text-white/45 leading-tight">
            Multi-agent ecosystem analysis for 5 Earth ocean basins active.
          </p>
        </div>

        {/* Quick Action Buttons */}
        <div className="flex items-center gap-1.5 pt-1">
          <button
            onClick={onPrintReport}
            className="flex-1 py-1.5 px-2 rounded-lg text-[11px] font-semibold text-white/70 hover:text-white flex items-center justify-center space-x-1 transition-all" style={{background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.12)'}}
          >
            <Printer className="w-3.5 h-3.5 text-white/60" />
            <span>Report</span>
          </button>
          <button
            onClick={onShowJSONAPI}
            className="flex-1 py-1.5 px-2 rounded-lg text-[11px] font-semibold text-white/70 hover:text-white flex items-center justify-center space-x-1 transition-all" style={{background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.12)'}}
          >
            <Code2 className="w-3.5 h-3.5 text-sky-300" />
            <span>JSON API</span>
          </button>
        </div>

        {/* User Profile / Auth Control */}
        <div className="pt-2 border-t border-white/10">
          {user ? (
            <div className="flex items-center justify-between p-2 rounded-xl" style={{background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.12)'}}>
              <div className="flex items-center space-x-2 truncate">
                <div className="w-7 h-7 rounded-full font-bold flex items-center justify-center text-xs" style={{background: 'rgba(255,255,255,0.18)', color: '#fff', border: '1px solid rgba(255,255,255,0.30)'}}>
                  {user.username.charAt(0).toUpperCase()}
                </div>
                <div className="truncate text-left">
                  <div className="font-bold text-xs text-white truncate">{user.username}</div>
                  <div className="text-[10px] text-sky-300 font-mono">{user.role}</div>
                </div>
              </div>
              <button
                onClick={onLogout}
                title="Sign Out"
                className="p-1 text-white/40 hover:text-red-400 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenLogin}
              className="w-full py-2 rounded-xl font-bold text-xs flex items-center justify-center space-x-2 transition-all text-white hover:bg-white/20" style={{background: 'rgba(255,255,255,0.12)', border: '1px solid rgba(255,255,255,0.22)'}}
            >
              <LogIn className="w-4 h-4" />
              <span>Sign In / Register</span>
            </button>
          )}
        </div>
      </div>
    </aside>
  );
};
