import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  MapPin, Navigation, Shield, AlertTriangle, CheckCircle2, XCircle,
  Crosshair, RefreshCw, Radio, Zap, ArrowRight, Wind, Waves,
  Thermometer, Activity, LocateFixed, Eye, ChevronRight, Clock,
  TrendingUp, AlertCircle, Info, FileText, Anchor
} from 'lucide-react';
import { varunaAPI } from '../services/api';
import { RiskAssessmentResponse } from '../types';
import { LiveTrackingMap } from './LiveTrackingMap';

// ─── Types ────────────────────────────────────────────────────────────────────
interface GeoPoint { lat: number; lon: number; }
interface DirectionalScan {
  direction: string;
  label: string;
  lat: number;
  lon: number;
  risk?: RiskAssessmentResponse;
  loading: boolean;
  error?: string;
  riskScore?: number;
  riskLevel?: string;
}
type SafetyStatus = 'SAFE' | 'CAUTION' | 'DANGER' | 'CRITICAL' | 'LOADING' | 'IDLE';

// ─── Constants ────────────────────────────────────────────────────────────────
const SCAN_RADIUS_DEG = 0.5; // ~55 km
const SCAN_DIRECTIONS = [
  { direction: 'N',  label: 'North',     dlat: +1, dlon:  0 },
  { direction: 'NE', label: 'NE',        dlat: +1, dlon: +1 },
  { direction: 'E',  label: 'East',      dlat:  0, dlon: +1 },
  { direction: 'SE', label: 'SE',        dlat: -1, dlon: +1 },
  { direction: 'S',  label: 'South',     dlat: -1, dlon:  0 },
  { direction: 'SW', label: 'SW',        dlat: -1, dlon: -1 },
  { direction: 'W',  label: 'West',      dlat:  0, dlon: -1 },
  { direction: 'NW', label: 'NW',        dlat: +1, dlon: -1 },
];

const getSafetyFromRisk = (level?: string): SafetyStatus => {
  if (level === 'SAFE' || level === 'LOW')      return 'SAFE';
  if (level === 'CAUTION' || level === 'MODERATE') return 'CAUTION';
  if (level === 'DANGER' || level === 'HIGH')     return 'DANGER';
  if (level === 'CRITICAL') return 'CRITICAL';
  return 'IDLE';
};

const safetyConfig: Record<SafetyStatus, { label: string; color: string; bg: string; border: string; icon: React.FC<any>; pulse: string }> = {
  SAFE:     { label: 'SAFE',     color: 'text-emerald-600', bg: 'bg-emerald-50',  border: 'border-emerald-300', icon: CheckCircle2,   pulse: 'bg-emerald-500' },
  CAUTION:  { label: 'CAUTION',  color: 'text-amber-600',   bg: 'bg-amber-50',    border: 'border-amber-300',   icon: AlertTriangle,  pulse: 'bg-amber-500' },
  DANGER:   { label: 'DANGER',   color: 'text-orange-600',  bg: 'bg-orange-50',   border: 'border-orange-300',  icon: AlertCircle,    pulse: 'bg-orange-500' },
  CRITICAL: { label: 'CRITICAL', color: 'text-red-600',     bg: 'bg-red-50',      border: 'border-red-400',     icon: XCircle,        pulse: 'bg-red-500' },
  LOADING:  { label: 'ANALYSING…', color: 'text-blue-500',  bg: 'bg-blue-50',     border: 'border-blue-200',    icon: RefreshCw,      pulse: 'bg-blue-400' },
  IDLE:     { label: 'STANDBY',  color: 'text-slate-500',   bg: 'bg-slate-50',    border: 'border-slate-200',   icon: Shield,         pulse: 'bg-slate-400' },
};

const dirRiskColor = (level?: string) => {
  if (level === 'SAFE' || level === 'LOW')      return { ring: 'ring-emerald-400', dot: 'bg-emerald-500', text: 'text-emerald-700' };
  if (level === 'CAUTION' || level === 'MODERATE') return { ring: 'ring-amber-400',   dot: 'bg-amber-500',   text: 'text-amber-700' };
  if (level === 'DANGER' || level === 'HIGH')     return { ring: 'ring-orange-400',  dot: 'bg-orange-500',  text: 'text-orange-700' };
  if (level === 'CRITICAL') return { ring: 'ring-red-400',     dot: 'bg-red-500',     text: 'text-red-700' };
  return { ring: 'ring-slate-200', dot: 'bg-slate-300', text: 'text-slate-500' };
};

export interface LiveSafetyPanelProps {
  initialLat?: number;
  initialLon?: number;
  selectedRegion?: string;
  onOpenReport?: () => void;
}

