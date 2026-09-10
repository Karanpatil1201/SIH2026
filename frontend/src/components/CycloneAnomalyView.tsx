import React from 'react';
import { Flame, Wind, Gauge, Navigation, ShieldAlert, AlertTriangle, Radio, Activity } from 'lucide-react';
import { CycloneDetails } from '../types';

interface CycloneAnomalyViewProps {
  cycloneData: CycloneDetails | null;
  loading: boolean;
}

export const CycloneAnomalyView: React.FC<CycloneAnomalyViewProps> = ({ cycloneData, loading }) => {
  if (loading || !cycloneData) {
    return (
      <div className="glass-panel p-8 rounded-2xl flex flex-col items-center justify-center space-y-4 min-h-[300px]">
        <div className="w-10 h-10 border-4 border-amber-500/30 border-t-amber-400 rounded-full animate-spin" />
        <p className="text-sm font-semibold text-amber-300">Tracking Cyclonic Storm Systems & Sensor Anomalies...</p>
      </div>
    );
  }

  const { name, cyclone_id, status, current_location, max_sustained_wind_kmh, central_pressure_hpa, movement_speed_kmh, movement_direction, affected_ports, historical_track, projected_track } = cycloneData;

  // Mock Anomaly Logs detected via Isolation Forest model
  const anomalyLogs = [
    { id: 'ANO-881', type: 'Sudden Sea Surface Temp Spike (+2.4°C / 3h)', lat: 16.8, lon: 86.5, severity: 'CRITICAL', confidence: 0.94, time: '20 mins ago' },
    { id: 'ANO-882', type: 'Pressure Drop Anomaly (-6.2 hPa / 2h)', lat: 17.1, lon: 85.8, severity: 'HIGH', confidence: 0.91, time: '45 mins ago' },
    { id: 'ANO-883', type: 'Satellite SAR Current Velocity Shear', lat: 15.9, lon: 87.1, severity: 'MODERATE', confidence: 0.86, time: '2 hours ago' }
  ];

  return (
    <div className="space-y-6">
      {/* Cyclone Primary Monitor Header Card */}
      <div className="glass-panel p-6 rounded-2xl border border-red-500/30 shadow-2xl shadow-red-500/10 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div className="flex items-center space-x-3">
            <div className="p-3 rounded-2xl bg-red-500/20 text-red-400 border border-red-500/30 animate-pulse">
              <Flame className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-xl font-extrabold text-slate-100">{name}</h3>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-red-950 text-red-400 border border-red-800">
                  {status}
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                ID: {cyclone_id} | Eye Lat: {current_location.lat}° N, Lon: {current_location.lon}° E
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className="px-3 py-1.5 rounded-xl bg-ocean-900 border border-slate-800 text-xs font-semibold text-slate-300 flex items-center space-x-1.5">
              <Radio className="w-3.5 h-3.5 text-emerald-400 animate-ping" />
              <span>Live Satellite Radar Feed</span>
            </span>
          </div>
        </div>

        {/* Cyclone Key Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-ocean-900/80 border border-slate-800 space-y-1">
            <div className="text-xs font-semibold text-slate-400 flex items-center space-x-1">
              <Wind className="w-4 h-4 text-red-400" />
              <span>Max Sustained Wind</span>
            </div>
            <div className="text-xl font-extrabold text-red-400">{max_sustained_wind_kmh} km/h</div>
            <p className="text-[10px] text-slate-500">Severe Cyclonic Storm Class</p>
          </div>

          <div className="p-4 rounded-xl bg-ocean-900/80 border border-slate-800 space-y-1">
            <div className="text-xs font-semibold text-slate-400 flex items-center space-x-1">
              <Gauge className="w-4 h-4 text-amber-400" />
              <span>Central Pressure</span>
            </div>
            <div className="text-xl font-extrabold text-amber-400">{central_pressure_hpa} hPa</div>
            <p className="text-[10px] text-slate-500">Rapid Depressurization</p>
          </div>

          <div className="p-4 rounded-xl bg-ocean-900/80 border border-slate-800 space-y-1">
            <div className="text-xs font-semibold text-slate-400 flex items-center space-x-1">
              <Navigation className="w-4 h-4 text-cyan-400" />
              <span>Movement Speed & Heading</span>
            </div>
            <div className="text-xl font-extrabold text-cyan-400">{movement_speed_kmh} km/h ({movement_direction})</div>
            <p className="text-[10px] text-slate-500">North-West Trajectory</p>
          </div>

          <div className="p-4 rounded-xl bg-ocean-900/80 border border-slate-800 space-y-1">
            <div className="text-xs font-semibold text-slate-400 flex items-center space-x-1">
              <ShieldAlert className="w-4 h-4 text-purple-400" />
              <span>High Alert Coastal Ports</span>
            </div>
            <div className="text-sm font-extrabold text-purple-300 truncate">{affected_ports.join(', ')}</div>
            <p className="text-[10px] text-slate-500">Coast Guard Signal 4 Raised</p>
          </div>
        </div>
      </div>

      {/* Historical Track & Projected Path Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Track Forecast Table */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <h4 className="font-bold text-slate-100 text-sm border-b border-slate-800 pb-3 flex items-center space-x-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            <span>Projected Storm Track & Intensity Forecast</span>
          </h4>

          <div className="space-y-2 max-h-64 overflow-y-auto">
            {projected_track.map((pt, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-ocean-900/60 border border-slate-800 flex items-center justify-between text-xs">
                <div>
                  <div className="font-bold text-slate-200">{pt.category}</div>
                  <div className="text-[11px] text-slate-400 font-mono mt-0.5">
                    Lat: {pt.lat}° N, Lon: {pt.lon}° E
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-red-400">{pt.max_wind_knots} Knots</div>
                  <div className="text-[11px] text-amber-400 font-mono">{pt.pressure_hpa} hPa</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Isolation Forest Anomaly Log */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <h4 className="font-bold text-slate-100 text-sm border-b border-slate-800 pb-3 flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>ML Isolation Forest Anomaly Feed</span>
          </h4>

          <div className="space-y-3">
            {anomalyLogs.map((ano) => (
              <div key={ano.id} className="p-3 rounded-xl bg-amber-950/20 border border-amber-900/40 text-xs space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-amber-400 font-extrabold">{ano.id}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-950 text-red-400 border border-red-800">
                    {ano.severity}
                  </span>
                </div>
                <div className="font-bold text-slate-200">{ano.type}</div>
                <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                  <span>Loc: ({ano.lat}°, {ano.lon}°)</span>
                  <span>Confidence: {(ano.confidence * 100).toFixed(0)}% • {ano.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
