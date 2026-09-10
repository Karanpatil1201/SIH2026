import React, { useState, useEffect } from 'react';
import {
  FileText, X, MapPin, Navigation, Download, Loader2,
  CheckCircle2, AlertTriangle, Waves, Wind, Thermometer,
  Fish, Compass, Shield, Activity, Clock, Globe, Printer
} from 'lucide-react';
import { varunaAPI } from '../services/api';
import { RiskAssessmentResponse, FishingZone, PersonaType } from '../types';
import { GLOBAL_MARINE_LOCATIONS } from '../data/globalMarineLocations';

interface MarineReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  prefillLat?: number;
  prefillLon?: number;
  activePersona?: PersonaType;
}

const PERSONAS: PersonaType[] = ['Fisherman', 'Shipping', 'Disaster', 'Researcher', 'Admin'];

const riskColor = (level?: string) => {
  if (level === 'LOW')      return '#16a34a';
  if (level === 'MODERATE') return '#d97706';
  if (level === 'HIGH')     return '#ea580c';
  if (level === 'CRITICAL') return '#dc2626';
  return '#6b7280';
};

const SCAN_DIRS = [
  { d: 'N',  dlat: +0.5, dlon:  0 }, { d: 'NE', dlat: +0.5, dlon: +0.5 },
  { d: 'E',  dlat:  0,   dlon: +0.5 }, { d: 'SE', dlat: -0.5, dlon: +0.5 },
  { d: 'S',  dlat: -0.5, dlon:  0 }, { d: 'SW', dlat: -0.5, dlon: -0.5 },
  { d: 'W',  dlat:  0,   dlon: -0.5 }, { d: 'NW', dlat: +0.5, dlon: -0.5 },
];

