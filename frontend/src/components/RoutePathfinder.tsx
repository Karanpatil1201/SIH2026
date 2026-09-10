import React, { useState } from 'react';
import { Navigation2, ShieldCheck, AlertCircle, Clock, MapPin, ArrowRight, Anchor, CheckCircle2 } from 'lucide-react';
import { RouteComparisonResponse, RouteOption } from '../types';

interface RoutePathfinderProps {
  routesData: RouteComparisonResponse | null;
  loading: boolean;
  onFetchRoutes: (originLat: number, originLon: number, destLat: number, destLon: number, originName: string, destName: string) => void;
}

const PRESET_PORTS = [
  { name: 'Mumbai Port', lat: 18.9667, lon: 72.8333 },
  { name: 'Goa Port (Mormugao)', lat: 15.4989, lon: 73.8278 },
  { name: 'Kochi Port', lat: 9.9667, lon: 76.2667 },
  { name: 'Lakshadweep (Kavaratti)', lat: 10.5667, lon: 72.6417 },
  { name: 'Visakhapatnam Port', lat: 17.6868, lon: 83.2185 },
  { name: 'Port Blair (Andaman)', lat: 11.6234, lon: 92.7264 }
];

export const RoutePathfinder: React.FC<RoutePathfinderProps> = ({ routesData, loading, onFetchRoutes }) => {
  const [originIndex, setOriginIndex] = useState<number>(0);
  const [destIndex, setDestIndex] = useState<number>(1);

  const handleCalculate = () => {
    const orig = PRESET_PORTS[originIndex];
    const dest = PRESET_PORTS[destIndex];
    onFetchRoutes(orig.lat, orig.lon, dest.lat, dest.lon, orig.name, dest.name);
  };

  return (
    <div className="space-y-6">
      {/* Route Control Panel */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2 font-bold text-slate-100 text-sm">
            <Navigation2 className="w-5 h-5 text-cyan-400" />
            <span>VARUNA Maritime Pathfinder & Dynamic Risk Routing</span>
          </div>
          <span className="text-[10px] text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800">
            A* Marine Pathfinder Engine
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          {/* Origin Picker */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center space-x-1">
              <MapPin className="w-3.5 h-3.5 text-emerald-400" />
              <span>Origin Port</span>
            </label>
            <select
              value={originIndex}
              onChange={(e) => setOriginIndex(Number(e.target.value))}
              className="w-full bg-ocean-900 border border-slate-700 rounded-xl px-3 py-2 text-xs font-semibold text-slate-200 focus:outline-none focus:border-cyan-400"
            >
              {PRESET_PORTS.map((p, idx) => (
                <option key={idx} value={idx} disabled={idx === destIndex}>
                  {p.name} ({p.lat.toFixed(2)}°, {p.lon.toFixed(2)}°)
                </option>
              ))}
            </select>
          </div>

          {/* Destination Picker */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center space-x-1">
              <Anchor className="w-3.5 h-3.5 text-cyan-400" />
              <span>Destination Port</span>
            </label>
            <select
              value={destIndex}
              onChange={(e) => setDestIndex(Number(e.target.value))}
              className="w-full bg-ocean-900 border border-slate-700 rounded-xl px-3 py-2 text-xs font-semibold text-slate-200 focus:outline-none focus:border-cyan-400"
            >
              {PRESET_PORTS.map((p, idx) => (
                <option key={idx} value={idx} disabled={idx === originIndex}>
                  {p.name} ({p.lat.toFixed(2)}°, {p.lon.toFixed(2)}°)
                </option>
              ))}
            </select>
          </div>

          {/* Calculate Button */}
          <button
            onClick={handleCalculate}
            disabled={loading}
            className="flex items-center justify-center space-x-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-bold shadow-lg shadow-cyan-500/20 border border-cyan-300/30 transition-all disabled:opacity-50"
          >
            <span>{loading ? 'Optimizing Route...' : 'Find Safest Shipping Route'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Routes Comparison Results */}
      {routesData && (
        <div className="space-y-6">
          {/* Recommendation Banner */}
          <div className="p-4 rounded-2xl glass-panel-glow border border-cyan-500/40 flex items-start space-x-3">
            <CheckCircle2 className="w-6 h-6 text-cyan-400 shrink-0 mt-0.5" />
            <div>
              <div className="text-xs uppercase font-extrabold tracking-wider text-cyan-400">
                Recommended Shipping Strategy
              </div>
              <p className="text-sm font-bold text-slate-100 mt-0.5">
                {routesData.recommendation_reason}
              </p>
            </div>
          </div>

          {/* Route Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {routesData.routes.map((route: RouteOption) => {
              const isRecommended = route.route_id === routesData.recommended_route_id;
              return (
                <div
                  key={route.route_id}
                  className={`glass-panel p-6 rounded-2xl space-y-4 border transition-all ${
                    isRecommended
                      ? 'border-teal-400/60 shadow-xl shadow-teal-500/10 bg-ocean-900/90'
                      : 'border-slate-800'
                  }`}
                >
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <div>
                      <h4 className="font-bold text-slate-100 text-base flex items-center space-x-2">
                        <span>{route.name}</span>
                      </h4>
                      <p className="text-xs text-slate-400 mt-0.5">
                        Distance: <span className="text-slate-200 font-semibold">{route.total_distance_km} km</span>
                      </p>
                    </div>
                    {isRecommended ? (
                      <span className="px-3 py-1 rounded-full bg-teal-500/20 text-teal-400 border border-teal-500/40 text-xs font-bold flex items-center space-x-1">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        <span>RECOMMENDED</span>
                      </span>
                    ) : (
                      <span className="px-3 py-1 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/40 text-xs font-bold flex items-center space-x-1">
                        <AlertCircle className="w-3.5 h-3.5" />
                        <span>HIGH WAVE EXPOSURE</span>
                      </span>
                    )}
                  </div>

                  {/* Route Stats */}
                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div className="p-3 rounded-xl bg-ocean-950/60 border border-slate-800">
                      <div className="text-[10px] uppercase font-bold text-slate-400">Estimated Travel Time</div>
                      <div className="text-sm font-extrabold text-cyan-300 flex items-center space-x-1 mt-0.5">
                        <Clock className="w-3.5 h-3.5" />
                        <span>{route.estimated_time_hours.toFixed(1)} Hours</span>
                      </div>
                    </div>

                    <div className="p-3 rounded-xl bg-ocean-950/60 border border-slate-800">
                      <div className="text-[10px] uppercase font-bold text-slate-400">Average Route Risk</div>
                      <div className={`text-sm font-extrabold mt-0.5 ${route.average_risk_score > 50 ? 'text-amber-400' : 'text-emerald-400'}`}>
                        {route.average_risk_score.toFixed(1)} / 100
                      </div>
                    </div>

                    <div className="p-3 rounded-xl bg-ocean-950/60 border border-slate-800">
                      <div className="text-[10px] uppercase font-bold text-slate-400">Max Wave Elevation</div>
                      <div className="text-sm font-extrabold text-slate-200 mt-0.5">
                        {route.max_wave_height} m
                      </div>
                    </div>

                    <div className="p-3 rounded-xl bg-ocean-950/60 border border-slate-800">
                      <div className="text-[10px] uppercase font-bold text-slate-400">Storm Exposure %</div>
                      <div className="text-sm font-extrabold text-slate-200 mt-0.5">
                        {route.storm_exposure_pct}%
                      </div>
                    </div>
                  </div>

                  {/* Waypoint Details List */}
                  <div>
                    <h5 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                      Waypoint Risk Breakdown ({route.waypoints.length} Points)
                    </h5>
                    <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
                      {route.waypoints.map((wpt, idx) => (
                        <div key={idx} className="flex items-center justify-between p-2 rounded-lg bg-ocean-950/40 text-[11px] border border-slate-800/80">
                          <span className="font-mono text-slate-300">
                            WPT #{idx + 1} ({wpt.lat.toFixed(2)}°, {wpt.lon.toFixed(2)}°)
                          </span>
                          <span className={`font-bold ${wpt.risk_score > 50 ? 'text-red-400' : 'text-emerald-400'}`}>
                            Risk: {wpt.risk_score.toFixed(0)} | Wave: {wpt.wave_height}m
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
