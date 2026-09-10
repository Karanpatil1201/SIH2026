import React from 'react';
import { ShieldAlert, TrendingUp, TrendingDown, Thermometer, Wind, Waves, Gauge, CloudRain, Droplet, CheckCircle, AlertTriangle } from 'lucide-react';
import { RiskAssessmentResponse } from '../types';

interface RiskAssessmentViewProps {
  assessment: RiskAssessmentResponse | null;
  loading: boolean;
}

export const RiskAssessmentView: React.FC<RiskAssessmentViewProps> = ({ assessment, loading }) => {
  if (loading) {
    return (
      <div className="glass-panel p-8 rounded-2xl flex flex-col items-center justify-center space-y-4 min-h-[350px]">
        <div className="w-12 h-12 border-4 border-cyan-500/30 border-t-cyan-400 rounded-full animate-spin" />
        <p className="text-sm font-semibold text-cyan-300">Fusing Copernicus & Open-Meteo Data Streams...</p>
      </div>
    );
  }

  if (!assessment) {
    return (
      <div className="glass-panel p-8 rounded-2xl text-center text-slate-400">
        No risk assessment loaded. Pick a location on the marine map above.
      </div>
    );
  }

  const risk_score = assessment.risk_score ?? 0;
  const risk_level = assessment.risk_level || 'LOW';
  const confidence = assessment.confidence ?? 0;
  const top_positive_forces = assessment.top_positive_forces || [];
  const top_negative_forces = assessment.top_negative_forces || [];
  const fused_record = assessment.fused_record || {
    wave_height: 0, wind_speed: 0, sst: 0, pressure: 0, swell_height: 0,
    wind_direction: 0, salinity: 0, chlorophyll: 0, current_velocity: 0, trust_score: 0
  };
  const recommended_action = assessment.recommended_action || 'Exercise baseline marine caution.';

  // Color mappings
  const getRiskColor = (level: string) => {
    switch (level) {
      case 'CRITICAL': return { text: 'text-red-700', bg: 'bg-red-100', border: 'border-red-300', shadow: 'shadow-red-500/20' };
      case 'HIGH': return { text: 'text-amber-700', bg: 'bg-amber-100', border: 'border-amber-300', shadow: 'shadow-amber-500/20' };
      case 'MODERATE': return { text: 'text-yellow-700', bg: 'bg-yellow-100', border: 'border-yellow-300', shadow: 'shadow-yellow-500/20' };
      default: return { text: 'text-emerald-700', bg: 'bg-emerald-100', border: 'border-emerald-300', shadow: 'shadow-emerald-500/20' };
    }
  };

  const riskTheme = getRiskColor(risk_level);

  return (
    <div className="space-y-6">
      {/* Top Banner: Score & Recommended Action */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Score Gauge Panel */}
        <div className={`glass-panel p-6 rounded-2xl border ${riskTheme.border} ${riskTheme.shadow} flex flex-col items-center justify-between text-center text-slate-900`}>
          <div className="flex items-center space-x-2 text-xs uppercase tracking-widest font-bold text-slate-700 mb-2">
            <ShieldAlert className={`w-4 h-4 ${riskTheme.text}`} />
            <span>XGBoost Multi-Source Risk Rating</span>
          </div>

          <div className="relative my-4 flex items-center justify-center">
            {/* Circle Risk Meter */}
            <div className="w-36 h-36 rounded-full border-8 border-slate-300 flex items-center justify-center relative">
              <div className={`text-4xl font-black tracking-tight ${riskTheme.text}`}>
                {risk_score.toFixed(1)}
              </div>
              <span className="absolute bottom-6 text-[10px] text-slate-600 uppercase font-bold">
                / 100
              </span>
            </div>
          </div>

          <div className="space-y-1">
            <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold ${riskTheme.bg} ${riskTheme.text} border ${riskTheme.border}`}>
              LEVEL: {risk_level}
            </span>
            <p className="text-xs text-slate-700 mt-1">
              Model Confidence: <span className="text-slate-900 font-extrabold">{(confidence * 100).toFixed(0)}%</span>
            </p>
          </div>
        </div>

        {/* Recommended Action & Key Advisory */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl flex flex-col justify-between space-y-4 text-slate-900">
          <div className="space-y-2">
            <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-cyan-400">
              <CheckCircle className="w-4 h-4 text-cyan-400" />
              <span>Automated Navigation Advisory</span>
            </div>
            <h3 className="text-lg font-bold text-slate-900">
              {recommended_action}
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Synthesized by VARUNA Risk Agent combining Copernicus ocean dynamics, Open-Meteo wind shear, and historical Indian Ocean cyclone patterns.
            </p>
          </div>

          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-slate-800">
            <div className="p-2.5 rounded-xl bg-blue-50 border border-blue-200 text-center">
              <div className="text-[10px] uppercase font-bold text-slate-600">Wave Height</div>
              <div className="text-base font-black text-cyan-700">{fused_record.wave_height ?? 0} m</div>
            </div>
            <div className="p-2.5 rounded-xl bg-blue-50 border border-blue-200 text-center">
              <div className="text-[10px] uppercase font-bold text-slate-600">Wind Speed</div>
              <div className="text-base font-black text-cyan-700">{fused_record.wind_speed ?? 0} kts</div>
            </div>
            <div className="p-2.5 rounded-xl bg-blue-50 border border-blue-200 text-center">
              <div className="text-[10px] uppercase font-bold text-slate-600">Sea Temp (SST)</div>
              <div className="text-base font-black text-cyan-700">{fused_record.sst ?? 0} °C</div>
            </div>
            <div className="p-2.5 rounded-xl bg-blue-50 border border-blue-200 text-center">
              <div className="text-[10px] uppercase font-bold text-slate-600">Pressure</div>
              <div className="text-base font-black text-cyan-700">{fused_record.pressure ?? 0} hPa</div>
            </div>
          </div>
        </div>
      </div>

      {/* SHAP Feature Contribution & Physics Parameters */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* SHAP Positive vs Negative Drivers */}
        <div className="glass-panel p-6 rounded-2xl space-y-4 text-slate-900">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h4 className="font-bold text-slate-100 flex items-center space-x-2 text-sm">
              <TrendingUp className="w-4 h-4 text-cyan-400" />
              <span>SHAP Explainable AI Feature Drivers</span>
            </h4>
            <span className="text-[10px] text-slate-600 font-mono font-semibold">XGBoost Attribution</span>
          </div>

          <div className="space-y-3">
            {/* Risk Increasing Forces */}
            <div>
              <div className="text-xs font-semibold text-red-400 mb-1.5 flex items-center space-x-1">
                <TrendingUp className="w-3.5 h-3.5" />
                <span>Top Risk Increasing Forces (+%)</span>
              </div>
              <div className="space-y-2">
                {top_positive_forces.map((f, i) => (
                    <div key={i} className="p-2.5 rounded-xl bg-red-50 border border-red-200 text-xs">
                    <div className="flex justify-between font-bold text-slate-800">
                      <span>{f.feature} (Value: {f.value})</span>
                      <span className="text-red-700 font-black">+{(f.impact ?? 0).toFixed(1)}%</span>
                    </div>
                    <p className="text-[11px] text-slate-600 mt-0.5">{f.description}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Risk Dampening Forces */}
            {top_negative_forces.length > 0 && (
              <div>
                <div className="text-xs font-semibold text-emerald-400 mb-1.5 flex items-center space-x-1">
                  <TrendingDown className="w-3.5 h-3.5" />
                  <span>Top Risk Mitigating Forces (-%)</span>
                </div>
                <div className="space-y-2">
                  {top_negative_forces.map((f, i) => (
                    <div key={i} className="p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 text-xs">
                      <div className="flex justify-between font-bold text-slate-800">
                        <span>{f.feature} (Value: {f.value})</span>
                        <span className="text-emerald-700 font-black">{(f.impact ?? 0).toFixed(1)}%</span>
                      </div>
                      <p className="text-[11px] text-slate-600 mt-0.5">{f.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Live Fused Marine Parameters Grid */}
        <div className="glass-panel p-6 rounded-2xl space-y-4 text-slate-900">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h4 className="font-bold text-slate-100 flex items-center space-x-2 text-sm">
              <Waves className="w-4 h-4 text-cyan-400" />
              <span>Fused Marine Physical State</span>
            </h4>
            <span className="text-[10px] text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded border border-emerald-300 font-bold">
              TRUST: {((fused_record.trust_score ?? 0) * 100).toFixed(0)}%
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 rounded-xl bg-white border border-slate-300 flex items-center space-x-3">
              <Thermometer className="w-5 h-5 text-amber-400" />
              <div>
                <div className="text-[10px] text-slate-600 uppercase font-bold">Sea Surface Temp</div>
                <div className="text-base font-black text-slate-900">{fused_record.sst ?? 0} °C</div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-white border border-slate-300 flex items-center space-x-3">
              <Waves className="w-5 h-5 text-cyan-400" />
              <div>
                <div className="text-[10px] text-slate-600 uppercase font-bold">Wave / Swell</div>
                <div className="text-base font-black text-slate-900">{fused_record.wave_height ?? 0} m / {fused_record.swell_height ?? 0} m</div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-white border border-slate-300 flex items-center space-x-3">
              <Wind className="w-5 h-5 text-teal-400" />
              <div>
                <div className="text-[10px] text-slate-600 uppercase font-bold">Wind Vector</div>
                <div className="text-base font-black text-slate-900">{fused_record.wind_speed ?? 0} kts ({fused_record.wind_direction ?? 0}°)</div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-white border border-slate-300 flex items-center space-x-3">
              <Gauge className="w-5 h-5 text-purple-400" />
              <div>
                <div className="text-[10px] text-slate-600 uppercase font-bold">Pressure (MSL)</div>
                <div className="text-base font-black text-slate-900">{fused_record.pressure ?? 0} hPa</div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-white border border-slate-300 flex items-center space-x-3">
              <Droplet className="w-5 h-5 text-blue-400" />
              <div>
                <div className="text-[10px] text-slate-600 uppercase font-bold">Salinity / Chlorophyll</div>
                <div className="text-base font-black text-slate-900">{fused_record.salinity ?? 0} PSU / {fused_record.chlorophyll ?? 0} mg/m³</div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-white border border-slate-300 flex items-center space-x-3">
              <CloudRain className="w-5 h-5 text-indigo-400" />
              <div>
                <div className="text-[10px] text-slate-600 uppercase font-bold">Current Velocity</div>
                <div className="text-base font-black text-slate-900">{fused_record.current_velocity ?? 0} m/s</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