export const MarineReportModal: React.FC<MarineReportModalProps> = ({
  isOpen, onClose, prefillLat, prefillLon, activePersona = 'Fisherman'
}) => {
  const [step, setStep] = useState<'form' | 'generating' | 'done'>('form');
  const [progress, setProgress] = useState(0);
  const [progressMsg, setProgressMsg] = useState('');

  // Form state
  const [persona, setPersona] = useState<PersonaType>(activePersona);
  const [currMode, setCurrMode] = useState<'gps' | 'manual' | 'region'>('manual');
  const [currLat, setCurrLat] = useState(prefillLat?.toFixed(4) ?? '18.9667');
  const [currLon, setCurrLon] = useState(prefillLon?.toFixed(4) ?? '72.8333');
  const [currName, setCurrName] = useState('Current Location');
  const [hasDestination, setHasDestination] = useState(false);
  const [destLat, setDestLat] = useState('');
  const [destLon, setDestLon] = useState('');
  const [destName, setDestName] = useState('Destination');
  const [selectedRegion, setSelectedRegion] = useState('arabian');
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Data
  const [currRisk, setCurrRisk] = useState<RiskAssessmentResponse | null>(null);
  const [destRisk, setDestRisk] = useState<RiskAssessmentResponse | null>(null);
  const [currFishing, setCurrFishing] = useState<FishingZone | null>(null);
  const [dirScanData, setDirScanData] = useState<{ d: string; level: string; score: number }[]>([]);

  // GPS auto-fill
  const requestGPS = () => {
    if (!navigator.geolocation) { setErrors({ gps: 'GPS not supported' }); return; }
    navigator.geolocation.getCurrentPosition(
      pos => {
        setCurrLat(pos.coords.latitude.toFixed(5));
        setCurrLon(pos.coords.longitude.toFixed(5));
        setCurrName('My GPS Location');
        setCurrMode('gps');
      },
      err => setErrors({ gps: err.message })
    );
  };

  const validate = () => {
    const e: Record<string, string> = {};
    const lat = parseFloat(currLat), lon = parseFloat(currLon);
    if (isNaN(lat) || lat < -90 || lat > 90) e.currLat = 'Invalid latitude';
    if (isNaN(lon) || lon < -180 || lon > 180) e.currLon = 'Invalid longitude';
    if (hasDestination) {
      const dlat = parseFloat(destLat), dlon = parseFloat(destLon);
      if (isNaN(dlat) || dlat < -90 || dlat > 90) e.destLat = 'Invalid latitude';
      if (isNaN(dlon) || dlon < -180 || dlon > 180) e.destLon = 'Invalid longitude';
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const generateReport = async () => {
    if (!validate()) return;
    setStep('generating');
    setProgress(0);

    const lat = parseFloat(currLat);
    const lon = parseFloat(currLon);

    try {
      setProgressMsg('Fetching current location risk assessment…'); setProgress(10);
      const cr = await varunaAPI.getRiskAssessment(lat, lon);
      setCurrRisk(cr); setProgress(25);

      setProgressMsg('Fetching fishing intelligence…');
      const cf = await varunaAPI.getFishingIntelligence(lat, lon);
      setCurrFishing(cf); setProgress(38);

      setProgressMsg('Running 360° proximity threat scan…');
      const scanResults: { d: string; level: string; score: number }[] = [];
      for (const dir of SCAN_DIRS) {
        const r = await varunaAPI.getRiskAssessment(lat + dir.dlat, lon + dir.dlon);
        scanResults.push({ d: dir.d, level: r.risk_level, score: Math.round(r.risk_score) });
        setProgress(38 + scanResults.length * 5);
      }
      setDirScanData(scanResults); setProgress(78);

      let dr: RiskAssessmentResponse | null = null;
      if (hasDestination) {
        setProgressMsg('Analysing destination location…');
        dr = await varunaAPI.getRiskAssessment(parseFloat(destLat), parseFloat(destLon));
        setDestRisk(dr);
      }
      setProgress(90);

      setProgressMsg('Compiling report…');
      await new Promise(r => setTimeout(r, 500));
      setProgress(100);

      // Open printable report in new window
      openPrintReport(cr, dr, cf, scanResults, lat, lon);
      setStep('done');
    } catch (err) {
      console.error(err);
      setErrors({ api: 'Failed to fetch data. Please check your connection and try again.' });
      setStep('form');
    }
  };

  const openPrintReport = (
    cr: RiskAssessmentResponse,
    dr: RiskAssessmentResponse | null,
    cf: FishingZone | null,
    scan: { d: string; level: string; score: number }[],
    lat: number, lon: number
  ) => {
    const now = new Date();
    const dateStr = now.toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    const timeStr = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', timeZoneName: 'short' });
    const rc = riskColor(cr.risk_level);
    const drc = dr ? riskColor(dr.risk_level) : '#6b7280';

    const scanTableRows = scan.map(s => `
      <tr>
        <td style="padding:6px 10px;font-weight:700;">${s.d}</td>
        <td style="padding:6px 10px;"><span style="padding:2px 8px;border-radius:999px;background:${riskColor(s.level)}22;color:${riskColor(s.level)};font-weight:800;font-size:11px;">${s.level}</span></td>
        <td style="padding:6px 10px;">
          <div style="background:#f1f5f9;border-radius:999px;height:8px;width:100px;overflow:hidden;">
            <div style="background:${riskColor(s.level)};height:8px;width:${s.score}%;border-radius:999px;"></div>
          </div>
        </td>
        <td style="padding:6px 10px;font-weight:900;color:${riskColor(s.level)};">${s.score}/100</td>
      </tr>
    `).join('');

    const destSection = dr ? `
      <div class="section">
        <div class="section-title" style="background:#1e40af;">🧭 Destination Location Analysis</div>
        <div class="loc-badge" style="background:#eff6ff;border:1px solid #bfdbfe;">
          📍 ${destName} — ${parseFloat(destLat).toFixed(4)}°N, ${parseFloat(destLon).toFixed(4)}°E
        </div>
        <div class="kpi-grid">
          <div class="kpi" style="border-left:4px solid ${drc}">
            <div class="kpi-label">Safety Status</div>
            <div class="kpi-value" style="color:${drc}">${dr.risk_level}</div>
            <div class="kpi-sub">Score: ${Math.round(dr.risk_score)}/100</div>
          </div>
          <div class="kpi"><div class="kpi-label">Wave Height</div><div class="kpi-value">${dr.fused_record.wave_height?.toFixed(2) ?? '—'}m</div><div class="kpi-sub">Period: ${dr.fused_record.wave_period?.toFixed(1) ?? '—'}s</div></div>
          <div class="kpi"><div class="kpi-label">Wind Speed</div><div class="kpi-value">${dr.fused_record.wind_speed?.toFixed(1) ?? '—'} m/s</div><div class="kpi-sub">${(dr.fused_record.wind_speed * 1.944).toFixed(0)} knots</div></div>
          <div class="kpi"><div class="kpi-label">Sea Surface Temp</div><div class="kpi-value">${dr.fused_record.sst?.toFixed(1) ?? '—'}°C</div><div class="kpi-sub">INCOIS SST Feed</div></div>
        </div>
        <div class="advisory">${dr.recommended_action}</div>
      </div>
    ` : '';

    const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>VARUNA Marine Safety Report — ${dateStr}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
    * { margin:0;padding:0;box-sizing:border-box; }
    body { font-family:'Inter',sans-serif;background:#fff;color:#0f172a;font-size:13px; }
    .page { max-width:860px;margin:0 auto;padding:32px; }

    /* Header */
    .header { background:linear-gradient(135deg,#1e3a8a 0%,#2563eb 100%);color:#fff;padding:28px 32px;border-radius:16px;margin-bottom:24px;display:flex;justify-content:space-between;align-items:center; }
    .brand { display:flex;align-items:center;gap:14px; }
    .brand-icon { background:rgba(255,255,255,0.18);border:1px solid rgba(255,255,255,0.30);border-radius:12px;padding:10px;font-size:24px; }
    .brand-name { font-size:28px;font-weight:900;letter-spacing:.08em; }
    .brand-sub { font-size:11px;opacity:.75;font-weight:600;margin-top:2px; }
    .report-meta { text-align:right;font-size:11px;opacity:.80; }
    .report-meta strong { font-size:14px;opacity:1; }

    /* Status badge */
    .status-bar { padding:14px 20px;border-radius:12px;margin-bottom:24px;display:flex;align-items:center;gap:16px;font-weight:800; }

    /* Sections */
    .section { margin-bottom:24px;border-radius:12px;overflow:hidden;border:1px solid #e2e8f0; }
    .section-title { background:#1e40af;color:#fff;padding:10px 18px;font-size:11px;font-weight:800;letter-spacing:.10em;text-transform:uppercase; }
    .section-body { padding:18px; }

    /* Location badge */
    .loc-badge { padding:8px 14px;border-radius:8px;font-size:12px;font-weight:700;margin:12px 18px; }

    /* KPI grid */
    .kpi-grid { display:grid;grid-template-columns:repeat(4,1fr);gap:12px;padding:14px 18px; }
    @media(max-width:600px){.kpi-grid{grid-template-columns:repeat(2,1fr);}}
    .kpi { background:#f8fafc;border-radius:10px;padding:12px 14px;border-left:4px solid #2563eb; }
    .kpi-label { font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#94a3b8; }
    .kpi-value { font-size:20px;font-weight:900;color:#0f172a;margin:4px 0 2px; }
    .kpi-sub { font-size:10px;color:#64748b;font-weight:600; }

    /* Advisory */
    .advisory { margin:0 18px 18px;padding:12px 16px;background:#eff6ff;border-left:4px solid #2563eb;border-radius:0 8px 8px 0;font-size:12px;font-weight:600;color:#1e3a8a;line-height:1.6; }

    /* SHAP table */
    .shap-row-pos { background:#fef2f2; }
    .shap-row-neg { background:#f0fdf4; }
    table { width:100%;border-collapse:collapse; }
    th { text-align:left;padding:8px 10px;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.06em;color:#64748b;background:#f8fafc;border-bottom:2px solid #e2e8f0; }
    td { font-size:12px;font-weight:600;border-bottom:1px solid #f1f5f9; }

    /* Scan grid */
    .scan-grid { display:grid;grid-template-columns:repeat(4,1fr);gap:8px;padding:14px 18px; }
    .scan-cell { text-align:center;padding:10px 6px;border-radius:8px;background:#f8fafc; }
    .scan-dir { font-size:14px;font-weight:900;color:#0f172a; }
    .scan-lvl { font-size:9px;font-weight:800;margin-top:3px;padding:2px 6px;border-radius:999px; }
    .scan-bar-wrap { background:#e2e8f0;border-radius:999px;height:4px;margin-top:4px;overflow:hidden; }
    .scan-bar { height:4px;border-radius:999px; }

    /* Footer */
    .footer { margin-top:32px;padding:16px;background:#f8fafc;border-radius:12px;text-align:center;font-size:10px;color:#94a3b8;font-weight:600;border:1px solid #e2e8f0; }
    .footer strong { color:#2563eb; }

    /* Print */
    @media print {
      body { background:#fff; }
      .page { padding:16px; }
      .no-print { display:none!important; }
    }
  </style>
</head>
<body>
<div class="page">
  <!-- Print button (hidden on print) -->
  <div class="no-print" style="margin-bottom:16px;display:flex;gap:10px;">
    <button onclick="window.print()" style="background:#2563eb;color:#fff;border:none;padding:10px 22px;border-radius:10px;font-weight:800;font-size:13px;cursor:pointer;display:flex;align-items:center;gap:8px;">
      🖨️ Save as PDF / Print
    </button>
    <button onclick="window.close()" style="background:#f1f5f9;color:#374151;border:1px solid #e2e8f0;padding:10px 18px;border-radius:10px;font-weight:700;font-size:13px;cursor:pointer;">
      ✕ Close
    </button>
  </div>

  <!-- Header -->
  <div class="header">
    <div class="brand">
      <div class="brand-icon">⚓</div>
      <div>
        <div class="brand-name">VARUNA</div>
        <div class="brand-sub">Multi-Agent Marine Intelligence Platform · SIH 2026</div>
      </div>
    </div>
    <div class="report-meta">
      <strong>🌊 Marine Safety Report</strong><br/>
      ${dateStr}<br/>
      ${timeStr}<br/>
      <span style="margin-top:4px;display:inline-block;padding:2px 8px;background:rgba(255,255,255,0.20);border-radius:999px;">Persona: ${persona}</span>
    </div>
  </div>

  <!-- Overall Status -->
  <div class="status-bar" style="background:${rc}18;border:2px solid ${rc}40;">
    <div style="width:16px;height:16px;border-radius:50%;background:${rc};flex-shrink:0;"></div>
    <div>
      <span style="font-size:18px;color:${rc};">Current Location: ${cr.risk_level} RISK</span>
      &nbsp;&nbsp;
      <span style="font-size:13px;font-weight:600;color:#64748b;">Risk Score ${Math.round(cr.risk_score)}/100 · Confidence ${Math.round((cr.confidence ?? 0.9) * 100)}%</span>
    </div>
  </div>

  <!-- Current Location -->
  <div class="section">
    <div class="section-title" style="background:#1e3a8a;">📍 Current Location Analysis</div>
    <div class="loc-badge" style="background:#eff6ff;border:1px solid #bfdbfe;">
      📍 ${currName} — ${lat.toFixed(5)}°N, ${lon.toFixed(5)}°E &nbsp;|&nbsp; ${dateStr}, ${timeStr}
    </div>
    <div class="kpi-grid">
      <div class="kpi" style="border-left-color:${rc}">
        <div class="kpi-label">Safety Status</div>
        <div class="kpi-value" style="color:${rc};font-size:16px;">${cr.risk_level}</div>
        <div class="kpi-sub">Score: ${Math.round(cr.risk_score)}/100</div>
      </div>
      <div class="kpi" style="border-left-color:#0ea5e9">
        <div class="kpi-label">Sig Wave Height</div>
        <div class="kpi-value">${cr.fused_record.wave_height?.toFixed(2) ?? '—'}m</div>
        <div class="kpi-sub">Period: ${cr.fused_record.wave_period?.toFixed(1) ?? '—'}s · Swell: ${cr.fused_record.swell_height?.toFixed(2) ?? '—'}m</div>
      </div>
      <div class="kpi" style="border-left-color:#8b5cf6">
        <div class="kpi-label">Surface Wind</div>
        <div class="kpi-value">${cr.fused_record.wind_speed?.toFixed(1) ?? '—'} m/s</div>
        <div class="kpi-sub">${((cr.fused_record.wind_speed ?? 0) * 1.944).toFixed(0)} knots · Dir ${cr.fused_record.wind_direction?.toFixed(0) ?? '—'}°</div>
      </div>
      <div class="kpi" style="border-left-color:#f59e0b">
        <div class="kpi-label">Sea Surface Temp</div>
        <div class="kpi-value">${cr.fused_record.sst?.toFixed(1) ?? '—'}°C</div>
        <div class="kpi-sub">Salinity: ${cr.fused_record.salinity?.toFixed(1) ?? '—'} PSU</div>
      </div>
      <div class="kpi" style="border-left-color:#10b981">
        <div class="kpi-label">Current Velocity</div>
        <div class="kpi-value">${cr.fused_record.current_velocity?.toFixed(2) ?? '—'} m/s</div>
        <div class="kpi-sub">ARGO Float Network</div>
      </div>
      <div class="kpi" style="border-left-color:#ec4899">
        <div class="kpi-label">Chlorophyll-a</div>
        <div class="kpi-value">${cr.fused_record.chlorophyll?.toFixed(2) ?? '—'}</div>
        <div class="kpi-sub">mg/m³ · OCM Satellite</div>
      </div>
      <div class="kpi" style="border-left-color:#6366f1">
        <div class="kpi-label">Atm Pressure</div>
        <div class="kpi-value">${cr.fused_record.pressure?.toFixed(0) ?? '—'} hPa</div>
        <div class="kpi-sub">WMO Station Network</div>
      </div>
      <div class="kpi" style="border-left-color:#14b8a6">
        <div class="kpi-label">Data Quality</div>
        <div class="kpi-value">${cr.fused_record.quality_report?.quality_score?.toFixed(0) ?? '98'}%</div>
        <div class="kpi-sub">${cr.fused_record.data_source_mode ?? 'HYBRID'} Mode</div>
      </div>
    </div>
    ${cf ? `
    <div style="padding:0 18px 10px;font-size:11px;font-weight:700;color:#064e3b;background:#f0fdf4;margin:0 18px;border-radius:8px;padding:10px 14px;">
      🐟 Nearest PFZ: ${cf.radius_km?.toFixed(1)} km radius · Score: ${Math.round(cf.pfz_indicator_score * 100)}% · Species: ${cf.recommended_target_species?.slice(0,3).join(', ') ?? '—'}
    </div>` : ''}
    <div class="advisory">${cr.recommended_action}</div>
  </div>

  <!-- Destination -->
  ${destSection}

  <!-- 360° Proximity Scan -->
  <div class="section">
    <div class="section-title" style="background:#1e40af;">🧭 360° Proximity Threat Scan (~55 km radius)</div>
    <div class="scan-grid">
      ${scan.map(s => `
        <div class="scan-cell">
          <div class="scan-dir">${s.d}</div>
          <div class="scan-lvl" style="background:${riskColor(s.level)}20;color:${riskColor(s.level)}">${s.level}</div>
          <div class="scan-bar-wrap"><div class="scan-bar" style="background:${riskColor(s.level)};width:${s.score}%"></div></div>
          <div style="font-size:11px;font-weight:900;color:${riskColor(s.level)};margin-top:3px;">${s.score}</div>
        </div>
      `).join('')}
    </div>
    ${scan.filter(s => s.level === 'HIGH' || s.level === 'CRITICAL').length > 0 ? `
    <div style="margin:0 18px 16px;padding:10px 14px;background:#fef2f2;border:1px solid #fecaca;border-radius:8px;font-size:11px;font-weight:700;color:#dc2626;">
      ⚠️ HIGH RISK DIRECTIONS: ${scan.filter(s => s.level === 'HIGH' || s.level === 'CRITICAL').map(s => s.d).join(', ')} — Exercise extreme caution when navigating in these directions.
    </div>` : `
    <div style="margin:0 18px 16px;padding:10px 14px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;font-size:11px;font-weight:700;color:#16a34a;">
      ✓ All surrounding corridors appear safe. Proceed with standard marine precautions.
    </div>`}
  </div>

  <!-- SHAP Risk Drivers -->
  <div class="section">
    <div class="section-title" style="background:#7c3aed;">🤖 AI Risk Drivers (XGBoost SHAP Explainability)</div>
    <div class="section-body" style="padding:0;">
      <table>
        <thead><tr>
          <th>Factor</th><th>Description</th><th>Value</th><th>Impact</th>
        </tr></thead>
        <tbody>
          ${cr.top_positive_forces.map(f => `
          <tr class="shap-row-pos">
            <td style="padding:8px 10px;font-weight:800;color:#dc2626;">${f.feature.replace(/_/g,' ').toUpperCase()}</td>
            <td style="padding:8px 10px;">${f.description}</td>
            <td style="padding:8px 10px;font-family:monospace;">${typeof f.value === 'number' ? f.value.toFixed(2) : f.value}</td>
            <td style="padding:8px 10px;font-weight:900;color:#dc2626;">+${f.impact.toFixed(1)}%</td>
          </tr>`).join('')}
          ${cr.top_negative_forces.map(f => `
          <tr class="shap-row-neg">
            <td style="padding:8px 10px;font-weight:800;color:#16a34a;">${f.feature.replace(/_/g,' ').toUpperCase()}</td>
            <td style="padding:8px 10px;">${f.description}</td>
            <td style="padding:8px 10px;font-family:monospace;">${typeof f.value === 'number' ? f.value.toFixed(2) : f.value}</td>
            <td style="padding:8px 10px;font-weight:900;color:#16a34a;">${f.impact.toFixed(1)}%</td>
          </tr>`).join('')}
        </tbody>
      </table>
    </div>
  </div>

  <!-- Footer -->
  <div class="footer">
    <strong>VARUNA</strong> — Smart India Hackathon 2026 · Multi-Agent Marine Intelligence System<br/>
    Powered by Copernicus Marine PHY · Open-Meteo · INCOIS OMNI Buoy Network · XGBoost + Isolation Forest<br/>
    Report generated: ${dateStr} at ${timeStr}<br/>
    <em>⚠️ Disclaimer: This report is generated by an AI prototype system. Always cross-verify with official INCOIS / IMD advisories before making operational decisions at sea.</em>
  </div>
</div>
</body>
</html>`;

    const win = window.open('', '_blank', 'width=960,height=900,scrollbars=yes');
    if (win) {
      win.document.write(html);
      win.document.close();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4" style={{ background: 'rgba(15,23,42,0.55)', backdropFilter: 'blur(6px)' }}>
      <div className="w-full max-w-xl rounded-2xl overflow-hidden shadow-2xl" style={{ background: '#fff', border: '1px solid rgba(37,99,235,0.18)', maxHeight: '90vh', overflowY: 'auto' }}>

        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4" style={{ background: 'linear-gradient(135deg, #1e3a8a, #2563eb)' }}>
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl" style={{ background: 'rgba(255,255,255,0.18)' }}>
              <FileText className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="font-black text-white text-base">Marine Safety Report</div>
              <div className="text-[11px] text-blue-200">Generate a full PDF report for any location or journey</div>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg text-white/60 hover:text-white hover:bg-white/15 transition-all">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* ── Form Step ── */}
        {step === 'form' && (
          <div className="p-6 space-y-5">

            {/* Persona */}
            <div>
              <label className="text-[10px] font-mono font-bold uppercase tracking-widest text-blue-400 block mb-2">Report Persona</label>
              <div className="flex flex-wrap gap-2">
                {PERSONAS.map(p => (
                  <button
                    key={p}
                    onClick={() => setPersona(p)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                      persona === p ? 'text-white shadow-sm' : 'text-slate-500 hover:text-blue-600'
                    }`}
                    style={{
                      background: persona === p ? '#2563eb' : '#f8fafc',
                      border: `1px solid ${persona === p ? '#1d4ed8' : '#e2e8f0'}`
                    }}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>

            {/* Current Location */}
            <div className="rounded-xl p-4 space-y-3" style={{ background: '#f8fafc', border: '1px solid #e2e8f0' }}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 text-sm font-bold text-blue-900">
                  <MapPin className="w-4 h-4 text-blue-500" />
                  <span>Current Location</span>
                </div>
                <button
                  onClick={requestGPS}
                  className="flex items-center space-x-1.5 px-3 py-1 rounded-lg text-xs font-bold text-blue-600 hover:bg-blue-100 transition-colors"
                  style={{ background: '#eff6ff', border: '1px solid rgba(37,99,235,0.20)' }}
                >
                  <Compass className="w-3.5 h-3.5" />
                  <span>Use GPS</span>
                </button>
              </div>
              <input
                value={currName}
                onChange={e => setCurrName(e.target.value)}
                placeholder="Location name (e.g. Mumbai Port)"
                className="w-full px-3 py-2 rounded-lg text-sm font-medium text-blue-900 outline-none"
                style={{ background: '#fff', border: '1px solid rgba(37,99,235,0.20)' }}
              />
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[10px] font-bold text-slate-400 uppercase">Latitude</label>
                  <input
                    value={currLat} onChange={e => setCurrLat(e.target.value)}
                    placeholder="e.g. 18.9667"
                    className="mt-1 w-full px-3 py-2 rounded-lg text-sm font-mono font-bold text-blue-900 outline-none"
                    style={{ background: '#fff', border: `1px solid ${errors.currLat ? '#ef4444' : 'rgba(37,99,235,0.20)'}` }}
                  />
                  {errors.currLat && <div className="text-xs text-red-500 mt-1">{errors.currLat}</div>}
                </div>
                <div>
                  <label className="text-[10px] font-bold text-slate-400 uppercase">Longitude</label>
                  <input
                    value={currLon} onChange={e => setCurrLon(e.target.value)}
                    placeholder="e.g. 72.8333"
                    className="mt-1 w-full px-3 py-2 rounded-lg text-sm font-mono font-bold text-blue-900 outline-none"
                    style={{ background: '#fff', border: `1px solid ${errors.currLon ? '#ef4444' : 'rgba(37,99,235,0.20)'}` }}
                  />
                  {errors.currLon && <div className="text-xs text-red-500 mt-1">{errors.currLon}</div>}
                </div>
              </div>
              {errors.gps && <div className="text-xs text-red-500">{errors.gps}</div>}
            </div>

            {/* Destination toggle */}
            <div>
              <label className="flex items-center space-x-3 cursor-pointer">
                <div
                  onClick={() => setHasDestination(v => !v)}
                  className="relative w-10 h-5 rounded-full transition-colors cursor-pointer"
                  style={{ background: hasDestination ? '#2563eb' : '#cbd5e1' }}
                >
                  <div className="absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-all" style={{ left: hasDestination ? '22px' : '2px' }} />
                </div>
                <div>
                  <div className="text-sm font-bold text-blue-900">Include Destination</div>
                  <div className="text-[11px] text-slate-400">Analyse where you want to go</div>
                </div>
              </label>
            </div>

            {/* Destination inputs */}
            {hasDestination && (
              <div className="rounded-xl p-4 space-y-3" style={{ background: '#f8fafc', border: '1px solid #e2e8f0' }}>
                <div className="flex items-center space-x-2 text-sm font-bold text-blue-900">
                  <Navigation className="w-4 h-4 text-emerald-500" />
                  <span>Destination Location</span>
                </div>
                <input
                  value={destName} onChange={e => setDestName(e.target.value)}
                  placeholder="Destination name (e.g. Goa Port)"
                  className="w-full px-3 py-2 rounded-lg text-sm font-medium text-blue-900 outline-none"
                  style={{ background: '#fff', border: '1px solid rgba(37,99,235,0.20)' }}
                />
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-[10px] font-bold text-slate-400 uppercase">Latitude</label>
                    <input
                      value={destLat} onChange={e => setDestLat(e.target.value)}
                      placeholder="e.g. 15.4910"
                      className="mt-1 w-full px-3 py-2 rounded-lg text-sm font-mono font-bold text-blue-900 outline-none"
                      style={{ background: '#fff', border: `1px solid ${errors.destLat ? '#ef4444' : 'rgba(37,99,235,0.20)'}` }}
                    />
                    {errors.destLat && <div className="text-xs text-red-500 mt-1">{errors.destLat}</div>}
                  </div>
                  <div>
                    <label className="text-[10px] font-bold text-slate-400 uppercase">Longitude</label>
                    <input
                      value={destLon} onChange={e => setDestLon(e.target.value)}
                      placeholder="e.g. 73.8278"
                      className="mt-1 w-full px-3 py-2 rounded-lg text-sm font-mono font-bold text-blue-900 outline-none"
                      style={{ background: '#fff', border: `1px solid ${errors.destLon ? '#ef4444' : 'rgba(37,99,235,0.20)'}` }}
                    />
                    {errors.destLon && <div className="text-xs text-red-500 mt-1">{errors.destLon}</div>}
                  </div>
                </div>
                {/* Quick destination presets */}
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {[
                    { name: 'Goa Port', lat: '15.4910', lon: '73.8278' },
                    { name: 'Kochi', lat: '9.9312', lon: '76.2673' },
                    { name: 'Chennai', lat: '13.0827', lon: '80.2707' },
                    { name: 'Visakhapatnam', lat: '17.6868', lon: '83.2185' },
                  ].map(p => (
                    <button
                      key={p.name}
                      onClick={() => { setDestLat(p.lat); setDestLon(p.lon); setDestName(p.name); }}
                      className="px-2 py-1 rounded-lg text-[10px] font-bold text-blue-600 hover:bg-blue-100 transition-colors"
                      style={{ background: '#eff6ff', border: '1px solid rgba(37,99,235,0.15)' }}
                    >
                      {p.name}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {errors.api && (
              <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-600 font-medium">{errors.api}</div>
            )}

            {/* Report contents info */}
            <div className="rounded-xl p-3" style={{ background: '#eff6ff', border: '1px solid rgba(37,99,235,0.15)' }}>
              <div className="text-[10px] font-mono font-bold text-blue-400 uppercase tracking-wider mb-2">Report Includes</div>
              <div className="grid grid-cols-2 gap-1">
                {[
                  '📍 Full location analysis', '🌊 Wave & wind data',
                  '🌡️ Sea surface temperature', '🐟 Fishing zone (PFZ)',
                  '🧭 360° threat scan', '🤖 SHAP AI risk drivers',
                  hasDestination ? '🗺️ Destination safety' : '⚡ Real-time conditions',
                  '💾 PDF export ready',
                ].map((item, i) => (
                  <div key={i} className="flex items-center space-x-1.5 text-[11px] text-blue-700 font-medium">
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={generateReport}
              className="w-full py-3 rounded-xl text-sm font-bold text-white flex items-center justify-center space-x-2 hover:opacity-90 transition-all"
              style={{ background: 'linear-gradient(135deg, #2563eb, #1d4ed8)', boxShadow: '0 4px 20px rgba(37,99,235,0.30)' }}
            >
              <Download className="w-4 h-4" />
              <span>Generate & Open Report</span>
            </button>
          </div>
        )}

        {/* ── Generating Step ── */}
        {step === 'generating' && (
          <div className="p-10 flex flex-col items-center text-center space-y-5">
            <div className="relative w-20 h-20">
              <svg className="w-20 h-20 -rotate-90" viewBox="0 0 80 80">
                <circle cx="40" cy="40" r="34" fill="none" stroke="#dbeafe" strokeWidth="6" />
                <circle cx="40" cy="40" r="34" fill="none" stroke="#2563eb" strokeWidth="6"
                  strokeDasharray={`${2 * Math.PI * 34}`}
                  strokeDashoffset={`${2 * Math.PI * 34 * (1 - progress / 100)}`}
                  strokeLinecap="round" style={{ transition: 'stroke-dashoffset 0.4s ease' }}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-sm font-black text-blue-700">{progress}%</span>
              </div>
            </div>
            <div>
              <div className="text-base font-black text-blue-900">Generating Report…</div>
              <div className="text-xs text-slate-400 mt-1">{progressMsg}</div>
            </div>
            <div className="w-full rounded-xl p-3" style={{ background: '#eff6ff', border: '1px solid rgba(37,99,235,0.15)' }}>
              {['Fetching risk data', 'Fishing intelligence', '360° scan (8 points)', 'AI SHAP analysis', hasDestination ? 'Destination analysis' : '', 'Compiling PDF'].filter(Boolean).map((s, i) => (
                <div key={i} className={`flex items-center space-x-2 py-1 text-xs ${progress > i * 15 ? 'text-blue-700 font-bold' : 'text-slate-300'}`}>
                  {progress > (i + 1) * 15 ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> : <div className="w-3.5 h-3.5 rounded-full border-2 border-slate-200" />}
                  <span>{s}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── Done Step ── */}
        {step === 'done' && (
          <div className="p-10 flex flex-col items-center text-center space-y-5">
            <div className="w-16 h-16 rounded-2xl bg-emerald-50 border-2 border-emerald-300 flex items-center justify-center">
              <CheckCircle2 className="w-8 h-8 text-emerald-500" />
            </div>
            <div>
              <div className="text-xl font-black text-blue-900">Report Ready!</div>
              <div className="text-xs text-slate-500 mt-1">The report has opened in a new window. Use the <strong>Save as PDF / Print</strong> button to save it.</div>
            </div>
            <div className="flex gap-3 w-full">
              <button
                onClick={() => { setStep('form'); setProgress(0); }}
                className="flex-1 py-2.5 rounded-xl text-sm font-bold text-blue-700 hover:bg-blue-100 transition-colors"
                style={{ background: '#eff6ff', border: '1px solid rgba(37,99,235,0.20)' }}
              >
                Generate Another
              </button>
              <button
                onClick={onClose}
                className="flex-1 py-2.5 rounded-xl text-sm font-bold text-white hover:opacity-90 transition-all"
                style={{ background: 'linear-gradient(135deg,#2563eb,#1d4ed8)' }}
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
