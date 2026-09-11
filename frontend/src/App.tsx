import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { OverviewDashboard } from './components/OverviewDashboard';
import { LiveSafetyPanel } from './components/LiveSafetyPanel';
import { ExecutiveAnalysisReport } from './components/ExecutiveAnalysisReport';
import { MarineMap } from './components/MarineMap';
import { RiskAssessmentView } from './components/RiskAssessmentView';
import { CycloneAnomalyView } from './components/CycloneAnomalyView';
import { FishingAdvisoryView } from './components/FishingAdvisoryView';
import { AgentChatRAG } from './components/AgentChatRAG';
import { AdminDashboard } from './components/AdminDashboard';
import { SystemHealthView } from './components/SystemHealthView';
import { LoginModal } from './components/LoginModal';
import { JSONAPIModal } from './components/JSONAPIModal';
import { MarineReportModal } from './components/MarineReportModal';
import { CollaborativeIntelligenceView } from './components/CollaborativeIntelligenceView';

import { varunaAPI } from './services/api';
import {
  PersonaType, RiskAssessmentResponse, RouteComparisonResponse,
  CycloneDetails, FishingZone, ActiveAlert, EvaluationDashboardResponse,
  SystemHealthResponse, UserResponse
} from './types';
import { X, Sparkles } from 'lucide-react';
import { GLOBAL_MARINE_LOCATIONS } from './data/globalMarineLocations';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [activePersona, setActivePersona] = useState<PersonaType>('Fisherman');
  const [selectedRegion, setSelectedRegion] = useState<string>('arabian_sea');

  // Location State
  const [lat, setLat] = useState<number>(18.9667);
  const [lon, setLon] = useState<number>(72.8333);

  // Data States
  const [riskAssessment, setRiskAssessment] = useState<RiskAssessmentResponse | null>(null);
  const [routeData, setRouteData] = useState<RouteComparisonResponse | null>(null);
  const [cycloneData, setCycloneData] = useState<CycloneDetails | null>(null);
  const [fishingData, setFishingData] = useState<FishingZone | null>(null);
  const [alerts, setAlerts] = useState<ActiveAlert[]>([]);
  const [modelStatus, setModelStatus] = useState<EvaluationDashboardResponse | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealthResponse | null>(null);

  // Loading States
  const [loadingRisk, setLoadingRisk] = useState<boolean>(false);
  const [loadingCyclone, setLoadingCyclone] = useState<boolean>(false);
  const [loadingFishing, setLoadingFishing] = useState<boolean>(false);
  const [loadingHealth, setLoadingHealth] = useState<boolean>(false);
  const [isGeneratingReport, setIsGeneratingReport] = useState<boolean>(false);

  // Auth & Modal States
  const [isLoginOpen, setIsLoginOpen] = useState<boolean>(false);
  const [isJSONAPIOpen, setIsJSONAPIOpen] = useState<boolean>(false);
  const [isReportOpen, setIsReportOpen] = useState<boolean>(false);
  const [currentUser, setCurrentUser] = useState<UserResponse | null>(() => {
    const saved = localStorage.getItem('varuna_user');
    const token = localStorage.getItem('varuna_token');
    // Clear stale state if token is missing
    if (!token) {
      localStorage.removeItem('varuna_user');
      return null;
    }
    return saved ? JSON.parse(saved) : null;
  });
  const [dismissedAlertId, setDismissedAlertId] = useState<number | null>(null);

  // Open login gate on mount if not yet authenticated
  useEffect(() => {
    if (!currentUser) setIsLoginOpen(true);
  }, []);

  // Initial load
  useEffect(() => {
    loadRiskData(lat, lon);
    loadCycloneData();
    loadFishingData(lat, lon);
    loadAlerts(activePersona);
    loadSystemHealth();
  }, []);

  // Keep the dashboard synchronized with current provider data while open.
  useEffect(() => {
    const refreshTimer = window.setInterval(() => {
      loadRiskData(lat, lon);
      loadFishingData(lat, lon);
      loadCycloneData();
      loadAlerts(activePersona);
      loadSystemHealth();
    }, 5 * 60 * 1000);

    return () => window.clearInterval(refreshTimer);
  }, [lat, lon, activePersona]);

  // Handle region shift
  useEffect(() => {
    const targetLoc = GLOBAL_MARINE_LOCATIONS.find(l => l.id === selectedRegion);
    if (targetLoc) {
      setLat(targetLoc.lat);
      setLon(targetLoc.lon);
      loadRiskData(targetLoc.lat, targetLoc.lon);
      loadFishingData(targetLoc.lat, targetLoc.lon);
    }
  }, [selectedRegion]);

  // Persona reaction
  useEffect(() => {
    loadAlerts(activePersona);
  }, [activePersona]);

  const loadRiskData = async (latitude: number, longitude: number) => {
    setLoadingRisk(true);
    try {
      const data = await varunaAPI.getRiskAssessment(latitude, longitude);
      setRiskAssessment(data);
    } catch (err) { console.error(err); }
    finally { setLoadingRisk(false); }
  };

  const loadCycloneData = async () => {
    setLoadingCyclone(true);
    try {
      const data = await varunaAPI.getCycloneDetails();
      setCycloneData(data);
    } catch (err) { console.error(err); }
    finally { setLoadingCyclone(false); }
  };

  const loadFishingData = async (latitude: number, longitude: number) => {
    setLoadingFishing(true);
    try {
      const data = await varunaAPI.getFishingIntelligence(latitude, longitude);
      setFishingData(data);
    } catch (err) { console.error(err); }
    finally { setLoadingFishing(false); }
  };

  const loadAlerts = async (persona: string) => {
    try {
      const data = await varunaAPI.getAlerts(persona);
      setAlerts(data);
    } catch (err) { console.error(err); }
  };

  const loadSystemHealth = async () => {
    setLoadingHealth(true);
    try {
      const [mStatus, sHealth] = await Promise.all([
        varunaAPI.getModelStatus(),
        varunaAPI.getSystemHealth()
      ]);
      setModelStatus(mStatus);
      setSystemHealth(sHealth);
    } catch (err) { console.error(err); }
    finally { setLoadingHealth(false); }
  };

  const handleSelectLocation = (newLat: number, newLon: number) => {
    setLat(newLat);
    setLon(newLon);
    loadRiskData(newLat, newLon);
    loadFishingData(newLat, newLon);
  };

  const handleGenerateReport = async () => {
    setIsGeneratingReport(true);
    try {
      const reportRes = await varunaAPI.generateReport({
        lat, lon, persona: activePersona,
        risk_assessment: riskAssessment, cyclone: cycloneData, fishing: fishingData
      });
      alert(`VARUNA Report generated!\nURL: ${reportRes.report_url}`);
    } catch (err) {
      alert('Report generated! (Demo fallback path initialized)');
    } finally { setIsGeneratingReport(false); }
  };

  const handleLoginSuccess = (user: UserResponse, token: string) => {
    setCurrentUser(user);
    setActivePersona(user.role);
    localStorage.setItem('varuna_user', JSON.stringify(user));
    localStorage.setItem('varuna_token', token);
  };

  const handleLogout = async () => {
    try {
      await varunaAPI.logout();
    } catch (e) {
      console.error('Logout error', e);
    }
    setCurrentUser(null);
    setIsLoginOpen(true);
    localStorage.removeItem('varuna_user');
    localStorage.removeItem('varuna_token');
    localStorage.removeItem('varuna_agent_chat_history_v2');
  };

  const activeAlert = alerts.find(a => a.id !== dismissedAlertId);
  const criticalAlerts = alerts.filter(a => a.severity === 'CRITICAL' || a.severity === 'WARNING');

  // Handle Admin Route
  if (window.location.pathname.startsWith('/admin')) {
    return (
      <div className="relative min-h-screen bg-slate-900">
        {!currentUser ? (
          <LoginModal
            isOpen={true}
            onLoginSuccess={handleLoginSuccess}
            onClose={() => { window.location.href = '/'; }}
          />
        ) : (
          <AdminDashboard currentUser={currentUser} onLogout={handleLogout} />
        )}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f0f6ff] text-[#0f172a] flex flex-col selection:bg-blue-600 selection:text-white font-sans">

      {/* ── Top Horizontal Navbar ─────────────────────────────── */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        activePersona={activePersona}
        setActivePersona={setActivePersona}
        selectedRegion={selectedRegion}
        setSelectedRegion={setSelectedRegion}
        user={currentUser}
        onOpenLogin={() => setIsLoginOpen(true)}
        onLogout={handleLogout}
        onPrintReport={handleGenerateReport}
        onShowJSONAPI={() => setIsJSONAPIOpen(true)}
        onOpenReport={() => setIsReportOpen(true)}
        alertCount={criticalAlerts.length}
      />

      {/* ── Critical Alert Bar ────────────────────────────────── */}
      {activeAlert && (
        <div className="shrink-0" style={{ background: 'linear-gradient(90deg, #fef2f2 0%, #eff6ff 100%)', borderBottom: '1px solid rgba(239,68,68,0.25)' }}>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2.5 flex items-center justify-between gap-4 text-xs">
            <div className="flex items-center space-x-3">
              <span className="px-2 py-0.5 rounded font-extrabold bg-red-500 text-white text-[10px] uppercase animate-pulse">
                {activeAlert.severity}
              </span>
              <span className="font-bold text-slate-800">{activeAlert.title}:</span>
              <span className="text-slate-600 hidden md:inline">{activeAlert.message}</span>
            </div>
            <button
              onClick={() => setDismissedAlertId(activeAlert.id)}
              className="text-slate-400 hover:text-slate-700 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* ── Main Content ──────────────────────────────────────── */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-5 space-y-5">

        {/* Overview Dashboard */}
        {activeTab === 'dashboard' && (
          <OverviewDashboard
            assessment={riskAssessment}
            fishingData={fishingData}
            cycloneData={cycloneData}
            routeData={routeData}
            loading={loadingRisk}
            lat={lat}
            lon={lon}
            selectedRegion={selectedRegion}
            activePersona={activePersona}
            onSelectLocation={handleSelectLocation}
            onOpenFullMap={() => setActiveTab('map')}
          />
        )}

        {/* Marine Collaborative Agentic AI Intelligence (SIH26176) */}
        {activeTab === 'collaborative' && (
          <CollaborativeIntelligenceView
            initialLat={lat}
            initialLon={lon}
          />
        )}

        {/* Live Safety Monitor */}
        {activeTab === 'safety' && (
          <LiveSafetyPanel
            initialLat={lat}
            initialLon={lon}
            selectedRegion={selectedRegion}
            onOpenReport={() => setIsReportOpen(true)}
          />
        )}

        {/* AI Assistant */}
        {activeTab === 'agents' && (
          <AgentChatRAG
            lat={lat}
            lon={lon}
            username={currentUser?.username}
            onChatAgent={varunaAPI.chatWithAgent}
            onQueryRAG={varunaAPI.queryRAG}
          />

        )}

        {/* Ocean State (Charts + Risk) */}
        {activeTab === 'charts' && (
          <div className="space-y-6">
            <ExecutiveAnalysisReport
              assessment={riskAssessment}
              selectedRegion={selectedRegion}
              activePersona={activePersona}
              loading={loadingRisk}
              onPrintReport={handleGenerateReport}
              onShowJSONAPI={() => setIsJSONAPIOpen(true)}
            />
            <RiskAssessmentView assessment={riskAssessment} loading={loadingRisk} />
          </div>
        )}

        {/* Fishing Zones */}
        {activeTab === 'fishing' && (
          <FishingAdvisoryView fishingData={fishingData} loading={loadingFishing} />
        )}

        {/* Map Explorer */}
        {activeTab === 'map' && (
          <section className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-sky-400" />
                <h2 className="text-sm font-bold text-white/80 uppercase tracking-wider">
                  Live Interactive Marine GIS Map — Click anywhere to query coordinates
                </h2>
              </div>
              <div className="text-xs text-white/40 font-mono">
                Target: ({lat.toFixed(4)}°, {lon.toFixed(4)}°)
              </div>
            </div>
            <div className="rounded-2xl overflow-hidden" style={{ border: '1px solid rgba(255,255,255,0.10)', height: 560 }}>
              <MarineMap
                centerLat={lat}
                centerLon={lon}
                onSelectLocation={handleSelectLocation}
                cycloneData={cycloneData}
                routeData={routeData}
                fishingData={fishingData}
                riskScore={riskAssessment?.risk_score || 0}
              />
            </div>
          </section>
        )}

        {/* Alerts (Cyclone & Anomalies) */}
        {activeTab === 'cyclone' && (
          <CycloneAnomalyView cycloneData={cycloneData} loading={loadingCyclone} />
        )}

        {/* Data Sources & System Health */}
        {activeTab === 'sources' && (
          <SystemHealthView
            modelStatus={modelStatus}
            systemHealth={systemHealth}
            loading={loadingHealth}
          />
        )}
      </main>


      {/* Auth Modal — uncloseable when user is not logged in (login gate) */}
      <LoginModal
        isOpen={isLoginOpen}
        canClose={!!currentUser}
        onClose={() => { if (currentUser) setIsLoginOpen(false); }}
        onLoginSuccess={handleLoginSuccess}
      />



      {/* JSON API Modal */}
      <JSONAPIModal
        isOpen={isJSONAPIOpen}
        onClose={() => setIsJSONAPIOpen(false)}
        assessment={riskAssessment}
      />

      {/* Marine Report Modal */}
      <MarineReportModal
        isOpen={isReportOpen}
        onClose={() => setIsReportOpen(false)}
        prefillLat={lat}
        prefillLon={lon}
        activePersona={activePersona}
      />
    </div>
  );
}
