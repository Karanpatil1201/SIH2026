import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface DirectionalPoint {
  direction: string;
  lat: number;
  lon: number;
  riskLevel?: string;
  riskScore?: number;
  loading: boolean;
}

interface LiveTrackingMapProps {
  lat: number | null;
  lon: number | null;
  accuracy: number | null;
  dirPoints: DirectionalPoint[];
  isTracking: boolean;
}

// ── Risk color mapping ────────────────────────────────────────────────────────
const riskToColor = (level?: string): string => {
  if (level === 'LOW')      return '#22c55e';
  if (level === 'MODERATE') return '#f59e0b';
  if (level === 'HIGH')     return '#f97316';
  if (level === 'CRITICAL') return '#ef4444';
  return '#94a3b8';
};

const riskToLabel = (level?: string): string => {
  if (level === 'LOW')      return '✓ SAFE';
  if (level === 'MODERATE') return '⚠ CAUTION';
  if (level === 'HIGH')     return '✖ DANGER';
  if (level === 'CRITICAL') return '🚨 CRITICAL';
  return '● SCANNING';
};

// ── Custom SVG icons ──────────────────────────────────────────────────────────
const youIcon = L.divIcon({
  className: '',
  html: `
    <div style="position:relative;width:44px;height:44px;">
      <div style="
        position:absolute;inset:0;
        border-radius:50%;
        background:rgba(37,99,235,0.15);
        animation:ripple 2s ease-out infinite;
      "></div>
      <div style="
        position:absolute;top:50%;left:50%;
        transform:translate(-50%,-50%);
        width:20px;height:20px;
        border-radius:50%;
        background:#2563eb;
        border:3px solid #ffffff;
        box-shadow:0 2px 12px rgba(37,99,235,0.60);
      "></div>
    </div>
    <style>
      @keyframes ripple {
        0%   { transform:scale(0.6); opacity:0.9; }
        100% { transform:scale(2.2); opacity:0; }
      }
    </style>
  `,
  iconSize: [44, 44],
  iconAnchor: [22, 22],
});

const dirIcon = (direction: string, color: string, loading: boolean) => L.divIcon({
  className: '',
  html: `
    <div style="
      width:36px;height:36px;border-radius:50%;
      background:${loading ? '#94a3b8' : color};
      border:3px solid #fff;
      box-shadow:0 2px 10px rgba(0,0,0,0.25);
      display:flex;align-items:center;justify-content:center;
      font-size:10px;font-weight:900;color:#fff;font-family:Inter,sans-serif;
      ${loading ? 'animation:spin 1s linear infinite;' : ''}
    ">${direction}</div>
    <style>@keyframes spin{to{transform:rotate(360deg)}}</style>
  `,
  iconSize: [36, 36],
  iconAnchor: [18, 18],
});

