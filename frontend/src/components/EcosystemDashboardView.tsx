import React from 'react';
import { Compass, ExternalLink, Sparkles } from 'lucide-react';

export const EcosystemDashboardView: React.FC = () => {
  return (
    <div className="space-y-4">
      {/* Banner */}
      <div className="glass-panel p-4 rounded-2xl border border-teal-500/30 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-teal-500/20 text-teal-400 border border-teal-500/30">
            <Compass className="w-6 h-6 animate-spin-slow" />
          </div>
          <div>
            <h3 className="text-base font-extrabold text-slate-100 flex items-center space-x-2">
              <span>VARUNA Marine Ecosystem Intelligence Dashboard</span>
              <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-teal-950 text-teal-400 border border-teal-800">
                Interactive Studio
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Multi-Agent Orchestration, Digital Twin What-If Simulation & Collaborative Evidence Fusion
            </p>
          </div>
        </div>

        <a
          href="/ecosystem.html"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-teal-500/20 text-teal-300 border border-teal-500/40 text-xs font-semibold hover:bg-teal-500/30 transition-all"
        >
          <span>Open Fullscreen</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>

      {/* Embedded Iframe */}
      <div className="w-full rounded-2xl overflow-hidden border border-slate-800 shadow-2xl bg-ocean-950" style={{ height: '800px' }}>
        <iframe
          src="/ecosystem.html"
          title="VARUNA Marine Ecosystem Intelligence"
          className="w-full h-full border-0"
        />
      </div>
    </div>
  );
};
