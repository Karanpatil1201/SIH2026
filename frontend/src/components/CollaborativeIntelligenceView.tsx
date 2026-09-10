import React, { useState, useEffect } from 'react';
import {
  ShieldCheck, AlertTriangle, XCircle, Brain, Dna, Swords, History,
  Clock, Sliders, ChevronDown, ChevronUp, RefreshCw, Anchor, Compass,
  Wind, Waves, Thermometer, CheckCircle2, ArrowRight, Zap, Target,
  Info, Eye, BarChart3, Sparkles
} from 'lucide-react';
import { varunaAPI } from '../services/api';
import {
  MarineWhyEngine, DecisionDNA, AgentDissentResponse, MarineTimelineResponse,
  MarineMissionProfileResponse, WhatIfEnhancedResponse
} from '../types';

interface CollaborativeIntelligenceViewProps {
  initialLat: number;
  initialLon: number;
}

const VESSEL_OPTIONS = [
  'Fishing Boat (Motorized)',
  'Artisanal / Canoe Craft',
  'Deep-Sea Mechanized Trawler',
  'Coastal Patrol Vessel',
  'Cargo / Passenger Craft'
];

const ACTIVITY_OPTIONS = [
  'Pelagic Fishing (Tuna / Mackerel)',
  'Demersal Gillnetting',
  'Coastal Harbor Transit',
  'Oceanographic Survey',
  'Night Fishing Run'
];