// ─────────────────────────────────────────────────────────────────────────────
export const LiveTrackingMap: React.FC<LiveTrackingMapProps> = ({
  lat, lon, accuracy, dirPoints, isTracking
}) => {
  const mapRef    = useRef<L.Map | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const youMarkerRef    = useRef<L.Marker | null>(null);
  const accuracyCircRef = useRef<L.Circle | null>(null);
  const dirMarkersRef   = useRef<L.Marker[]>([]);
  const riskCirclesRef  = useRef<L.Circle[]>([]);
  const polylineRef     = useRef<L.Polyline | null>(null);
  const posHistoryRef   = useRef<[number, number][]>([]);
  const followRef       = useRef<boolean>(true); // auto-follow toggle

  // ── Init map ────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = L.map(containerRef.current, {
      center: [lat ?? 18.9, lon ?? 72.8],
      zoom: 9,
      zoomControl: true,
      attributionControl: false,
    });

    // Tile layer — OpenStreetMap (free, no API key)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '© OpenStreetMap',
    }).addTo(map);

    // Attribution compact
    L.control.attribution({ prefix: false, position: 'bottomright' }).addTo(map);
    map.attributionControl?.setPrefix('');

    // When user drags, stop auto-follow
    map.on('dragstart', () => { followRef.current = false; });

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // ── Update "YOU" position ───────────────────────────────────────────────────
  useEffect(() => {
    const map = mapRef.current;
    if (!map || lat == null || lon == null) return;

    const pos: [number, number] = [lat, lon];

    // Record position history for trail
    posHistoryRef.current.push(pos);
    if (posHistoryRef.current.length > 60) posHistoryRef.current.shift();

    // Update or create "You" marker
    if (youMarkerRef.current) {
      youMarkerRef.current.setLatLng(pos);
    } else {
      youMarkerRef.current = L.marker(pos, { icon: youIcon, zIndexOffset: 1000 })
        .addTo(map)
        .bindTooltip('📍 You are here', { permanent: false, className: 'live-tip' });
    }

    // Accuracy circle
    if (accuracy != null) {
      if (accuracyCircRef.current) {
        accuracyCircRef.current.setLatLng(pos).setRadius(accuracy);
      } else {
        accuracyCircRef.current = L.circle(pos, {
          radius: accuracy,
          color: '#2563eb',
          fillColor: '#2563eb',
          fillOpacity: 0.08,
          weight: 1.5,
          dashArray: '4',
        }).addTo(map);
      }
    }

    // Trail polyline
    if (posHistoryRef.current.length > 1) {
      if (polylineRef.current) {
        polylineRef.current.setLatLngs(posHistoryRef.current);
      } else {
        polylineRef.current = L.polyline(posHistoryRef.current, {
          color: '#2563eb',
          weight: 3,
          opacity: 0.5,
          dashArray: '6 4',
        }).addTo(map);
      }
    }

    // Auto-follow
    if (followRef.current) {
      map.setView(pos, Math.max(map.getZoom(), 9), { animate: true, duration: 1.2 });
    }
  }, [lat, lon, accuracy]);

  // ── Update directional scan markers ────────────────────────────────────────
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    // Remove old
    dirMarkersRef.current.forEach(m => m.remove());
    riskCirclesRef.current.forEach(c => c.remove());
    dirMarkersRef.current = [];
    riskCirclesRef.current = [];

    const center = lat != null && lon != null ? { lat, lon } : null;

    dirPoints.forEach(pt => {
      if (!pt.lat || !pt.lon) return;
      const color = riskToColor(pt.riskLevel);

      // Direction marker
      const marker = L.marker([pt.lat, pt.lon], {
        icon: dirIcon(pt.direction, color, pt.loading),
      })
        .addTo(map)
        .bindPopup(`
          <div style="font-family:Inter,sans-serif;font-size:12px;min-width:160px;">
            <div style="font-weight:900;font-size:14px;color:#0f172a;margin-bottom:4px;">
              ${pt.direction} — ${riskToLabel(pt.riskLevel)}
            </div>
            <div style="color:#64748b;font-size:11px;">
              ${pt.lat.toFixed(4)}°N, ${pt.lon.toFixed(4)}°E
            </div>
            ${pt.riskScore != null ? `
            <div style="margin-top:6px;">
              <div style="font-size:10px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:.05em;">Risk Score</div>
              <div style="background:#f1f5f9;border-radius:999px;height:6px;margin-top:3px;overflow:hidden;">
                <div style="background:${color};height:6px;width:${pt.riskScore}%;border-radius:999px;"></div>
              </div>
              <div style="font-weight:900;font-size:13px;color:${color};margin-top:2px;">${Math.round(pt.riskScore)}/100</div>
            </div>` : ''}
          </div>
        `, { maxWidth: 200 });

      dirMarkersRef.current.push(marker);

      // Risk zone circle (only when not loading)
      if (!pt.loading && center) {
        const circle = L.circle([pt.lat, pt.lon], {
          radius: 30000, // 30 km visual zone
          color,
          fillColor: color,
          fillOpacity: 0.06,
          weight: 1.5,
          dashArray: pt.riskLevel === 'CRITICAL' ? '4' : undefined,
        }).addTo(map);
        riskCirclesRef.current.push(circle);
      }
    });
  }, [dirPoints, lat, lon]);

  // ── Re-centre button ────────────────────────────────────────────────────────
  const recenter = () => {
    if (mapRef.current && lat != null && lon != null) {
      followRef.current = true;
      mapRef.current.setView([lat, lon], 9, { animate: true, duration: 1 });
    }
  };

  return (
    <div className="relative w-full" style={{ height: 420, borderRadius: '1rem', overflow: 'hidden', border: '1px solid rgba(37,99,235,0.14)', boxShadow: '0 2px 16px rgba(29,78,216,0.08)' }}>
      {/* Map container */}
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />

      {/* Top overlay bar */}
      <div style={{
        position: 'absolute', top: 10, left: 10, right: 10, zIndex: 999,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        pointerEvents: 'none',
      }}>
        <div style={{
          background: 'rgba(255,255,255,0.95)',
          backdropFilter: 'blur(10px)',
          borderRadius: '0.75rem',
          padding: '6px 12px',
          border: '1px solid rgba(37,99,235,0.18)',
          boxShadow: '0 2px 12px rgba(0,0,0,0.10)',
          display: 'flex', alignItems: 'center', gap: '8px',
          fontSize: '11px', fontWeight: 700, color: '#1e3a8a', fontFamily: 'Inter,sans-serif',
        }}>
          <span style={{
            width: 8, height: 8, borderRadius: '50%',
            background: isTracking ? '#22c55e' : '#94a3b8',
            boxShadow: isTracking ? '0 0 0 3px rgba(34,197,94,0.3)' : 'none',
            animation: isTracking ? 'ping 1.5s ease-out infinite' : 'none',
            display: 'inline-block',
          }} />
          {isTracking ? '● LIVE GPS TRACKING' : lat != null ? '📍 MANUAL LOCATION' : 'STANDBY'}
          {lat != null && (
            <span style={{ color: '#6b7280', fontWeight: 600 }}>
              {lat.toFixed(4)}°N, {lon?.toFixed(4)}°E
            </span>
          )}
        </div>
      </div>

      {/* Re-center button */}
      <button
        onClick={recenter}
        title="Re-centre map on your location"
        style={{
          position: 'absolute', bottom: 16, right: 16, zIndex: 999,
          background: '#2563eb', color: '#fff',
          border: 'none', borderRadius: '0.75rem',
          padding: '8px 14px',
          fontSize: '11px', fontWeight: 700, cursor: 'pointer',
          display: 'flex', alignItems: 'center', gap: '6px',
          boxShadow: '0 2px 12px rgba(37,99,235,0.40)',
          fontFamily: 'Inter,sans-serif',
        }}
      >
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><circle cx="12" cy="12" r="3"/><path d="M12 2v4m0 12v4M2 12h4m12 0h4"/></svg>
        Re-centre
      </button>

      {/* No GPS placeholder */}
      {lat == null && (
        <div style={{
          position: 'absolute', inset: 0, zIndex: 998,
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          background: 'rgba(240,246,255,0.85)', backdropFilter: 'blur(4px)',
          gap: '8px',
        }}>
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#93c5fd" strokeWidth="1.5"><circle cx="12" cy="12" r="3"/><path d="M12 2v4m0 12v4M2 12h4m12 0h4"/></svg>
          <div style={{ fontWeight: 700, color: '#2563eb', fontSize: '14px', fontFamily: 'Inter,sans-serif' }}>Waiting for location…</div>
          <div style={{ color: '#94a3b8', fontSize: '11px', fontFamily: 'Inter,sans-serif' }}>Enable GPS or enter coordinates</div>
        </div>
      )}

      <style>{`
        .live-tip { background:#1e3a8a;color:#fff;border:none;border-radius:8px;font-size:11px;font-weight:700;padding:4px 8px; }
        .leaflet-popup-content-wrapper { border-radius:14px !important; border:1px solid rgba(37,99,235,0.15) !important; }
        @keyframes ping { 0%,100%{opacity:1}50%{opacity:0.4} }
      `}</style>
    </div>
  );
};