const MARINE_SECTORS = [
  { name: 'Mumbai Offshore', lat: 18.9667, lon: 72.8333, desc: 'Central Arabian Sea Corridor' },
  { name: 'Goa Coastal Waters', lat: 15.2993, lon: 73.7500, desc: 'West Coast Shelf Zone' },
  { name: 'Chennai / Bay of Bengal', lat: 13.0827, lon: 80.2707, desc: 'Coromandel Deep Waters' },
  { name: 'Kochi Deep Sea', lat: 9.9312, lon: 76.2673, desc: 'High Pelagic Catch Sector' },
  { name: 'Gujarat Gulf of Khambhat', lat: 21.1702, lon: 72.8311, desc: 'High Tidal Energy Shelf' },
  { name: 'Lakshadweep Archipelago', lat: 10.5667, lon: 72.6417, desc: 'Deep Oceanic Coral Shelf' },
];

// ─── Component ────────────────────────────────────────────────────────────────
export const LiveSafetyPanel: React.FC<LiveSafetyPanelProps> = ({
  initialLat = 18.9667,
  initialLon = 72.8333,
  selectedRegion,
  onOpenReport
}) => {
  // Mode: 'sector' (fast marine presets) | 'manual' (custom coordinates) | 'live' (device GPS)
  const [gpsMode, setGpsMode] = useState<'sector' | 'manual' | 'live'>('sector');
  const [gpsStatus, setGpsStatus] = useState<'idle' | 'requesting' | 'tracking' | 'error'>('idle');
  const [gpsError, setGpsError] = useState<string>('');
  const [livePos, setLivePos] = useState<GeoPoint | null>(null);
  const [accuracy, setAccuracy] = useState<number | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // Manual input
  const [manualLat, setManualLat] = useState<string>(String(initialLat));
  const [manualLon, setManualLon] = useState<string>(String(initialLon));
  const [manualError, setManualError] = useState<string>('');

  // Analysis state — default to valid marine sector immediately
  const [analysisPos, setAnalysisPos] = useState<GeoPoint>({ lat: initialLat, lon: initialLon });
  const [currentRisk, setCurrentRisk] = useState<RiskAssessmentResponse | null>(null);
  const [safetyStatus, setSafetyStatus] = useState<SafetyStatus>('IDLE');
  const [loadingCurrent, setLoadingCurrent] = useState(false);

  // Directional scan
  const [dirScans, setDirScans] = useState<DirectionalScan[]>(
    SCAN_DIRECTIONS.map(d => ({ direction: d.direction, label: d.label, lat: 0, lon: 0, loading: false }))
  );
  const [scanningDir, setScanningDir] = useState(false);

  // Smart alerts derived
  const [smartAlerts, setSmartAlerts] = useState<{ dir: string; level: string; msg: string }[]>([]);

  const watchRef = useRef<number | null>(null);
  const autoRefreshRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Sync with initialLat/initialLon if props change
  useEffect(() => {
    if (initialLat && initialLon) {
      setAnalysisPos({ lat: initialLat, lon: initialLon });
      setManualLat(String(initialLat));
      setManualLon(String(initialLon));
    }
  }, [initialLat, initialLon]);

  // ── GPS ──
  const startTracking = useCallback(() => {
    if (!navigator.geolocation) {
      setGpsError('Geolocation is not supported by your browser.');
      setGpsStatus('error');
      return;
    }
    setGpsStatus('requesting');
    setGpsError('');

    watchRef.current = navigator.geolocation.watchPosition(
      (pos) => {
        const pt = { lat: pos.coords.latitude, lon: pos.coords.longitude };
        setLivePos(pt);
        setAccuracy(pos.coords.accuracy);
        setLastUpdated(new Date());
        setGpsStatus('tracking');
        setAnalysisPos(pt);
      },
      (err) => {
        setGpsStatus('error');
        setGpsError(err.message || 'Unable to retrieve location. Check browser permissions.');
      },
      { enableHighAccuracy: true, maximumAge: 15000, timeout: 20000 }
    );
  }, []);

  const stopTracking = useCallback(() => {
    if (watchRef.current !== null) {
      navigator.geolocation.clearWatch(watchRef.current);
      watchRef.current = null;
    }
    setGpsStatus('idle');
  }, []);

  // ── Analyse position ──
  const analysePosition = useCallback(async (pos: GeoPoint) => {
    setLoadingCurrent(true);
    setSafetyStatus('LOADING');
    try {
      const risk = await varunaAPI.getRiskAssessment(pos.lat, pos.lon);
      setCurrentRisk(risk);
      setSafetyStatus(getSafetyFromRisk(risk.risk_level));
    } catch {
      setSafetyStatus('IDLE');
    } finally {
      setLoadingCurrent(false);
    }
  }, []);

  // ── Directional scan ──
  const runDirectionalScan = useCallback(async (pos: GeoPoint) => {
    setScanningDir(true);
    const results: DirectionalScan[] = SCAN_DIRECTIONS.map(d => ({
      direction: d.direction,
      label: d.label,
      lat: pos.lat + d.dlat * SCAN_RADIUS_DEG,
      lon: pos.lon + d.dlon * SCAN_RADIUS_DEG,
      loading: true,
    }));
    setDirScans([...results]);

    const fetched = await Promise.allSettled(
      results.map(async (r) => {
        const risk = await varunaAPI.getRiskAssessment(r.lat, r.lon);
        return { ...r, risk, loading: false };
      })
    );

    const finalScans = fetched.map((res, i) =>
      res.status === 'fulfilled'
        ? { ...res.value, riskLevel: res.value.risk?.risk_level, riskScore: res.value.risk?.risk_score }
        : { ...results[i], loading: false, error: 'Failed' }
    );
    setDirScans(finalScans);

    // Build smart alerts
    const alerts = finalScans
      .filter(s => s.risk && (s.risk.risk_level === 'DANGER' || s.risk.risk_level === 'HIGH' || s.risk.risk_level === 'CRITICAL'))
      .map(s => ({
        dir: s.label,
        level: s.risk!.risk_level,
        msg: `${s.label} corridor shows ${s.risk!.risk_level} risk (score ${Math.round(s.risk!.risk_score)}/100). ${s.risk!.recommended_action?.split('.')[0] ?? ''}.`
      }));
    setSmartAlerts(alerts);
    setScanningDir(false);
  }, []);

  // Trigger analysis + scan whenever analysisPos changes
  useEffect(() => {
    if (!analysisPos) return;
    analysePosition(analysisPos);
    runDirectionalScan(analysisPos);
  }, [analysisPos, analysePosition, runDirectionalScan]);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      stopTracking();
      if (autoRefreshRef.current) clearInterval(autoRefreshRef.current);
    };
  }, [stopTracking]);

  // Auto-refresh every 60 s when tracking
  useEffect(() => {
    if (gpsStatus === 'tracking' && livePos) {
      if (autoRefreshRef.current) clearInterval(autoRefreshRef.current);
      autoRefreshRef.current = setInterval(() => {
        setLastUpdated(new Date());
        if (livePos) setAnalysisPos({ ...livePos });
      }, 60000);
    }
    return () => { if (autoRefreshRef.current) clearInterval(autoRefreshRef.current); };
  }, [gpsStatus, livePos]);

  // ── Manual submission ──
  const handleManualSubmit = () => {
    const lat = parseFloat(manualLat);
    const lon = parseFloat(manualLon);
    if (isNaN(lat) || lat < -90 || lat > 90) { setManualError('Latitude must be between -90 and 90'); return; }
    if (isNaN(lon) || lon < -180 || lon > 180) { setManualError('Longitude must be between -180 and 180'); return; }
    setManualError('');
    setAnalysisPos({ lat, lon });
  };

  const handleSelectSector = (sector: typeof MARINE_SECTORS[0]) => {
    setAnalysisPos({ lat: sector.lat, lon: sector.lon });
    setManualLat(String(sector.lat));
    setManualLon(String(sector.lon));
  };

  const cfg = safetyConfig[safetyStatus];
  const SafetyIcon = cfg.icon;

  return (
    <div className="space-y-5 pb-6">

      {/* ── Header ───────────────────────────────────────────── */}
      <div className="rounded-2xl p-5" style={{ background: '#ffffff', border: '1px solid rgba(37,99,235,0.14)', boxShadow: '0 2px 16px rgba(29,78,216,0.07)' }}>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-[11px] font-mono font-bold text-blue-500 uppercase tracking-widest mb-1">
              <Radio className="w-3.5 h-3.5 animate-pulse" />
              <span>Real-Time Marine Safety & Threat Intelligence</span>
            </div>
            <h1 className="text-2xl font-black text-blue-950">Live Location Safety Monitor</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Continuous offshore telemetry, 360° radar risk analysis, and AI lookahead threat detection.
            </p>
          </div>
          {/* Mode toggle + Report button */}
          <div className="flex items-center gap-2 flex-wrap">
            <div className="flex items-center rounded-xl p-1 space-x-1" style={{ background: '#eff6ff', border: '1px solid rgba(37,99,235,0.15)' }}>
              <button
                onClick={() => { setGpsMode('sector'); stopTracking(); }}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1.5 ${gpsMode === 'sector' ? 'bg-blue-600 text-white shadow-sm' : 'text-blue-600 hover:bg-blue-100'}`}
              >
                <Anchor className="w-3.5 h-3.5" />
                <span>Marine Sectors</span>
              </button>
              <button
                onClick={() => { setGpsMode('manual'); stopTracking(); }}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1.5 ${gpsMode === 'manual' ? 'bg-blue-600 text-white shadow-sm' : 'text-blue-600 hover:bg-blue-100'}`}
              >
                <MapPin className="w-3.5 h-3.5" />
                <span>Coordinates</span>
              </button>
              <button
                onClick={() => { setGpsMode('live'); startTracking(); }}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1.5 ${gpsMode === 'live' ? 'bg-blue-600 text-white shadow-sm' : 'text-blue-600 hover:bg-blue-100'}`}
              >
                <LocateFixed className="w-3.5 h-3.5" />
                <span>Vessel GPS</span>
              </button>
            </div>
            {/* Report button */}
            {onOpenReport && (
              <button
                onClick={onOpenReport}
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-white hover:opacity-90 transition-all"
                style={{ background: 'linear-gradient(135deg,#2563eb,#1d4ed8)', border: '1px solid #1d4ed8', boxShadow: '0 2px 10px rgba(37,99,235,0.25)' }}
              >
                <FileText className="w-3.5 h-3.5" />
                <span>Generate Report</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ── Live Tracking Map ─────────────────────────────────── */}
      <LiveTrackingMap
        lat={analysisPos?.lat ?? null}
        lon={analysisPos?.lon ?? null}
        accuracy={accuracy}
        isTracking={gpsStatus === 'tracking'}
        dirPoints={dirScans.map(s => ({
          direction: s.direction,
          lat: s.lat,
          lon: s.lon,
          riskLevel: s.risk?.risk_level ?? s.riskLevel,
          riskScore: s.risk?.risk_score ?? s.riskScore,
          loading: s.loading,
        }))}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

        {/* ── Left Column: GPS / Manual + Current Safety ───────── */}
        <div className="space-y-4">

          {/* GPS / Manual Input Card */}
          <div className="rounded-2xl p-4 space-y-3" style={{ background: '#ffffff', border: '1px solid rgba(37,99,235,0.14)', boxShadow: '0 2px 12px rgba(29,78,216,0.06)' }}>

            {gpsMode === 'sector' && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="text-[10px] font-mono font-bold uppercase tracking-widest text-blue-500">Operational Maritime Sectors</div>
                  <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-blue-100 text-blue-800">
                    6 Active Zones
                  </span>
                </div>
                <div className="space-y-2">
                  {MARINE_SECTORS.map((sector) => {
                    const isSelected = Math.abs(analysisPos.lat - sector.lat) < 0.01 && Math.abs(analysisPos.lon - sector.lon) < 0.01;
                    return (
                      <button
                        key={sector.name}
                        onClick={() => handleSelectSector(sector)}
                        className={`w-full p-2.5 rounded-xl text-left transition-all border ${
                          isSelected
                            ? 'bg-blue-50 border-blue-400 shadow-sm ring-1 ring-blue-300'
                            : 'bg-white hover:bg-slate-50 border-slate-200'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-blue-950 flex items-center space-x-1.5">
                            <Anchor className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                            <span>{sector.name}</span>
                          </span>
                          <span className="font-mono text-[10px] text-slate-400">
                            {sector.lat.toFixed(2)}°N, {sector.lon.toFixed(2)}°E
                          </span>
                        </div>
                        <div className="text-[11px] text-slate-500 mt-0.5 pl-5">
                          {sector.desc}
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {gpsMode === 'live' && (
              <>
                <div className="flex items-center justify-between">
                  <div className="text-[10px] font-mono font-bold uppercase tracking-widest text-blue-500">Vessel GPS Tracking</div>
                  {gpsStatus === 'tracking' && (
                    <span className="flex items-center space-x-1.5 text-[10px] font-bold text-emerald-600">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
                      <span>LIVE TELEMETRY</span>
                    </span>
                  )}
                </div>

                {gpsStatus === 'idle' && (
                  <div className="space-y-2">
                    <p className="text-xs text-slate-500">
                      Connect to your vessel or browser GPS hardware for continuous positional safety tracking and proximity alarms.
                    </p>
                    <button onClick={startTracking}
                      className="w-full py-3 rounded-xl text-sm font-bold text-white flex items-center justify-center space-x-2 hover:opacity-90 transition-opacity"
                      style={{ background: 'linear-gradient(135deg, #2563eb, #1d4ed8)' }}>
                      <LocateFixed className="w-4 h-4" />
                      <span>Acquire Vessel GPS</span>
                    </button>
                  </div>
                )}

                {gpsStatus === 'requesting' && (
                  <div className="flex items-center space-x-3 py-3">
                    <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />
                    <div>
                      <div className="text-sm font-bold text-blue-700">Acquiring GPS fix…</div>
                      <div className="text-[11px] text-slate-400">Allow location access in browser</div>
                    </div>
                  </div>
                )}

                {gpsStatus === 'tracking' && livePos && (
                  <div className="space-y-2.5">
                    <div className="grid grid-cols-2 gap-2">
                      <div className="rounded-xl p-2.5 text-center" style={{ background: '#eff6ff', border: '1px solid rgba(37,99,235,0.12)' }}>
                        <div className="text-[10px] text-blue-400 font-mono mb-0.5">LATITUDE</div>
                        <div className="text-sm font-black text-blue-900">{livePos.lat.toFixed(5)}°</div>
                      </div>
                      <div className="rounded-xl p-2.5 text-center" style={{ background: '#eff6ff', border: '1px solid rgba(37,99,235,0.12)' }}>
                        <div className="text-[10px] text-blue-400 font-mono mb-0.5">LONGITUDE</div>
                        <div className="text-sm font-black text-blue-900">{livePos.lon.toFixed(5)}°</div>
                      </div>
                    </div>
                    {accuracy && (
                      <div className="flex items-center space-x-1.5 text-[11px] text-slate-500">
                        <Crosshair className="w-3 h-3 text-blue-400" />
                        <span>Accuracy: ±{Math.round(accuracy)}m</span>
                      </div>
                    )}
                    {lastUpdated && (
                      <div className="flex items-center space-x-1.5 text-[11px] text-slate-500">
                        <Clock className="w-3 h-3 text-blue-400" />
                        <span>Last update: {lastUpdated.toLocaleTimeString()}</span>
                      </div>
                    )}
                    <button
                      onClick={() => livePos && setAnalysisPos({ ...livePos })}
                      className="w-full py-2 rounded-xl text-xs font-bold text-blue-700 hover:bg-blue-100 flex items-center justify-center space-x-2 transition-colors"
                      style={{ background: '#eff6ff', border: '1px solid rgba(37,99,235,0.20)' }}
                    >
                      <RefreshCw className="w-3.5 h-3.5" />
                      <span>Re-analyse Current Fix</span>
                    </button>
                  </div>
                )}

                {gpsStatus === 'error' && (
                  <div className="space-y-2">
                    <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900">
                      <div className="font-bold flex items-center space-x-1.5"><AlertTriangle className="w-3.5 h-3.5 text-amber-600" /><span>GPS Unavailable</span></div>
                      <div className="mt-1 text-amber-700">{gpsError}</div>
                    </div>
                    <button onClick={startTracking}
                      className="w-full py-2 rounded-xl text-xs font-bold text-blue-600 border border-blue-200 hover:bg-blue-50 transition-colors">
                      Retry Fix
                    </button>
                    <button onClick={() => setGpsMode('sector')}
                      className="w-full py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-50 transition-colors">
                      Switch to Marine Sectors
                    </button>
                  </div>
                )}
              </>
            )}

            {gpsMode === 'manual' && (
              <>
                <div className="text-[10px] font-mono font-bold uppercase tracking-widest text-blue-500">Custom Maritime Coordinates</div>
                <div className="space-y-2">
                  <div>
                    <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Latitude (-90 to 90)</label>
                    <input
                      type="number" step="0.0001" placeholder="e.g. 18.9667"
                      value={manualLat}
                      onChange={e => setManualLat(e.target.value)}
                      className="mt-1 w-full px-3 py-2 rounded-xl text-sm font-mono font-bold text-blue-900 outline-none transition-all"
                      style={{ background: '#eff6ff', border: '1px solid rgba(37,99,235,0.25)' }}
                    />
                  </div>
                  <div>
                    <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Longitude (-180 to 180)</label>
                    <input
                      type="number" step="0.0001" placeholder="e.g. 72.8333"
                      value={manualLon}
                      onChange={e => setManualLon(e.target.value)}
                      className="mt-1 w-full px-3 py-2 rounded-xl text-sm font-mono font-bold text-blue-900 outline-none transition-all"
                      style={{ background: '#eff6ff', border: '1px solid rgba(37,99,235,0.25)' }}
                    />
                  </div>
                  {manualError && (
                    <div className="text-xs text-red-600 font-medium flex items-center space-x-1">
                      <XCircle className="w-3.5 h-3.5" />
                      <span>{manualError}</span>
                    </div>
                  )}
                  <button
                    onClick={handleManualSubmit}
                    className="w-full py-2.5 rounded-xl text-sm font-bold text-white flex items-center justify-center space-x-2 hover:opacity-90 transition-opacity"
                    style={{ background: 'linear-gradient(135deg, #2563eb, #1d4ed8)' }}
                  >
                    <Eye className="w-4 h-4" />
                    <span>Analyse Coordinates</span>
                  </button>
                </div>
              </>
            )}
          </div>

          {/* ── Current Safety Status ── */}
          {analysisPos && (
            <div className={`rounded-2xl p-5 space-y-3 ${cfg.bg}`} style={{ border: `1px solid`, borderColor: safetyStatus === 'SAFE' ? '#6ee7b7' : safetyStatus === 'CAUTION' ? '#fcd34d' : safetyStatus === 'DANGER' ? '#fb923c' : safetyStatus === 'CRITICAL' ? '#f87171' : '#93c5fd' }}>
              <div className="flex items-center justify-between">
                <div className="text-[10px] font-mono font-bold uppercase tracking-widest text-slate-500">Safety Status</div>
                <span className={`w-2 h-2 rounded-full ${cfg.pulse} ${safetyStatus !== 'IDLE' ? 'animate-ping' : ''}`} />
              </div>

              <div className="flex items-center space-x-3">
                <div className={`p-3 rounded-2xl ${cfg.bg}`} style={{ border: `2px solid`, borderColor: safetyStatus === 'SAFE' ? '#34d399' : safetyStatus === 'CAUTION' ? '#f59e0b' : safetyStatus === 'DANGER' ? '#f97316' : safetyStatus === 'CRITICAL' ? '#ef4444' : '#60a5fa' }}>
                  <SafetyIcon className={`w-7 h-7 ${cfg.color} ${safetyStatus === 'LOADING' ? 'animate-spin' : ''}`} />
                </div>
                <div>
                  <div className={`text-2xl font-black ${cfg.color}`}>{cfg.label}</div>
                  <div className="text-xs text-slate-500">
                    {analysisPos.lat.toFixed(4)}°, {analysisPos.lon.toFixed(4)}°
                  </div>
                </div>
              </div>

              {currentRisk && (
                <>
                  <div className="w-full h-2 rounded-full bg-white/60">
                    <div
                      className={`h-2 rounded-full transition-all duration-1000 ${
                        currentRisk.risk_level === 'LOW' ? 'bg-emerald-500' :
                        currentRisk.risk_level === 'MODERATE' ? 'bg-amber-500' :
                        currentRisk.risk_level === 'HIGH' ? 'bg-orange-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${currentRisk.risk_score}%` }}
                    />
                  </div>
                  <div className={`text-xs font-bold ${cfg.color}`}>
                    Risk Score: {Math.round(currentRisk.risk_score)}/100 · Confidence: {Math.round((currentRisk.confidence ?? 0.9) * 100)}%
                  </div>
                  <p className="text-[11px] text-slate-600 leading-snug">
                    {currentRisk.recommended_action}
                  </p>

                  {/* Quick metrics */}
                  <div className="grid grid-cols-3 gap-2 pt-1">
                    {[
                      { icon: Waves, label: 'Wave', val: `${currentRisk.fused_record.wave_height?.toFixed(1)}m` },
                      { icon: Wind,  label: 'Wind', val: `${currentRisk.fused_record.wind_speed?.toFixed(0)} m/s` },
                      { icon: Thermometer, label: 'SST', val: `${currentRisk.fused_record.sst?.toFixed(1)}°C` },
                    ].map(m => (
                      <div key={m.label} className="rounded-xl p-2 text-center bg-white/60">
                        <m.icon className="w-3 h-3 mx-auto text-slate-400 mb-0.5" />
                        <div className="text-[9px] text-slate-400 font-mono">{m.label}</div>
                        <div className="text-xs font-black text-slate-700">{m.val}</div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        {/* ── Middle Column: Directional Compass Scan ──────────── */}
        <div className="space-y-4">
          <div className="rounded-2xl p-4 space-y-4" style={{ background: '#ffffff', border: '1px solid rgba(37,99,235,0.14)', boxShadow: '0 2px 12px rgba(29,78,216,0.06)' }}>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-[10px] font-mono font-bold uppercase tracking-widest text-blue-400">360° Proximity Scan</div>
                <div className="text-xs text-slate-400 mt-0.5">~{Math.round(SCAN_RADIUS_DEG * 111)} km radius</div>
              </div>
              {scanningDir && <RefreshCw className="w-4 h-4 text-blue-400 animate-spin" />}
            </div>

            {/* Compass visual */}
            {analysisPos ? (
              <div className="relative w-56 h-56 mx-auto">
                {/* Outer ring */}
                <div className="absolute inset-0 rounded-full" style={{ border: '2px solid rgba(37,99,235,0.15)' }} />
                <div className="absolute inset-4 rounded-full" style={{ border: '1px dashed rgba(37,99,235,0.10)' }} />

                {/* Center dot — current position */}
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-10">
                  <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ background: '#2563eb' }}>
                    <LocateFixed className="w-4 h-4 text-white" />
                  </div>
                  <div className="absolute -bottom-5 left-1/2 transform -translate-x-1/2 text-[9px] font-bold text-blue-700 whitespace-nowrap">YOU</div>
                </div>

                {/* Directional dots */}
                {dirScans.map((scan, i) => {
                  const angle = i * 45; // 0=N, 45=NE ...
                  const rad = (angle - 90) * (Math.PI / 180);
                  const r = 90; // radius px
                  const x = 50 + (r / 112 * 100) * Math.cos(rad);
                  const y = 50 + (r / 112 * 100) * Math.sin(rad);
                  const rc = dirRiskColor(scan.risk?.risk_level);
                  return (
                    <div
                      key={scan.direction}
                      className="absolute transform -translate-x-1/2 -translate-y-1/2"
                      style={{ left: `${x}%`, top: `${y}%` }}
                    >
                      <div className={`w-7 h-7 rounded-full flex items-center justify-center ring-2 ${rc.ring} ${rc.dot} shadow-md transition-all`}>
                        {scan.loading ? (
                          <RefreshCw className="w-3 h-3 text-white animate-spin" />
                        ) : (
                          <span className="text-[9px] font-black text-white">{scan.direction}</span>
                        )}
                      </div>
                    </div>
                  );
                })}

                {/* Cardinal labels */}
                {[['N', 50, 3], ['E', 97, 50], ['S', 50, 97], ['W', 3, 50]].map(([l, x, y]) => (
                  <div key={l} className="absolute text-[10px] font-black text-blue-300 transform -translate-x-1/2 -translate-y-1/2" style={{ left: `${x}%`, top: `${y}%` }}>
                    {l}
                  </div>
                ))}
              </div>
            ) : (
              <div className="w-56 h-56 mx-auto rounded-full flex items-center justify-center" style={{ border: '2px dashed rgba(37,99,235,0.15)' }}>
                <div className="text-center text-xs text-slate-400 space-y-1">
                  <Navigation className="w-8 h-8 mx-auto text-blue-200" />
                  <div>Enable GPS or enter<br />coordinates to scan</div>
                </div>
              </div>
            )}

            {/* Legend */}
            <div className="grid grid-cols-2 gap-1.5 text-[10px]">
              {[
                { level: 'LOW',      color: 'bg-emerald-500', label: 'Safe' },
                { level: 'MODERATE', color: 'bg-amber-500',   label: 'Caution' },
                { level: 'HIGH',     color: 'bg-orange-500',  label: 'Danger' },
                { level: 'CRITICAL', color: 'bg-red-500',     label: 'Critical' },
              ].map(l => (
                <div key={l.level} className="flex items-center space-x-1.5">
                  <span className={`w-2.5 h-2.5 rounded-full ${l.color}`} />
                  <span className="text-slate-500 font-medium">{l.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Directional detail list */}
          <div className="rounded-2xl p-4 space-y-2" style={{ background: '#ffffff', border: '1px solid rgba(37,99,235,0.14)', boxShadow: '0 2px 12px rgba(29,78,216,0.06)' }}>
            <div className="text-[10px] font-mono font-bold uppercase tracking-widest text-blue-400 mb-3">Direction Risk Breakdown</div>
            {dirScans.map(scan => {
              const rc = dirRiskColor(scan.risk?.risk_level);
              return (
                <div key={scan.direction} className="flex items-center space-x-3 py-1.5" style={{ borderBottom: '1px solid rgba(37,99,235,0.07)' }}>
                  <div className={`w-6 h-6 rounded-full flex-shrink-0 flex items-center justify-center ${rc.dot}`}>
                    <span className="text-[8px] font-black text-white">{scan.direction}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-700">{scan.label}</span>
                      {scan.loading ? (
                        <span className="text-[10px] text-blue-400 animate-pulse">Scanning…</span>
                      ) : (
                        <span className={`text-[10px] font-black ${rc.text}`}>{scan.risk?.risk_level ?? '—'}</span>
                      )}
                    </div>
                    {!scan.loading && scan.risk && (
                      <div className="w-full h-1 rounded-full bg-slate-100 mt-1">
                        <div className={`h-1 rounded-full ${rc.dot}`} style={{ width: `${scan.risk.risk_score}%` }} />
                      </div>
                    )}
                  </div>
                  {!scan.loading && scan.risk && (
                    <span className="text-[10px] font-mono text-slate-400 flex-shrink-0">{Math.round(scan.risk.risk_score)}</span>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* ── Right Column: Smart Alerts + Predictions ─────────── */}
        <div className="space-y-4">

          {/* Smart Alerts */}
          <div className="rounded-2xl p-4 space-y-3" style={{ background: '#ffffff', border: '1px solid rgba(37,99,235,0.14)', boxShadow: '0 2px 12px rgba(29,78,216,0.06)' }}>
            <div className="flex items-center justify-between">
              <div className="text-[10px] font-mono font-bold uppercase tracking-widest text-blue-400">Smart Alerts</div>
              {smartAlerts.length > 0 && (
                <span className="px-1.5 py-0.5 rounded bg-red-500 text-white text-[9px] font-black">{smartAlerts.length}</span>
              )}
            </div>

            {!analysisPos ? (
              <div className="py-6 text-center text-xs text-slate-400 space-y-1">
                <Zap className="w-8 h-8 mx-auto text-blue-200" />
                <div>Start GPS or enter location<br />to generate smart alerts</div>
              </div>
            ) : scanningDir ? (
              <div className="py-4 text-center space-y-2">
                <RefreshCw className="w-6 h-6 mx-auto text-blue-400 animate-spin" />
                <div className="text-xs text-blue-500 font-medium">Running 360° threat scan…</div>
              </div>
            ) : smartAlerts.length === 0 ? (
              <div className="py-4 rounded-xl text-center bg-emerald-50 border border-emerald-200">
                <CheckCircle2 className="w-8 h-8 mx-auto text-emerald-500 mb-2" />
                <div className="text-sm font-black text-emerald-700">All Clear</div>
                <div className="text-[11px] text-emerald-600 mt-0.5">No high-risk zones detected in surrounding area</div>
              </div>
            ) : (
              <div className="space-y-2">
                {smartAlerts.map((alert, i) => (
                  <div key={i} className={`p-3 rounded-xl space-y-1 ${alert.level === 'CRITICAL' ? 'bg-red-50 border border-red-200' : 'bg-orange-50 border border-orange-200'}`}>
                    <div className={`flex items-center space-x-2 text-xs font-black ${alert.level === 'CRITICAL' ? 'text-red-700' : 'text-orange-700'}`}>
                      <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                      <span>{alert.level} — {alert.dir} Corridor</span>
                    </div>
                    <p className="text-[11px] text-slate-600 leading-snug">{alert.msg}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* SHAP Force Drivers */}
          {currentRisk && (
            <div className="rounded-2xl p-4 space-y-3" style={{ background: '#ffffff', border: '1px solid rgba(37,99,235,0.14)', boxShadow: '0 2px 12px rgba(29,78,216,0.06)' }}>
              <div className="text-[10px] font-mono font-bold uppercase tracking-widest text-blue-400">AI Risk Drivers (SHAP)</div>
              <div className="space-y-2">
                {currentRisk.top_positive_forces.slice(0, 3).map((f, i) => (
                  <div key={i} className="flex items-start space-x-2.5 p-2 rounded-lg bg-red-50 border border-red-100">
                    <TrendingUp className="w-3.5 h-3.5 text-red-500 shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <div className="text-xs font-bold text-red-700 truncate">{f.description.split('(')[0].trim()}</div>
                      <div className="w-full h-1 rounded-full bg-red-100 mt-1">
                        <div className="h-1 rounded-full bg-red-400" style={{ width: `${Math.min(f.impact, 100)}%` }} />
                      </div>
                    </div>
                    <span className="text-[10px] font-mono font-black text-red-600 shrink-0">+{f.impact.toFixed(1)}%</span>
                  </div>
                ))}
                {currentRisk.top_negative_forces.slice(0, 2).map((f, i) => (
                  <div key={i} className="flex items-start space-x-2.5 p-2 rounded-lg bg-emerald-50 border border-emerald-100">
                    <Activity className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <div className="text-xs font-bold text-emerald-700 truncate">{f.description.split('(')[0].trim()}</div>
                    </div>
                    <span className="text-[10px] font-mono font-black text-emerald-600 shrink-0">{f.impact.toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Prediction: Upcoming path risk */}
          {analysisPos && currentRisk && (
            <div className="rounded-2xl p-4 space-y-3" style={{ background: '#ffffff', border: '1px solid rgba(37,99,235,0.14)', boxShadow: '0 2px 12px rgba(29,78,216,0.06)' }}>
              <div className="text-[10px] font-mono font-bold uppercase tracking-widest text-blue-400">Upcoming Path Prediction</div>
              <div className="space-y-2">
                {[
                  { label: '~55 km ahead (N)', dist: SCAN_RADIUS_DEG },
                  { label: '~110 km ahead (N)', dist: SCAN_RADIUS_DEG * 2 },
                  { label: '~165 km ahead (N)', dist: SCAN_RADIUS_DEG * 3 },
                ].map((step, i) => {
                  const scan = dirScans.find(s => s.direction === 'N');
                  const risk = scan?.risk;
                  const rc = dirRiskColor(risk?.risk_level);
                  // Simulate degrading confidence
                  const conf = Math.round(((currentRisk.confidence ?? 0.9) - i * 0.08) * 100);
                  return (
                    <div key={i} className="flex items-center space-x-3">
                      <div className="flex flex-col items-center">
                        <div className={`w-3 h-3 rounded-full ${rc.dot}`} />
                        {i < 2 && <div className="w-0.5 h-4 bg-slate-200" />}
                      </div>
                      <div className="flex-1 flex items-center justify-between">
                        <div>
                          <div className="text-xs font-bold text-slate-700">{step.label}</div>
                          <div className="text-[10px] text-slate-400">Confidence: {Math.max(conf, 60)}%</div>
                        </div>
                        <div className={`text-[10px] font-black px-2 py-0.5 rounded ${
                          risk?.risk_level === 'LOW' ? 'bg-emerald-100 text-emerald-700' :
                          risk?.risk_level === 'MODERATE' ? 'bg-amber-100 text-amber-700' :
                          'bg-orange-100 text-orange-700'
                        }`}>
                          {risk?.risk_level ?? 'LOADING'}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="pt-1 rounded-xl p-2.5 flex items-start space-x-2" style={{ background: '#eff6ff', border: '1px solid rgba(37,99,235,0.12)' }}>
                <Info className="w-3.5 h-3.5 text-blue-400 shrink-0 mt-0.5" />
                <p className="text-[10px] text-blue-600 leading-snug">
                  Prediction assumes northward movement. Confidence decreases with distance. Re-enter heading for accurate route-based prediction.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
