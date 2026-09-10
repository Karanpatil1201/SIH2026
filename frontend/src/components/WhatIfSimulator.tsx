import React, { useState } from 'react';
import { Sliders, Play, TrendingUp, AlertTriangle, ShieldCheck, RefreshCw } from 'lucide-react';
import { WhatIfRequest, WhatIfResponse } from '../types';

interface WhatIfSimulatorProps {
  lat: number;
  lon: number;
  onRunSimulation: (req: WhatIfRequest) => Promise<WhatIfResponse>;
}

export const WhatIfSimulator: React.FC<WhatIfSimulatorProps> = ({ lat, lon, onRunSimulation }) => {
  const [waveIncrease, setWaveIncrease] = useState<number>(50);
  const [windIncrease, setWindIncrease] = useState<number>(30);
  const [pressureDrop, setPressureDrop] = useState<number>(15);
  const [cycloneProb, setCycloneProb] = useState<number>(40);

  const [loading, setLoading] = useState<boolean>(false);
  const [simulationResult, setSimulationResult] = useState<WhatIfResponse | null>(null);

  const handleSimulate = async () => {
    setLoading(true);
    try {
      const res = await onRunSimulation({
        lat,
        lon,
        wave_increase_pct: waveIncrease,
        wind_increase_pct: windIncrease,
        pressure_drop_hpa: pressureDrop,
        cyclone_prob_increase: cycloneProb,
      });
      setSimulationResult(res);
    } catch (err) {
      console.error('Simulation failed', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* What-If Controls Header */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2 font-bold text-slate-100 text-sm">
            <Sliders className="w-5 h-5 text-purple-400" />
            <span>Interactive Marine Perturbation & What-If Scenario Builder</span>
          </div>
          <span className="text-[10px] text-purple-400 bg-purple-950/60 px-2 py-0.5 rounded border border-purple-800 font-mono">
            Synthetic Physics Simulator
          </span>
        </div>

        {/* Sliders Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
          {/* Wave Height Increase Slider */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold">
              <span className="text-slate-300">Wave Height Increase (% Surge)</span>
              <span className="text-cyan-400 font-bold">+{waveIncrease}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="200"
              value={waveIncrease}
              onChange={(e) => setWaveIncrease(Number(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
            />
          </div>

          {/* Wind Speed Surge Slider */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold">
              <span className="text-slate-300">Wind Speed Surge (% Gust)</span>
              <span className="text-teal-400 font-bold">+{windIncrease}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="150"
              value={windIncrease}
              onChange={(e) => setWindIncrease(Number(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-teal-400"
            />
          </div>

          {/* Atmospheric Pressure Drop Slider */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold">
              <span className="text-slate-300">Atmospheric Pressure Drop (hPa)</span>
              <span className="text-amber-400 font-bold">-{pressureDrop} hPa</span>
            </div>
            <input
              type="range"
              min="0"
              max="40"
              value={pressureDrop}
              onChange={(e) => setPressureDrop(Number(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-400"
            />
          </div>

          {/* Cyclone Threat Index */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold">
              <span className="text-slate-300">Cyclone Storm Risk Forcing</span>
              <span className="text-red-400 font-bold">+{cycloneProb}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={cycloneProb}
              onChange={(e) => setCycloneProb(Number(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-red-400"
            />
          </div>
        </div>

        {/* Action Button */}
        <div className="pt-2 flex justify-end">
          <button
            onClick={handleSimulate}
            disabled={loading}
            className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-purple-500/20 border border-purple-400/30 transition-all disabled:opacity-50"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-white" />}
            <span>{loading ? 'Running Physics Model...' : 'Execute What-If Simulation'}</span>
          </button>
        </div>
      </div>

      {/* Simulation Output Cards */}
      {simulationResult && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Original vs Simulated Risk */}
            <div className="glass-panel p-6 rounded-2xl flex flex-col justify-between space-y-4">
              <div className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Original Baseline Risk
              </div>
              <div className="text-4xl font-extrabold text-slate-300">
                {simulationResult.original_risk.toFixed(1)} <span className="text-xs text-slate-500">/ 100</span>
              </div>
              <span className="inline-block w-max px-2.5 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300 border border-slate-700">
                STATUS: {simulationResult.original_level}
              </span>
            </div>

            {/* Simulated Risk Outcome */}
            <div className="glass-panel p-6 rounded-2xl border border-red-500/40 shadow-xl shadow-red-500/10 flex flex-col justify-between space-y-4">
              <div className="text-xs font-bold uppercase tracking-wider text-red-400 flex items-center space-x-1">
                <TrendingUp className="w-4 h-4" />
                <span>Simulated Perturbed Risk</span>
              </div>
              <div className="text-4xl font-extrabold text-red-400">
                {simulationResult.simulated_risk.toFixed(1)} <span className="text-xs text-red-500">/ 100</span>
              </div>
              <span className="inline-block w-max px-2.5 py-0.5 rounded text-[10px] font-bold bg-red-950 text-red-400 border border-red-800">
                NEW LEVEL: {simulationResult.simulated_level}
              </span>
            </div>

            {/* Risk Delta Surge */}
            <div className="glass-panel p-6 rounded-2xl flex flex-col justify-between space-y-4">
              <div className="text-xs font-bold uppercase tracking-wider text-amber-400">
                Projected Risk Delta (+ Surge)
              </div>
              <div className="text-4xl font-extrabold text-amber-400">
                +{simulationResult.risk_delta.toFixed(1)} %
              </div>
              <p className="text-[11px] text-slate-400">
                Non-linear XGBoost risk escalation under compound atmospheric stress.
              </p>
            </div>
          </div>

          {/* Explanation Card */}
          <div className="glass-panel p-6 rounded-2xl space-y-3">
            <h4 className="font-bold text-slate-100 text-sm flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <span>Simulation Impact Analysis & Route Degradation</span>
            </h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              {simulationResult.explanation}
            </p>
            <div className="p-3 rounded-xl bg-ocean-900/80 border border-slate-800 text-xs font-mono text-cyan-300">
              {simulationResult.affected_route_impact}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
