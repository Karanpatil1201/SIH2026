import React from 'react';
import { Fish, Waves, Thermometer, ShieldCheck, AlertCircle, Sparkles, CheckCircle2 } from 'lucide-react';
import { FishingZone } from '../types';
import { useLanguage } from '../i18n';

interface FishingAdvisoryViewProps {
  fishingData: FishingZone | null;
  loading: boolean;
}

export const FishingAdvisoryView: React.FC<FishingAdvisoryViewProps> = ({ fishingData, loading }) => {
  const { t } = useLanguage();
  if (loading || !fishingData) {
    return (
      <div className="glass-panel p-8 rounded-2xl flex flex-col items-center justify-center space-y-4 min-h-[300px]">
        <div className="w-10 h-10 border-4 border-emerald-500/30 border-t-emerald-400 rounded-full animate-spin" />
        <p className="text-sm font-semibold text-emerald-300">{t('loading')}</p>
      </div>
    );
  }

  const pfz_indicator_score = fishingData.pfz_indicator_score ?? 0;
  const sst_gradient = fishingData.sst_gradient ?? 0;
  const chlorophyll_concentration = fishingData.chlorophyll_concentration ?? 0;
  const current_convergence = fishingData.current_convergence ?? 0;
  const confidence = fishingData.confidence ?? 0;
  const recommended_target_species = fishingData.recommended_target_species || ['Mackerel', 'Sardine', 'Tuna'];
  const safety_advisory = fishingData.safety_advisory || 'Exercise baseline marine caution.';
  const zone_id = fishingData.zone_id || 'PFZ_ZONE';

  return (
    <div className="space-y-6">
      {/* Top PFZ Potential Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-emerald-500/30 shadow-2xl shadow-emerald-500/10 space-y-4 text-slate-900">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div className="flex items-center space-x-3">
            <div className="p-3 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              <Fish className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-xl font-extrabold text-slate-900">{t('fishingZones')} (PFZ)</h3>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-emerald-950 text-emerald-400 border border-emerald-800">
                  {zone_id}
                </span>
              </div>
              <p className="text-xs text-slate-600 mt-0.5">
                Derived via Sentinel-3 OLCI Chlorophyll-a & MODIS SST thermal front alignment.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="text-right">
              <div className="text-[10px] uppercase font-bold text-slate-600">{t('pfzRating')}</div>
              <div className="text-4xl font-black text-emerald-700 tracking-tight">
                {pfz_indicator_score.toFixed(1)}%
              </div>
            </div>
          </div>
        </div>

        {/* Safety Clearance Banner */}
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 flex items-start space-x-3">
          <ShieldCheck className="w-6 h-6 text-emerald-400 shrink-0 mt-0.5" />
          <div>
            <div className="text-xs font-extrabold uppercase tracking-wider text-emerald-700">
              {t('safetyAdvisory')}
            </div>
            <p className="text-sm font-semibold text-slate-800 mt-0.5">
              {safety_advisory}
            </p>
          </div>
        </div>
      </div>

      {/* Target Species & Physics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recommended Species Card */}
        <div className="glass-panel p-6 rounded-2xl space-y-4 text-slate-900">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h4 className="font-bold text-slate-900 text-sm flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-emerald-400" />
              <span>{t('recommendedSpecies')}</span>
            </h4>
            <span className="text-[10px] text-emerald-700 font-mono font-bold">{t('highCatchProbability')}</span>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {recommended_target_species.map((species, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-white border border-slate-300 flex items-center space-x-3 hover:border-emerald-500/40 transition-all">
                <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
                  <Fish className="w-5 h-5" />
                </div>
                <div>
                  <div className="font-bold text-slate-900 text-sm">{species}</div>
                  <div className="text-[10px] text-slate-600">Pelagic Catch Group</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Oceanographic Front Metrics */}
        <div className="glass-panel p-6 rounded-2xl space-y-4 text-slate-900">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h4 className="font-bold text-slate-900 text-sm flex items-center space-x-2">
              <Waves className="w-4 h-4 text-cyan-400" />
              <span>{t('oceanMetrics')}</span>
            </h4>
            <span className="text-[10px] text-slate-600 font-mono font-bold">{t('confidence')}: {(confidence * 100).toFixed(0)}%</span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="p-3.5 rounded-xl bg-white border border-slate-300 flex justify-between items-center">
              <div>
                <div className="font-bold text-slate-900">Chlorophyll-a Concentration</div>
                <div className="text-[11px] text-slate-600">Plankton bloom indicator for fish aggregation</div>
              </div>
              <div className="text-lg font-black text-emerald-700">{chlorophyll_concentration} mg/m³</div>
            </div>

            <div className="p-3.5 rounded-xl bg-white border border-slate-300 flex justify-between items-center">
              <div>
                <div className="font-bold text-slate-900">Thermal Front SST Gradient</div>
                <div className="text-[11px] text-slate-600">Temperature boundary differential</div>
              </div>
              <div className="text-lg font-black text-cyan-700">{sst_gradient} °C / 10km</div>
            </div>

            <div className="p-3.5 rounded-xl bg-white border border-slate-300 flex justify-between items-center">
              <div>
                <div className="font-bold text-slate-900">Ocean Current Convergence Index</div>
                <div className="text-[11px] text-slate-600">Surface flow confluence zone</div>
              </div>
              <div className="text-lg font-black text-purple-700">{current_convergence}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
