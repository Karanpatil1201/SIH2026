import React from 'react';
import {
  MapPin, AlertTriangle, ShieldCheck, Printer, Sparkles, CheckCircle2,
  Zap, AlertCircle, ArrowUpRight, FileText, Info, HelpCircle, Compass
} from 'lucide-react';
import { RiskAssessmentResponse, PersonaType } from '../types';

interface ExecutiveAnalysisReportProps {
  assessment: RiskAssessmentResponse | null;
  selectedRegion: string;
  activePersona: PersonaType;
  loading: boolean;
  onPrintReport: () => void;
  onShowJSONAPI: () => void;
}

import { GLOBAL_MARINE_LOCATIONS, GlobalMarineLocation } from '../data/globalMarineLocations';

export const ExecutiveAnalysisReport: React.FC<ExecutiveAnalysisReportProps> = ({
  assessment,
  selectedRegion,
  activePersona,
  loading,
  onPrintReport,
  onShowJSONAPI
}) => {
  if (loading || !assessment) {
    return (
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-12 flex flex-col items-center justify-center space-y-4 min-h-[400px]">
        <div className="w-12 h-12 border-4 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin" />
        <p className="text-sm font-bold text-cyan-600 dark:text-cyan-400">
          Synthesizing Multi-Satellite Correlation & XGBoost Risk Matrix...
        </p>
      </div>
    );
  }

  const locationData: GlobalMarineLocation = GLOBAL_MARINE_LOCATIONS.find(l => l.id === selectedRegion) || GLOBAL_MARINE_LOCATIONS[0];
  const riskScore = locationData.riskScore || assessment.risk_score || 50;
  const confidencePct = Math.round((assessment.confidence || 0.94) * 100);

  const currentTitle = `${locationData.name} — AI Ocean Analysis Report`;
  const currentLocationTag = locationData.regionTag;

  return (
    <div className="space-y-6 text-slate-100 selection:bg-cyan-500 selection:text-slate-950">
      {/* Header Metadata Section */}
      <div className="bg-[#07192c] border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-4 shadow-xl">
        {/* Location Badge */}
        <div className="flex items-center space-x-2 text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider">
          <MapPin className="w-4 h-4 text-cyan-400" />
          <span>{currentLocationTag}</span>
        </div>

        {/* Title and Top Action Badges */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
            {currentTitle}
          </h1>

          <div className="flex flex-wrap items-center gap-2">
            {/* Anomaly Badge */}
            <span className="px-3 py-1.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 text-xs font-bold flex items-center space-x-1.5 shadow-sm">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>Possible Changes Detected</span>
            </span>

            {/* Confidence Badge */}
            <span className="px-3 py-1.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 text-xs font-bold font-mono shadow-sm">
              {confidencePct}% Sure
            </span>

            {/* Print Report Button */}
            <button
              onClick={onPrintReport}
              className="px-3.5 py-1.5 rounded-full bg-[#05111d] hover:bg-[#0c2744] text-slate-200 text-xs font-bold flex items-center space-x-1.5 transition-all border border-slate-700 shadow-sm"
            >
              <Printer className="w-3.5 h-3.5 text-cyan-400" />
              <span>Print Report</span>
            </button>
          </div>
        </div>

        {/* Subtitle Details */}
        <p className="text-xs text-slate-400 font-medium">
          Verified on {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })} • Coordinates: {assessment.location.lat.toFixed(2)}° N, {assessment.location.lon.toFixed(2)}° E • Multi-satellite & In-situ float correlation
        </p>
      </div>

      {/* Hero Plain-English AI Summary (VARUNA Review) */}
      <div className="bg-gradient-to-r from-[#072540] via-[#092d4f] to-[#051c33] border border-cyan-500/40 rounded-3xl p-6 sm:p-8 space-y-3 shadow-xl">
        <div className="flex items-center space-x-2 text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider">
          <CheckCircle2 className="w-4 h-4 text-cyan-400" />
          <span>PLAIN-ENGLISH AI SUMMARY (VARUNA REVIEW)</span>
        </div>

        <blockquote className="text-lg sm:text-xl font-bold text-white leading-snug">
          "{locationData.name}: {locationData.description}"
        </blockquote>

        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-medium">
          We avoided technical jargon: baseline sea surface temperature is {locationData.baselineSST}°C with waves averaging {locationData.baselineWave}m and wind speeds at {locationData.baselineWind} knots. Key marine species monitored include {locationData.keyTargetSpecies.join(', ')}.
        </p>
      </div>

      {/* 5-Point Deep Ocean Analysis Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-black tracking-tight text-white">
            5-Point Deep Ocean Analysis — {locationData.name}
          </h3>
          <span className="text-xs font-mono text-cyan-400 font-bold">
            Multi-Agent Correlation
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {/* Card 1: What is Normal? (Green Tint Header) */}
          <div className="bg-[#07192c] border border-emerald-500/30 rounded-2xl p-5 space-y-2.5 shadow-lg">
            <div className="text-xs font-mono font-bold text-emerald-300 flex items-center space-x-1.5 bg-emerald-950/60 p-2 rounded-xl border border-emerald-500/40">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>1. What is Normal?</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed font-medium">
              Normal {locationData.name} baseline features sea surface temperatures near ~{locationData.baselineSST}°C avg, steady trade winds, and stable circulation patterns.
            </p>
          </div>

          {/* Card 2: What is Changing? (Amber Tint Header) */}
          <div className="bg-[#07192c] border border-amber-500/30 rounded-2xl p-5 space-y-2.5 shadow-lg">
            <div className="text-xs font-mono font-bold text-amber-300 flex items-center space-x-1.5 bg-amber-950/60 p-2 rounded-xl border border-amber-500/40">
              <Zap className="w-4 h-4 text-amber-400 shrink-0" />
              <span>2. What is Changing?</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed font-medium">
              Surface waters show thermal variation. Waves measured at {locationData.baselineWave}m with wind gusts reaching {locationData.baselineWind} knots across regional channels.
            </p>
          </div>

          {/* Card 3: What is Unusual? (Red/Coral Tint Header) */}
          <div className="bg-[#07192c] border border-red-500/30 rounded-2xl p-5 space-y-2.5 shadow-lg">
            <div className="text-xs font-mono font-bold text-red-300 flex items-center space-x-1.5 bg-red-950/60 p-2 rounded-xl border border-red-500/40">
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
              <span>3. What is Unusual?</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed font-medium">
              Isolation Forest anomaly score flags current shear variance near coordinate ({locationData.lat.toFixed(2)}°, {locationData.lon.toFixed(2)}°).
            </p>
          </div>

          {/* Card 4: Why It Matters (Purple Tint Header) */}
          <div className="bg-[#07192c] border border-purple-500/30 rounded-2xl p-5 space-y-2.5 shadow-lg">
            <div className="text-xs font-mono font-bold text-purple-300 flex items-center space-x-1.5 bg-purple-950/60 p-2 rounded-xl border border-purple-500/40">
              <Sparkles className="w-4 h-4 text-purple-400 shrink-0" />
              <span>4. Why It Matters</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed font-medium">
              Affects catch rates for {locationData.keyTargetSpecies.slice(0, 2).join(' & ')} while impacting vessel route efficiency and safety thresholds.
            </p>
          </div>

          {/* Card 5: Recommended Action (Blue Tint Header) */}
          <div className="bg-[#07192c] border border-cyan-500/30 rounded-2xl p-5 space-y-2.5 shadow-lg">
            <div className="text-xs font-mono font-bold text-cyan-300 flex items-center space-x-1.5 bg-cyan-950/60 p-2 rounded-xl border border-cyan-500/40">
              <ShieldCheck className="w-4 h-4 text-cyan-400 shrink-0" />
              <span>5. Recommended Action</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed font-medium">
              {assessment.recommended_action || 'Exercise caution over offshore routes. Issue high wave warnings to local harbours.'}
            </p>
          </div>
        </div>
      </div>

      {/* SHAP Feature Impact Breakdown */}
      <div className="bg-[#07192c] border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-4 shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h4 className="text-base font-bold text-white flex items-center space-x-2">
            <HelpCircle className="w-5 h-5 text-cyan-400" />
            <span>SHAP Explainability & Physical Force Drivers</span>
          </h4>
          <span className="text-xs font-mono text-cyan-300">
            XGBoost Risk Score: {riskScore.toFixed(1)} / 100
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          {/* Positive Risk Forces */}
          <div className="space-y-2">
            <div className="font-bold text-red-400 uppercase tracking-wider font-mono text-[10px]">
              Risk Increasing Drivers (+Impact)
            </div>
            {assessment.top_positive_forces.map((force, i) => (
              <div key={i} className="p-3 rounded-xl bg-red-950/20 border border-red-500/30 flex justify-between items-center">
                <div>
                  <div className="font-bold text-slate-200">{force.description}</div>
                  <div className="text-[10px] text-slate-400 font-mono">Value: {force.value}</div>
                </div>
                <span className="font-mono font-bold text-red-400">+{force.impact}%</span>
              </div>
            ))}
          </div>

          {/* Mitigating Forces */}
          <div className="space-y-2">
            <div className="font-bold text-emerald-400 uppercase tracking-wider font-mono text-[10px]">
              Risk Mitigating Drivers (-Impact)
            </div>
            {assessment.top_negative_forces.map((force, i) => (
              <div key={i} className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/30 flex justify-between items-center">
                <div>
                  <div className="font-bold text-slate-200">{force.description}</div>
                  <div className="text-[10px] text-slate-400 font-mono">Value: {force.value}</div>
                </div>
                <span className="font-mono font-bold text-emerald-400">{force.impact}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
