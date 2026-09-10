import React from 'react';
import { Activity, ShieldCheck, Database, Server, Cpu, CheckCircle2, RefreshCw } from 'lucide-react';
import { EvaluationDashboardResponse, SystemHealthResponse } from '../types';

interface SystemHealthViewProps {
  modelStatus: EvaluationDashboardResponse | null;
  systemHealth: SystemHealthResponse | null;
  loading: boolean;
}

export const SystemHealthView: React.FC<SystemHealthViewProps> = ({ modelStatus, systemHealth, loading }) => {
  if (loading || !modelStatus || !systemHealth) {
    return (
      <div className="glass-panel p-8 rounded-2xl flex flex-col items-center justify-center space-y-4 min-h-[300px]">
        <div className="w-10 h-10 border-4 border-cyan-500/30 border-t-cyan-400 rounded-full animate-spin" />
        <p className="text-sm font-semibold text-cyan-300">Auditing Data Provider Latency & ML Model Accuracy Matrix...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* System Operational Overview Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-emerald-500/30 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div className="flex items-center space-x-3">
            <div className="p-3 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              <Activity className="w-7 h-7" />
            </div>
            <div>
              <h3 className="text-lg font-extrabold text-slate-100">VARUNA System Command & Data Health</h3>
              <p className="text-xs text-slate-400">Live API Provider Latency & Ground-Truth Evaluator</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <span className="px-3 py-1.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 text-xs font-bold flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <span>SYSTEM {systemHealth.status}</span>
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
          <div className="p-3 rounded-xl bg-ocean-900/60 border border-slate-800">
            <div className="text-[10px] uppercase font-bold text-slate-400">Database Engine</div>
            <div className="text-sm font-extrabold text-slate-200 mt-0.5">{systemHealth.database}</div>
          </div>
          <div className="p-3 rounded-xl bg-ocean-900/60 border border-slate-800">
            <div className="text-[10px] uppercase font-bold text-slate-400">Operational Mode</div>
            <div className="text-sm font-extrabold text-cyan-300 mt-0.5">{systemHealth.operational_mode}</div>
          </div>
          <div className="p-3 rounded-xl bg-ocean-900/60 border border-slate-800">
            <div className="text-[10px] uppercase font-bold text-slate-400">Evaluated Ground Truth Samples</div>
            <div className="text-sm font-extrabold text-purple-300 mt-0.5">{modelStatus.ground_truth_sample_count} Records</div>
          </div>
        </div>
      </div>

      {/* Model Benchmark Grid */}
      <div className="space-y-4">
        <h4 className="font-bold text-slate-100 text-sm flex items-center space-x-2">
          <Cpu className="w-4 h-4 text-cyan-400" />
          <span>Machine Learning Model Accuracy Benchmarks</span>
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {modelStatus.models.map((m, idx) => (
            <div key={idx} className="glass-panel p-6 rounded-2xl space-y-4 border border-slate-800">
              <div className="flex justify-between items-start border-b border-slate-800 pb-3">
                <div>
                  <h5 className="font-bold text-slate-100 text-base">{m.model_name}</h5>
                  <p className="text-xs text-slate-400">{m.task}</p>
                </div>
                <span className="px-2.5 py-1 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 text-xs font-mono font-bold">
                  {(m.accuracy * 100).toFixed(1)}% ACC
                </span>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-3 gap-3 text-center text-xs">
                <div className="p-2.5 rounded-xl bg-ocean-900/80 border border-slate-800">
                  <div className="text-[10px] uppercase text-slate-400 font-semibold">Precision</div>
                  <div className="text-sm font-extrabold text-slate-200 font-mono">{(m.precision * 100).toFixed(1)}%</div>
                </div>
                <div className="p-2.5 rounded-xl bg-ocean-900/80 border border-slate-800">
                  <div className="text-[10px] uppercase text-slate-400 font-semibold">Recall</div>
                  <div className="text-sm font-extrabold text-slate-200 font-mono">{(m.recall * 100).toFixed(1)}%</div>
                </div>
                <div className="p-2.5 rounded-xl bg-ocean-900/80 border border-slate-800">
                  <div className="text-[10px] uppercase text-slate-400 font-semibold">F1 Score</div>
                  <div className="text-sm font-extrabold text-teal-400 font-mono">{(m.f1_score * 100).toFixed(1)}%</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Data Source Providers Matrix */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <h4 className="font-bold text-slate-100 text-sm flex items-center space-x-2 border-b border-slate-800 pb-3">
          <Server className="w-4 h-4 text-emerald-400" />
          <span>Ingestion Pipelines & External Provider Health</span>
        </h4>

        <div className="space-y-3">
          {systemHealth.sources.map((src, i) => (
            <div key={i} className="p-3.5 rounded-xl bg-ocean-900/60 border border-slate-800 flex items-center justify-between text-xs">
              <div className="flex items-center space-x-3">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <div>
                  <div className="font-bold text-slate-100">{src.name}</div>
                  <div className="text-[11px] text-slate-400">{src.provider_type}</div>
                </div>
              </div>

              <div className="flex items-center space-x-4 text-right">
                <div>
                  <div className="font-mono text-cyan-400 font-bold">{src.latency_ms} ms</div>
                  <div className="text-[10px] text-slate-500 font-mono">Latency</div>
                </div>
                <div>
                  <div className="font-mono text-emerald-400 font-bold">{(src.trust_reliability * 100).toFixed(0)}%</div>
                  <div className="text-[10px] text-slate-500 font-mono">Reliability</div>
                </div>
                <span className="px-2.5 py-1 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-bold text-[10px]">
                  {src.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
