import React from 'react';
import {
  MapPin, Wind, Waves, Fish, ShieldCheck, Anchor, Thermometer,
  Droplets, Navigation, Activity, Layers, ArrowUpRight, Cpu, Radio
} from 'lucide-react';
import { RiskAssessmentResponse, FishingZone, CycloneDetails, RouteComparisonResponse } from '../types';
import { MarineMap } from './MarineMap';
import { GLOBAL_MARINE_LOCATIONS } from '../data/globalMarineLocations';

interface OverviewDashboardProps {
  assessment: RiskAssessmentResponse | null;
  fishingData: FishingZone | null;
  cycloneData: CycloneDetails | null;
  routeData: RouteComparisonResponse | null;
  loading: boolean;
  lat: number;
  lon: number;
  selectedRegion: string;
  activePersona: string;
  onSelectLocation: (lat: number, lon: number) => void;
  onOpenFullMap: () => void;
}

const getRiskColor = (level?: string) => {
  if (level === 'LOW') return { text: 'text-emerald-400', bg: 'bg-emerald-500/15', border: 'border-emerald-500/30', bar: 'bg-emerald-400' };
  if (level === 'MODERATE') return { text: 'text-amber-400', bg: 'bg-amber-500/15', border: 'border-amber-500/30', bar: 'bg-amber-400' };
  if (level === 'HIGH') return { text: 'text-orange-400', bg: 'bg-orange-500/15', border: 'border-orange-500/30', bar: 'bg-orange-400' };
  if (level === 'CRITICAL') return { text: 'text-red-400', bg: 'bg-red-500/15', border: 'border-red-500/30', bar: 'bg-red-400' };
  return { text: 'text-sky-300', bg: 'bg-sky-500/15', border: 'border-sky-500/30', bar: 'bg-sky-400' };
};

const WindDir: { [k: number]: string } = { 0: 'N', 45: 'NE', 90: 'E', 135: 'SE', 180: 'S', 225: 'SW', 270: 'W', 315: 'NW', 360: 'N' };
const getWindDir = (deg?: number) => {
  if (deg == null) return '—';
  const dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
  return dirs[Math.round(deg / 22.5) % 16];
};