export const CollaborativeIntelligenceView: React.FC<CollaborativeIntelligenceViewProps> = ({
  initialLat = 18.9667,
  initialLon = 72.8333
}) => {
  const [lat, setLat] = useState<number>(initialLat);
  const [lon, setLon] = useState<number>(initialLon);
  const [activeSubTab, setActiveSubTab] = useState<'decision' | 'dissent' | 'timeline' | 'twin' | 'whatif'>('decision');

  // Mission Profile (Decision Twin) Form
  const [departureTime, setDepartureTime] = useState<string>('05:00 AM');
  const [vesselType, setVesselType] = useState<string>('Fishing Boat (Motorized)');
  const [durationHours, setDurationHours] = useState<number>(6.0);
  const [targetActivity, setTargetActivity] = useState<string>('Pelagic Fishing (Tuna / Mackerel)');

  // What-If Form
  const [baselineTime, setBaselineTime] = useState<string>('08:00 AM');
  const [scenarioTime, setScenarioTime] = useState<string>('05:00 AM');
  const [waveSurge, setWaveSurge] = useState<number>(30);
  const [windSurge, setWindSurge] = useState<number>(20);
  const [pressDrop, setPressDrop] = useState<number>(10);

  // Loaded Data States
  const [loading, setLoading] = useState<boolean>(false);
  const [whyData, setWhyData] = useState<MarineWhyEngine | null>(null);
  const [dnaData, setDnaData] = useState<DecisionDNA | null>(null);
  const [dissentData, setDissentData] = useState<AgentDissentResponse | null>(null);
  const [timelineData, setTimelineData] = useState<MarineTimelineResponse | null>(null);
  const [missionData, setMissionData] = useState<MarineMissionProfileResponse | null>(null);
  const [whatIfData, setWhatIfData] = useState<WhatIfEnhancedResponse | null>(null);
  const [dnaExpanded, setDnaExpanded] = useState<boolean>(false);

  // Load all intelligence on coordinate change
  const loadIntelligence = async (targetLat: number, targetLon: number) => {
    setLoading(true);
    try {
      const [why, dna, dissent, timeline, mission, whatif] = await Promise.all([
        varunaAPI.getMarineWhy(targetLat, targetLon),
        varunaAPI.getMarineDecisionDNA(targetLat, targetLon),
        varunaAPI.getAgentDissent(targetLat, targetLon),
        varunaAPI.getMarineTimeline(targetLat, targetLon),
        varunaAPI.analyzeMissionProfile({
          latitude: targetLat,
          longitude: targetLon,
          departure_time: departureTime,
          vessel_type: vesselType,
          mission_duration_hours: durationHours,
          target_activity: targetActivity
        }),
        varunaAPI.runWhatIfEnhanced({
          lat: targetLat,
          lon: targetLon,
          baseline_departure: baselineTime,
          scenario_departure: scenarioTime,
          wave_increase_pct: waveSurge,
          wind_increase_pct: windSurge,
          pressure_drop_hpa: pressDrop
        })
      ]);

      setWhyData(why);
      setDnaData(dna);
      setDissentData(dissent);
      setTimelineData(timeline);
      setMissionData(mission);
      setWhatIfData(whatif);
    } catch (err) {
      console.error('Failed to load collaborative intelligence', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadIntelligence(lat, lon);
  }, [lat, lon]);

  const handleSimulateWhatIf = async () => {
    setLoading(true);
    try {
      const res = await varunaAPI.runWhatIfEnhanced({
        lat,
        lon,
        baseline_departure: baselineTime,
        scenario_departure: scenarioTime,
        wave_increase_pct: waveSurge,
        wind_increase_pct: windSurge,
        pressure_drop_hpa: pressDrop
      });
      setWhatIfData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateMission = async () => {
    setLoading(true);
    try {
      const res = await varunaAPI.analyzeMissionProfile({
        latitude: lat,
        longitude: lon,
        departure_time: departureTime,
        vessel_type: vesselType,
        mission_duration_hours: durationHours,
        target_activity: targetActivity
      });
      setMissionData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  // Badges & styling
  const rec = whyData?.recommendation || dnaData?.recommendation || 'RECOMMENDED';
  const recBadge =
    rec === 'RECOMMENDED'
      ? { bg: 'bg-emerald-50 text-emerald-800 border-emerald-300', dot: 'bg-emerald-500', text: 'text-emerald-700' }
      : rec === 'CAUTION'
      ? { bg: 'bg-amber-50 text-amber-800 border-amber-300', dot: 'bg-amber-500', text: 'text-amber-700' }
      : { bg: 'bg-red-50 text-red-800 border-red-300', dot: 'bg-red-500', text: 'text-red-700' };

  return (
    <div className="space-y-5 pb-8">

      {/* ── Top Overview Banner ─────────────────────────────────── */}
      <div className="rounded-3xl p-6 bg-white border border-blue-100 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-[11px] font-mono font-bold text-blue-600 uppercase tracking-widest mb-1">
              <Sparkles className="w-3.5 h-3.5 text-blue-600" />
              <span>SIH26176 / Collaborative Agentic AI for Marine Ecosystem Reasoning</span>
            </div>
            <h1 className="text-2xl font-black text-blue-950">Marine Collaborative AI Suite</h1>
            <p className="text-xs text-slate-500 mt-1 max-w-2xl">
              Transparent multi-agent decision architecture: Marine WHY Engine, Decision DNA,
              Agent Dissent & Conflict Resolution, Temporal Marine Timeline, and Decision Twin.
            </p>
          </div>

          {/* Quick Coordinate Controller & Refresh */}
          <div className="flex items-center gap-2 flex-wrap">
            <div className="flex items-center space-x-2 bg-blue-50/80 px-3 py-1.5 rounded-xl border border-blue-200 text-xs">
              <span className="font-bold text-slate-500">Sector:</span>
              <span className="font-mono font-bold text-blue-950">{lat.toFixed(4)}°N, {lon.toFixed(4)}°E</span>
            </div>
            <button
              onClick={() => loadIntelligence(lat, lon)}
              disabled={loading}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 transition-all shadow-sm"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Re-Evaluate</span>
            </button>
          </div>
        </div>

        {/* Navigation Tabs for 6 Capabilities */}
        <div className="flex items-center gap-2 mt-5 border-t border-slate-100 pt-4 flex-wrap">
          <button
            onClick={() => setActiveSubTab('decision')}
            className={`flex items-center space-x-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
              activeSubTab === 'decision'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Brain className="w-3.5 h-3.5" />
            <span>Decision & WHY Engine</span>
          </button>
          <button
            onClick={() => setActiveSubTab('dissent')}
            className={`flex items-center space-x-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
              activeSubTab === 'dissent'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Swords className="w-3.5 h-3.5" />
            <span>Agent Dissent & Consensus</span>
          </button>
          <button
            onClick={() => setActiveSubTab('timeline')}
            className={`flex items-center space-x-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
              activeSubTab === 'timeline'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
            }`}
          >
            <History className="w-3.5 h-3.5" />
            <span>Marine Timeline (Past/Pres/Fut)</span>
          </button>
          <button
            onClick={() => setActiveSubTab('twin')}
            className={`flex items-center space-x-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
              activeSubTab === 'twin'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Target className="w-3.5 h-3.5" />
            <span>Marine Decision Twin</span>
          </button>
          <button
            onClick={() => setActiveSubTab('whatif')}
            className={`flex items-center space-x-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
              activeSubTab === 'whatif'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>What-If Scenario Simulator</span>
          </button>
        </div>
      </div>

      {/* ── Tab 1: Marine Decision Card, WHY Engine & Decision DNA ── */}
      {activeSubTab === 'decision' && (
        <div className="space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* Marine Decision Card */}
            <div className="rounded-3xl p-5 bg-white border border-blue-100 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider">
                  Master Recommendation
                </span>
                <span className={`px-2.5 py-1 rounded-full text-xs font-extrabold border ${recBadge.bg}`}>
                  {rec === 'RECOMMENDED' ? '🟢 RECOMMENDED' : rec === 'CAUTION' ? '🟡 CAUTION' : '🔴 AVOID'}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-3 pt-2">
                <div className="p-3 rounded-2xl bg-blue-50/50 border border-blue-100">
                  <div className="text-[10px] font-mono text-slate-400">RISK SCORE</div>
                  <div className="text-2xl font-black text-blue-950 mt-0.5">
                    {Math.round(dnaData?.risk_score || 38)}/100
                  </div>
                </div>
                <div className="p-3 rounded-2xl bg-blue-50/50 border border-blue-100">
                  <div className="text-[10px] font-mono text-slate-400">CONFIDENCE</div>
                  <div className="text-2xl font-black text-blue-950 mt-0.5">
                    {Math.round((dnaData?.confidence || 0.88) * 100)}%
                  </div>
                </div>
              </div>
              <div className="text-xs text-slate-600 leading-relaxed pt-1">
                {whyData?.summary_why || 'Multi-agent baseline operational evaluation.'}
              </div>
            </div>

            {/* Marine WHY Engine Factors */}
            <div className="md:col-span-2 rounded-3xl p-5 bg-white border border-blue-100 shadow-sm space-y-3">
              <div className="flex items-center space-x-2">
                <Brain className="w-4 h-4 text-blue-600" />
                <h3 className="font-extrabold text-blue-950 text-sm">Marine WHY Engine — Primary Causal Factors</h3>
              </div>
              <p className="text-xs text-slate-500">
                Transparent multi-agent causality explaining why this marine sector was given the current safety designation:
              </p>
              <div className="space-y-2 pt-1">
                {whyData?.primary_factors?.map((f, i) => (
                  <div key={i} className="flex items-start space-x-2.5 p-2.5 rounded-xl bg-slate-50 border border-slate-100 text-xs text-slate-700">
                    <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 mt-0.5 shrink-0" />
                    <span>{f}</span>
                  </div>
                ))}
              </div>
              <div className="pt-2 flex items-center justify-between text-[11px] text-slate-500 border-t border-slate-100">
                <span>Supporting Agents: <b>{whyData?.supporting_agents?.join(', ') || 'Ocean, Weather, GIS'}</b></span>
                {whyData?.dissenting_agents && whyData.dissenting_agents.length > 0 && (
                  <span className="text-amber-700 font-bold">Dissenting: {whyData.dissenting_agents.join(', ')}</span>
                )}
              </div>
            </div>
          </div>

          {/* 🧬 Decision DNA Card */}
          {dnaData && (
            <div className="rounded-3xl p-5 bg-white border border-blue-100 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Dna className="w-4 h-4 text-purple-600" />
                  <h3 className="font-extrabold text-blue-950 text-sm">🧬 Decision DNA Blueprint</h3>
                  <span className="text-[10px] font-mono px-2 py-0.5 bg-purple-50 text-purple-700 border border-purple-200 rounded-md font-bold">
                    {dnaData.decision_id}
                  </span>
                </div>
                <button
                  onClick={() => setDnaExpanded(!dnaExpanded)}
                  className="flex items-center space-x-1 text-xs font-bold text-blue-600 hover:text-blue-800"
                >
                  <span>{dnaExpanded ? 'Collapse Blueprint' : 'Expand Full DNA'}</span>
                  {dnaExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                </button>
              </div>

              {/* Agent Votes Matrix */}
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                {Object.entries(dnaData.agents || {}).map(([ag, st]) => (
                  <div key={ag} className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-center">
                    <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">{ag}</div>
                    <div className={`mt-1 text-xs font-extrabold ${
                      st === 'SAFE' || st === 'RECOMMENDED' ? 'text-emerald-600' :
                      st === 'DANGER' || st === 'AVOID' ? 'text-red-600' : 'text-amber-600'
                    }`}>
                      {st}
                    </div>
                  </div>
                ))}
              </div>

              {dnaExpanded && (
                <div className="space-y-3 pt-3 border-t border-slate-100 text-xs">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
                      <div className="font-bold text-slate-700 uppercase tracking-wider text-[10px]">Supporting Evidence</div>
                      {dnaData.supporting_evidence.map((s, idx) => (
                        <div key={idx} className="text-slate-600">• {s}</div>
                      ))}
                    </div>
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
                      <div className="font-bold text-slate-700 uppercase tracking-wider text-[10px]">What Would Change My Decision?</div>
                      {dnaData.what_would_change_decision.map((w, idx) => (
                        <div key={idx} className="text-slate-600">• {w}</div>
                      ))}
                    </div>
                  </div>
                  <div className="p-3 rounded-xl bg-blue-50/50 border border-blue-100 text-[11px] text-slate-500 flex flex-wrap justify-between gap-2">
                    <div><b>Data Provenance:</b> {dnaData.data_sources.join(' | ')}</div>
                    <div><b>Generated:</b> {new Date(dnaData.timestamp).toLocaleTimeString()}</div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ── Tab 2: Agent Dissent & Conflict Resolution ── */}
      {activeSubTab === 'dissent' && dissentData && (
        <div className="space-y-5">
          {/* Conflict Detected Alert Banner */}
          <div className={`rounded-3xl p-5 border ${
            dissentData.has_conflict ? 'bg-amber-50/60 border-amber-300' : 'bg-emerald-50/60 border-emerald-300'
          } space-y-3`}>
            <div className="flex items-center space-x-2.5">
              <Swords className={`w-5 h-5 ${dissentData.has_conflict ? 'text-amber-600' : 'text-emerald-600'}`} />
              <h3 className="font-black text-base text-blue-950">
                {dissentData.has_conflict ? '⚔️ Cross-Agent Conflict Detected' : '✓ Unanimous Agent Consensus'}
              </h3>
            </div>
            <p className="text-xs text-slate-700 leading-relaxed font-medium">
              {dissentData.conflict_detected}
            </p>
            {dissentData.has_conflict && (
              <div className="p-3 rounded-2xl bg-white border border-amber-200 text-xs space-y-1">
                <div className="font-bold text-blue-950 uppercase tracking-wider text-[10px]">
                  Master Orchestrator Resolution Strategy: {dissentData.resolution_strategy}
                </div>
                <p className="text-slate-600">{dissentData.resolution_rationale}</p>
              </div>
            )}
          </div>

          {/* Agent Opinion Matrix Table */}
          <div className="rounded-3xl p-5 bg-white border border-blue-100 shadow-sm space-y-3">
            <h3 className="font-extrabold text-blue-950 text-sm">Specialized Agent Opinion Matrix</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 text-slate-400 font-mono text-[10px] uppercase">
                    <th className="py-2.5 px-3">Agent</th>
                    <th className="py-2.5 px-3">Priority Level</th>
                    <th className="py-2.5 px-3">Decision</th>
                    <th className="py-2.5 px-3">Risk Score</th>
                    <th className="py-2.5 px-3">Confidence</th>
                    <th className="py-2.5 px-3">Key Evidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {dissentData.agent_opinions.map((op, i) => (
                    <tr key={i} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3 px-3 font-bold text-blue-950">{op.agent}</td>
                      <td className="py-3 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                          op.priority_level === 'SAFETY_CRITICAL' ? 'bg-red-50 text-red-700 border border-red-200' :
                          op.priority_level === 'OPERATIONAL' ? 'bg-blue-50 text-blue-700 border border-blue-200' :
                          'bg-slate-100 text-slate-700'
                        }`}>
                          {op.priority_level}
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        <span className={`font-extrabold ${
                          op.decision === 'SAFE' || op.decision === 'RECOMMENDED' ? 'text-emerald-600' :
                          op.decision === 'DANGER' || op.decision === 'AVOID' ? 'text-red-600' : 'text-amber-600'
                        }`}>
                          {op.decision}
                        </span>
                      </td>
                      <td className="py-3 px-3 font-mono font-bold text-slate-700">{Math.round(op.risk_score)}/100</td>
                      <td className="py-3 px-3 font-mono text-slate-500">{Math.round(op.confidence * 100)}%</td>
                      <td className="py-3 px-3 text-slate-600">{op.key_evidence}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ── Tab 3: Past → Present → Future Marine Timeline ── */}
      {activeSubTab === 'timeline' && timelineData && (
        <div className="space-y-5">
          <div className="rounded-3xl p-5 bg-white border border-blue-100 shadow-sm space-y-4">
            <div className="flex items-center space-x-2">
              <History className="w-4 h-4 text-blue-600" />
              <h3 className="font-extrabold text-blue-950 text-sm">⏳ Temporal Marine Timeline: Past → Present → Future</h3>
            </div>
            <p className="text-xs text-slate-500">
              Cross-horizon temporal reasoning contrasting past empirical observations with live telemetry and numerical model projections:
            </p>

            {/* 3 Step Stage Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
              {timelineData.timeline_stages.map((st, i) => (
                <div key={i} className={`p-4 rounded-2xl border ${
                  st.stage === 'PRESENT' ? 'bg-blue-50/50 border-blue-400 shadow-sm ring-1 ring-blue-300' : 'bg-slate-50 border-slate-200'
                } space-y-3`}>
                  <div className="flex items-center justify-between">
                    <span className="font-black text-xs text-blue-950 uppercase tracking-wider">{st.stage}</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      st.risk_level === 'SAFE' ? 'bg-emerald-100 text-emerald-800' :
                      st.risk_level === 'DANGER' ? 'bg-red-100 text-red-800' : 'bg-amber-100 text-amber-800'
                    }`}>
                      {st.risk_level} (Score: {Math.round(st.risk_score)})
                    </span>
                  </div>
                  <div className="text-[11px] font-mono text-slate-400">{st.timestamp_label}</div>

                  <div className="space-y-1 text-xs pt-1">
                    <div className="flex justify-between text-slate-600">
                      <span>Wave Swell:</span>
                      <b className="font-mono text-blue-950">{st.wave_height_m}m</b>
                    </div>
                    <div className="flex justify-between text-slate-600">
                      <span>Surface Wind:</span>
                      <b className="font-mono text-blue-950">{st.wind_speed_kmh} km/h</b>
                    </div>
                    <div className="flex justify-between text-slate-600">
                      <span>SST Temperature:</span>
                      <b className="font-mono text-blue-950">{st.surface_temp_c}°C</b>
                    </div>
                  </div>

                  <p className="text-[11px] text-slate-500 italic pt-1 border-t border-slate-200">
                    {st.notes}
                  </p>
                </div>
              ))}
            </div>

            {/* Trend Explanation Box */}
            <div className="p-3.5 rounded-2xl bg-blue-50 border border-blue-200 text-xs text-blue-950 font-medium leading-relaxed">
              {timelineData.temporal_reasoning}
            </div>
          </div>
        </div>
      )}

      {/* ── Tab 4: Marine Decision Twin (Mission Profile) ── */}
      {activeSubTab === 'twin' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          {/* Mission Inputs Form */}
          <div className="rounded-3xl p-5 bg-white border border-blue-100 shadow-sm space-y-4">
            <div className="flex items-center space-x-2">
              <Target className="w-4 h-4 text-blue-600" />
              <h3 className="font-extrabold text-blue-950 text-sm">Mission Context Inputs</h3>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-500 uppercase tracking-wider text-[10px]">Planned Departure</label>
                <select
                  value={departureTime}
                  onChange={e => setDepartureTime(e.target.value)}
                  className="w-full mt-1 px-3 py-2 rounded-xl bg-blue-50 border border-blue-200 font-bold text-blue-950"
                >
                  <option value="04:00 AM">04:00 AM (Early Dawn)</option>
                  <option value="05:00 AM">05:00 AM (Optimal Dawn Window)</option>
                  <option value="07:00 AM">07:00 AM (Morning)</option>
                  <option value="08:30 AM">08:30 AM (Mid Morning)</option>
                  <option value="12:00 PM">12:00 PM (Noon Thermal Breeze)</option>
                  <option value="04:00 PM">04:00 PM (Late Afternoon)</option>
                </select>
              </div>

              <div>
                <label className="font-bold text-slate-500 uppercase tracking-wider text-[10px]">Vessel Classification</label>
                <select
                  value={vesselType}
                  onChange={e => setVesselType(e.target.value)}
                  className="w-full mt-1 px-3 py-2 rounded-xl bg-blue-50 border border-blue-200 font-bold text-blue-950"
                >
                  {VESSEL_OPTIONS.map(v => <option key={v} value={v}>{v}</option>)}
                </select>
              </div>

              <div>
                <label className="font-bold text-slate-500 uppercase tracking-wider text-[10px]">Mission Duration: {durationHours} Hours</label>
                <input
                  type="range" min="2" max="18" step="1"
                  value={durationHours}
                  onChange={e => setDurationHours(Number(e.target.value))}
                  className="w-full mt-2 accent-blue-600"
                />
              </div>

              <div>
                <label className="font-bold text-slate-500 uppercase tracking-wider text-[10px]">Target Activity</label>
                <select
                  value={targetActivity}
                  onChange={e => setTargetActivity(e.target.value)}
                  className="w-full mt-1 px-3 py-2 rounded-xl bg-blue-50 border border-blue-200 font-bold text-blue-950"
                >
                  {ACTIVITY_OPTIONS.map(a => <option key={a} value={a}>{a}</option>)}
                </select>
              </div>

              <button
                onClick={handleUpdateMission}
                className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold transition-all shadow-md mt-2"
              >
                Synthesize Decision Twin
              </button>
            </div>
          </div>

          {/* Decision Twin Output */}
          <div className="lg:col-span-2 rounded-3xl p-5 bg-white border border-blue-100 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Brain className="w-4 h-4 text-purple-600" />
                <h3 className="font-extrabold text-blue-950 text-sm">🧠 Marine Decision Twin Profile</h3>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-extrabold border ${
                missionData?.recommendation === 'RECOMMENDED' ? 'bg-emerald-50 text-emerald-800 border-emerald-300' :
                missionData?.recommendation === 'CAUTION' ? 'bg-amber-50 text-amber-800 border-amber-300' :
                'bg-red-50 text-red-800 border-red-300'
              }`}>
                {missionData?.recommendation || 'RECOMMENDED'}
              </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-center">
                <div className="text-[10px] font-mono text-slate-400">MISSION RISK</div>
                <div className="text-xl font-black text-blue-950 mt-0.5">{Math.round(missionData?.risk_score || 36)}/100</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-center">
                <div className="text-[10px] font-mono text-slate-400">CONFIDENCE</div>
                <div className="text-xl font-black text-blue-950 mt-0.5">{Math.round((missionData?.confidence || 0.88) * 100)}%</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-center">
                <div className="text-[10px] font-mono text-slate-400">DEPARTURE</div>
                <div className="text-sm font-bold text-blue-950 mt-1">{departureTime}</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-center">
                <div className="text-[10px] font-mono text-slate-400">DURATION</div>
                <div className="text-sm font-bold text-blue-950 mt-1">{durationHours}h Window</div>
              </div>
            </div>

            <div className="space-y-2 pt-2">
              <div className="text-xs font-bold text-slate-700">Expected Environmental Evolution During Mission:</div>
              {missionData?.expected_changes_during_mission.map((ch, idx) => (
                <div key={idx} className="p-2.5 rounded-xl bg-blue-50/60 border border-blue-100 text-xs text-slate-700 flex items-start space-x-2">
                  <Clock className="w-3.5 h-3.5 text-blue-600 mt-0.5 shrink-0" />
                  <span>{ch}</span>
                </div>
              ))}
            </div>

            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600">
              <b>Vessel Limiting Threshold:</b> Switching to smaller artisanal craft elevates risk to CAUTION due to wave steepness limits.
            </div>
          </div>
        </div>
      )}

      {/* ── Tab 5: What-If Scenario Simulator ── */}
      {activeSubTab === 'whatif' && (
        <div className="space-y-5">
          <div className="rounded-3xl p-5 bg-white border border-blue-100 shadow-sm space-y-4">
            <div className="flex items-center space-x-2">
              <Sliders className="w-4 h-4 text-purple-600" />
              <h3 className="font-extrabold text-blue-950 text-sm">🔮 Comparative What-If Scenario Simulator</h3>
            </div>
            <p className="text-xs text-slate-500">
              Test alternative operational decisions side-by-side (e.g. 05:00 AM vs 08:00 AM departure or simulated wave/wind surge):
            </p>

            {/* Slider Controls */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
              <div className="space-y-1.5 p-3 rounded-2xl bg-slate-50 border border-slate-200">
                <div className="flex justify-between text-xs font-bold">
                  <span className="text-slate-600">Wave Height Surge</span>
                  <span className="text-blue-600">+{waveSurge}%</span>
                </div>
                <input
                  type="range" min="0" max="150" value={waveSurge}
                  onChange={e => setWaveSurge(Number(e.target.value))}
                  className="w-full accent-blue-600"
                />
              </div>

              <div className="space-y-1.5 p-3 rounded-2xl bg-slate-50 border border-slate-200">
                <div className="flex justify-between text-xs font-bold">
                  <span className="text-slate-600">Wind Speed Surge</span>
                  <span className="text-blue-600">+{windSurge}%</span>
                </div>
                <input
                  type="range" min="0" max="100" value={windSurge}
                  onChange={e => setWindSurge(Number(e.target.value))}
                  className="w-full accent-blue-600"
                />
              </div>

              <div className="space-y-1.5 p-3 rounded-2xl bg-slate-50 border border-slate-200">
                <div className="flex justify-between text-xs font-bold">
                  <span className="text-slate-600">Pressure Drop</span>
                  <span className="text-amber-600">-{pressDrop} hPa</span>
                </div>
                <input
                  type="range" min="0" max="30" value={pressDrop}
                  onChange={e => setPressDrop(Number(e.target.value))}
                  className="w-full accent-amber-600"
                />
              </div>
            </div>

            <div className="flex justify-end pt-1">
              <button
                onClick={handleSimulateWhatIf}
                className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold shadow-sm transition-all flex items-center space-x-1.5"
              >
                <Zap className="w-3.5 h-3.5" />
                <span>Simulate Alternative Scenario</span>
              </button>
            </div>

            {/* Side-by-Side Comparison */}
            {whatIfData && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-3">
                {/* Baseline */}
                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-bold text-slate-400 uppercase">Baseline ({whatIfData.baseline.departure})</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-200 text-slate-800">
                      {whatIfData.baseline.recommendation}
                    </span>
                  </div>
                  <div className="text-2xl font-black text-blue-950">
                    Risk {Math.round(whatIfData.baseline.risk_score)}/100
                  </div>
                  <div className="text-xs text-slate-600 space-y-0.5">
                    <div>Wave: <b>{whatIfData.baseline.wave_height_m}m</b></div>
                    <div>Wind: <b>{whatIfData.baseline.wind_speed_kmh} km/h</b></div>
                  </div>
                </div>

                {/* Scenario */}
                <div className="p-4 rounded-2xl bg-purple-50/50 border border-purple-200 shadow-sm space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-bold text-purple-700 uppercase">Alternative ({whatIfData.scenario.departure})</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      whatIfData.scenario.recommendation === 'RECOMMENDED' ? 'bg-emerald-100 text-emerald-800' :
                      whatIfData.scenario.recommendation === 'CAUTION' ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {whatIfData.scenario.recommendation}
                    </span>
                  </div>
                  <div className="text-2xl font-black text-purple-950">
                    Risk {Math.round(whatIfData.scenario.risk_score)}/100
                    <span className={`ml-2 text-sm font-bold ${whatIfData.risk_delta < 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                      ({whatIfData.risk_delta > 0 ? `+${whatIfData.risk_delta}` : whatIfData.risk_delta})
                    </span>
                  </div>
                  <div className="text-xs text-slate-600 space-y-0.5">
                    <div>Wave: <b>{whatIfData.scenario.wave_height_m}m</b></div>
                    <div>Wind: <b>{whatIfData.scenario.wind_speed_kmh} km/h</b></div>
                  </div>
                </div>
              </div>
            )}

            {whatIfData && (
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 text-xs text-slate-700 leading-relaxed">
                <b>Simulation Result:</b> {whatIfData.main_reason}
              </div>
            )}
          </div>
        </div>
      )}

    </div>
  );
};