export const OverviewDashboard: React.FC<OverviewDashboardProps> = ({
  assessment, fishingData, cycloneData, routeData, loading, lat, lon,
  selectedRegion, activePersona, onSelectLocation, onOpenFullMap
}) => {
  const locationData = GLOBAL_MARINE_LOCATIONS.find(l => l.id === selectedRegion) || GLOBAL_MARINE_LOCATIONS[0];
  const fused = assessment?.fused_record;
  const risk = assessment;
  const riskColors = getRiskColor(risk?.risk_level);

  const personaBadgeColors: Record<string, string> = {
    Fisherman: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
    Shipping: 'bg-sky-500/20 text-sky-300 border-sky-500/30',
    Disaster: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    Researcher: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
    Admin: 'bg-white/20 text-white border-white/30',
  };

  return (
    <div className="space-y-5 pb-6">
      {/* ── Location Header ─────────────────────────────────────── */}
      <div
        className="rounded-2xl p-5 sm:p-6"
        style={{ background: '#ffffff', border: '1px solid rgba(37,99,235,0.14)', boxShadow: '0 2px 16px rgba(29,78,216,0.07)' }}
      >
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="space-y-1">
            {/* Location tag */}
            <div className="flex items-center space-x-2 text-[11px] font-mono font-bold text-blue-400 uppercase tracking-widest">
              <MapPin className="w-3.5 h-3.5" />
              <span>{locationData.regionTag}</span>
            </div>
            {/* Big title */}
            <h1 className="text-2xl sm:text-3xl font-black text-blue-900 tracking-tight">
              {locationData.name}
              <span className="text-base font-semibold text-blue-400 ml-2">Marine Intelligence</span>
            </h1>
            <p className="text-xs text-slate-500 font-medium">
              Coordinates: {lat.toFixed(4)}°N, {lon.toFixed(4)}°E
              &nbsp;•&nbsp;{locationData.description.split('.')[0]}.
            </p>
          </div>

          {/* Right badges */}
          <div className="flex flex-wrap items-center gap-2">
            <span className={`px-2.5 py-1 rounded-lg text-[11px] font-bold border ${personaBadgeColors[activePersona] || 'bg-white/10 text-white border-white/20'}`}>
              {activePersona} Decision Support
            </span>
            <span className="px-2.5 py-1 rounded-lg text-[11px] font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              <span>INCOIS &amp; IMD Telemetry Active</span>
            </span>
            <span className="text-[11px] text-slate-500 font-mono">
              {new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })}
            </span>
          </div>
        </div>
      </div>

      {/* ── 4 KPI Metric Cards ──────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Operational Risk */}
        <div className="rounded-2xl p-4 space-y-3" style={{ background: '#ffffff', border: '1px solid rgba(37,99,235,0.14)', boxShadow: '0 2px 12px rgba(29,78,216,0.06)' }}>
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-blue-400">Operational Risk</span>
            <ShieldCheck className="w-4 h-4 text-blue-300" />
          </div>
          {loading || !risk ? (
            <div className="h-8 bg-white/10 rounded animate-pulse" />
          ) : (
            <>
              <div className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold ${riskColors.bg} ${riskColors.text} ${riskColors.border} border`}>
                {risk.risk_level} ({Math.round(risk.risk_score)}/100)
              </div>
              <div className="text-2xl font-black text-blue-900">
                {risk.risk_level === 'LOW' ? 'Ops Feasible' :
                 risk.risk_level === 'MODERATE' ? 'Caution' :
                 risk.risk_level === 'HIGH' ? 'Avoid Offshore' : 'Abort Mission'}
              </div>
              <p className="text-[11px] text-slate-500 leading-snug">
                {risk.recommended_action?.split('.')[0] || 'Conditions evaluated.'}
              </p>
              {/* Mini bar */}
              <div className="w-full h-1 rounded-full bg-blue-100">
                <div className={`h-1 rounded-full ${riskColors.bar} transition-all`} style={{ width: `${risk.risk_score}%` }} />
              </div>
            </>
          )}
        </div>

        {/* Card 2: Sig Wave Height */}
        <div className="rounded-2xl p-4 space-y-3" style={{ background: '#ffffff', border: '1px solid rgba(37,99,235,0.14)', boxShadow: '0 2px 12px rgba(29,78,216,0.06)' }}>
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-blue-400">Sig Wave Height</span>
            <Waves className="w-4 h-4 text-blue-300" />
          </div>
          {loading || !fused ? (
            <div className="h-8 bg-white/10 rounded animate-pulse" />
          ) : (
            <>
              <div className="text-sky-600 text-[11px] font-bold font-mono">
                Period {fused.wave_period?.toFixed(1) ?? '—'}s
              </div>
              <div className="text-2xl font-black text-blue-900">
                {fused.wave_height?.toFixed(2) ?? locationData.baselineWave} <span className="text-base font-semibold text-slate-400">m</span>
              </div>
              <p className="text-[11px] text-slate-500 leading-snug">
                Swell {fused.swell_height?.toFixed(2) ?? '—'}m &bull; Dir {getWindDir(fused.wave_direction)}
              </p>
              <div className="text-[10px] text-white/30 font-mono flex items-center space-x-1">
                <Radio className="w-3 h-3" /><span>INCOIS Ocean State Forecast</span>
              </div>
            </>
          )}
        </div>

        {/* Card 3: Surface Wind */}
        <div className="rounded-2xl p-4 space-y-3" style={{ background: '#ffffff', border: '1px solid rgba(37,99,235,0.14)', boxShadow: '0 2px 12px rgba(29,78,216,0.06)' }}>
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-blue-400">Surface Wind</span>
            <Wind className="w-4 h-4 text-blue-300" />
          </div>
          {loading || !fused ? (
            <div className="h-8 bg-white/10 rounded animate-pulse" />
          ) : (
            <>
              <div className="text-purple-300 text-[11px] font-bold font-mono">
                {getWindDir(fused.wind_direction)} ({fused.wind_direction?.toFixed(0) ?? '—'}°)
              </div>
              <div className="text-2xl font-black text-blue-900">
                {fused.wind_speed?.toFixed(2) ?? locationData.baselineWind}{' '}
                <span className="text-base font-semibold text-slate-400">m/s</span>
                <span className="text-sm text-purple-500 ml-2 font-mono">({((fused.wind_speed ?? 0) * 1.944).toFixed(1)} kts)</span>
              </div>
              <p className="text-[11px] text-slate-500">Temp: {fused.sst?.toFixed(1) ?? locationData.baselineSST}°C SST</p>
              <div className="text-[10px] text-slate-400 font-mono flex items-center space-x-1">
                <Radio className="w-3 h-3" /><span>IMD Coastal Weather Station</span>
              </div>
            </>
          )}
        </div>

        {/* Card 4: Nearest PFZ */}
        <div className="rounded-2xl p-4 space-y-3" style={{ background: '#ffffff', border: '1px solid rgba(37,99,235,0.14)', boxShadow: '0 2px 12px rgba(29,78,216,0.06)' }}>
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-blue-400">Nearest PFZ</span>
            <Fish className="w-4 h-4 text-blue-300" />
          </div>
          {!fishingData ? (
            <div className="h-8 bg-white/10 rounded animate-pulse" />
          ) : (
            <>
              <div className="text-emerald-300 text-[11px] font-bold font-mono">
                Confidence {Math.round((fishingData.confidence ?? 0.85) * 100)}%
              </div>
              <div className="text-2xl font-black text-blue-900">
                {fishingData.radius_km?.toFixed(1) ?? '—'}{' '}
                <span className="text-base font-semibold text-slate-400">km</span>
                <span className="text-sm text-slate-400 ml-2">radius</span>
              </div>
              <p className="text-[11px] text-slate-500 leading-snug">
                Species: {fishingData.recommended_target_species?.slice(0, 2).join(', ') || locationData.keyTargetSpecies.slice(0,2).join(', ')}
              </p>
              <div className="text-[10px] text-slate-400 font-mono flex items-center space-x-1">
                <Radio className="w-3 h-3" /><span>INCOIS Satellite Advisory</span>
              </div>
            </>
          )}
        </div>
      </div>

      {/* ── Split: Map + Telemetry ───────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        {/* Left: Mini Map */}
        <div className="lg:col-span-3 rounded-2xl overflow-hidden" style={{ border: '1px solid rgba(37,99,235,0.14)', boxShadow: '0 2px 16px rgba(29,78,216,0.07)', minHeight: 380 }}>
          {/* Map header */}
          <div className="px-4 py-3 flex items-center justify-between" style={{ background: '#f0f6ff', borderBottom: '1px solid rgba(37,99,235,0.12)' }}>
            <div>
              <div className="flex items-center space-x-2 text-xs font-bold text-blue-900">
                <Layers className="w-4 h-4 text-blue-500" />
                <span>Live Marine Situation Map — {locationData.name.split(' ')[0]}</span>
              </div>
              <p className="text-[10px] text-slate-400 mt-0.5">Interactive GIS layer with PFZ, Risk Corridors &amp; Marine Protected Areas</p>
            </div>
            <button
              onClick={onOpenFullMap}
              className="flex items-center space-x-1.5 text-[11px] font-bold text-blue-600 hover:text-blue-800 transition-colors"
            >
              <span>Full Map</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
          <div style={{ height: 340 }}>
            <MarineMap
              centerLat={lat}
              centerLon={lon}
              onSelectLocation={onSelectLocation}
              cycloneData={cycloneData}
              fishingData={fishingData}
              riskScore={assessment?.risk_score ?? 0}
            />
          </div>
        </div>

        {/* Right: Oceanographic Telemetry */}
        <div className="lg:col-span-2 rounded-2xl p-4 space-y-4" style={{ background: '#ffffff', border: '1px solid rgba(37,99,235,0.14)', boxShadow: '0 2px 16px rgba(29,78,216,0.07)' }}>
          {/* Header */}
          <div className="flex items-center justify-between pb-3" style={{ borderBottom: '1px solid rgba(37,99,235,0.10)' }}>
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-blue-500" />
              <span className="text-xs font-bold text-blue-900">Detailed Oceanographic Telemetry</span>
            </div>
            <button className="text-[11px] font-bold text-blue-500 hover:text-blue-700 transition-colors flex items-center space-x-1">
              <span>View Charts</span>
              <ArrowUpRight className="w-3 h-3" />
            </button>
          </div>

          {loading || !fused ? (
            <div className="space-y-3">
              {[1,2,3,4].map(i => <div key={i} className="h-14 bg-blue-100 rounded-xl animate-pulse" />)}
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-3">
              {/* SST */}
              <div className="rounded-xl p-3 space-y-1" style={{ background: '#eff6ff', border: '1px solid rgba(37,99,235,0.12)' }}>
                <div className="flex items-center space-x-1.5 text-[10px] text-blue-400">
                  <Thermometer className="w-3 h-3" />
                  <span>Sea Surface Temp</span>
                </div>
                <div className="text-xl font-black text-blue-900">{fused.sst?.toFixed(1) ?? locationData.baselineSST}°C</div>
                <div className="text-[10px] text-emerald-600 font-mono">Open-Meteo Marine · LIVE</div>
              </div>

              {/* Surface Current */}
              <div className="rounded-xl p-3 space-y-1" style={{ background: '#eff6ff', border: '1px solid rgba(37,99,235,0.12)' }}>
                <div className="flex items-center space-x-1.5 text-[10px] text-blue-400">
                  <Navigation className="w-3 h-3" />
                  <span>Surface Current</span>
                </div>
                <div className="text-xl font-black text-blue-900">{fused.current_velocity?.toFixed(1) ?? '0.6'} <span className="text-sm text-slate-400">m/s</span></div>
                <div className="text-[10px] text-emerald-600 font-mono">Open-Meteo Marine · LIVE</div>
              </div>

              {/* Chlorophyll */}
              <div className="rounded-xl p-3 space-y-1" style={{ background: '#eff6ff', border: '1px solid rgba(37,99,235,0.12)' }}>
                <div className="flex items-center space-x-1.5 text-[10px] text-blue-400">
                  <Droplets className="w-3 h-3" />
                  <span>Chlorophyll-a</span>
                </div>
                <div className="text-xl font-black text-blue-900">{fused.chlorophyll?.toFixed(2) ?? '1.41'} <span className="text-sm text-slate-400">mg/m³</span></div>
                <div className={`text-[10px] font-mono ${fused.chlorophyll_source === 'Copernicus Marine Live' ? 'text-emerald-600' : 'text-amber-600'}`}>
                  {fused.chlorophyll_source === 'Copernicus Marine Live' ? 'Copernicus BGC · LIVE' : 'Satellite indicator · demo fallback'}
                </div>
              </div>

              {/* Mixed Layer */}
              <div className="rounded-xl p-3 space-y-1" style={{ background: '#eff6ff', border: '1px solid rgba(37,99,235,0.12)' }}>
                <div className="flex items-center space-x-1.5 text-[10px] text-blue-400">
                  <Waves className="w-3 h-3" />
                  <span>Mixed Layer Depth</span>
                </div>
                <div className="text-xl font-black text-blue-900">{fused.sea_level ? (fused.sea_level * 10 + 20).toFixed(0) : '26'} <span className="text-sm text-slate-400">m</span></div>
                <div className="text-[10px] text-amber-600 font-mono">Derived proxy · no live MLD feed</div>
              </div>

              {/* Salinity */}
              <div className="rounded-xl p-3 space-y-1" style={{ background: '#eff6ff', border: '1px solid rgba(37,99,235,0.12)' }}>
                <div className="flex items-center space-x-1.5 text-[10px] text-blue-400">
                  <Cpu className="w-3 h-3" />
                  <span>Salinity</span>
                </div>
                <div className="text-xl font-black text-blue-900">{fused.salinity?.toFixed(1) ?? '34.8'} <span className="text-sm text-slate-400">PSU</span></div>
                <div className={`text-[10px] font-mono ${fused.salinity_source === 'Copernicus Marine Live' ? 'text-emerald-600' : 'text-amber-600'}`}>
                  {fused.salinity_source === 'Copernicus Marine Live' ? 'Copernicus Physics · LIVE' : 'Model fallback · no live ARGO feed'}
                </div>
              </div>

              {/* Pressure */}
              <div className="rounded-xl p-3 space-y-1" style={{ background: '#eff6ff', border: '1px solid rgba(37,99,235,0.12)' }}>
                <div className="flex items-center space-x-1.5 text-[10px] text-blue-400">
                  <Activity className="w-3 h-3" />
                  <span>Atm Pressure</span>
                </div>
                <div className="text-xl font-black text-blue-900">{fused.pressure?.toFixed(0) ?? '1012'} <span className="text-sm text-slate-400">hPa</span></div>
                <div className="text-[10px] text-emerald-600 font-mono">Open-Meteo live weather</div>
              </div>
            </div>
          )}

          {/* Ask VARUNA Intelligence banner */}
          <div
            className="rounded-xl p-3 flex items-center justify-between cursor-pointer hover:opacity-90 transition-opacity"
            style={{ background: 'linear-gradient(135deg, #1d4ed8 0%, #0f2044 100%)', border: '1px solid rgba(255,255,255,0.20)' }}
          >
            <div className="flex items-center space-x-2.5">
              <div className="p-1.5 rounded-lg" style={{ background: 'rgba(255,255,255,0.15)' }}>
                <Anchor className="w-4 h-4 text-white" />
              </div>
              <div>
                <div className="text-xs font-bold text-white">Ask VARUNA Intelligence</div>
                <div className="text-[10px] text-white/60">Autonomous reasoning with multi-agent coordination</div>
              </div>
            </div>
            <ArrowUpRight className="w-4 h-4 text-white/60" />
          </div>
        </div>
      </div>
    </div>
  );
};
