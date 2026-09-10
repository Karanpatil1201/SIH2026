import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { CycloneDetails, RouteComparisonResponse, FishingZone } from '../types';
import { Home, Sliders, Layers, X, Eye, EyeOff, ShieldAlert, Compass } from 'lucide-react';
import { varunaAPI } from '../services/api';

interface MarineMapProps {
  centerLat: number;
  centerLon: number;
  onSelectLocation: (lat: number, lon: number) => void;
  cycloneData?: CycloneDetails | null;
  routeData?: RouteComparisonResponse | null;
  fishingData?: FishingZone | null;
  riskScore?: number;
}

// Global Moored Ocean Buoy Dataset
const GLOBAL_BUOYS = [
  { id: 'AD07', name: 'AD07 (North Arabian Sea)', lat: 18.50, lon: 69.20, type: 'OMNI', status: 'Active (OMNI)' },
  { id: 'AD08', name: 'AD08 (Central Arabian Sea)', lat: 15.00, lon: 68.80, type: 'OMNI', status: 'Active (OMNI)' },
  { id: 'AD09', name: 'AD09 (South Lakshadweep)', lat: 10.50, lon: 72.40, type: 'OMNI', status: 'Active (OMNI)' },
  { id: 'AD10', name: 'AD10 (Minicoy Offshore)', lat: 8.30, lon: 73.00, type: 'OMNI', status: 'Active (OMNI)' },
  { id: 'CB01', name: 'CB01 (Andaman Deep Sea)', lat: 11.50, lon: 92.60, type: 'Moored', status: 'Active' },
  { id: 'CB02', name: 'CB02 (Lakshadweep Basin)', lat: 10.80, lon: 72.10, type: 'Moored', status: 'Active' },
  { id: 'CB06', name: 'CB06 (Palk Strait Shelf)', lat: 10.20, lon: 79.90, type: 'Standby', status: 'Inactive (OMNI)' },
  { id: 'BD12', name: 'BD12 (South Bay of Bengal)', lat: 10.50, lon: 94.00, type: 'OMNI', status: 'Active (OMNI)' },
  { id: 'BD13', name: 'BD13 (Central Bay of Bengal)', lat: 14.00, lon: 87.00, type: 'OMNI', status: 'Active (OMNI)' },
  { id: 'CALVAL', name: 'CALVAL (Kavaratti Calibration)', lat: 10.56, lon: 72.64, type: 'Moored', status: 'Active' }
];

export const MarineMap: React.FC<MarineMapProps> = ({
  centerLat,
  centerLon,
  onSelectLocation,
  cycloneData,
  routeData,
  fishingData,
  riskScore = 0
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const layersRef = useRef<L.LayerGroup | null>(null);

  // Map state controls
  const [currentMouseCoords, setCurrentMouseCoords] = useState<{ lat: number; lng: number }>({
    lat: centerLat,
    lng: centerLon
  });
  const [activeTileLayer, setActiveTileLayer] = useState<'satellite' | 'bathymetry' | 'dark'>('satellite');
  const [showLegend, setShowLegend] = useState<boolean>(true);
  const [showBuoys, setShowBuoys] = useState<boolean>(true);
  const [showCycloneLayer, setShowCycloneLayer] = useState<boolean>(true);
  const [showPFZLayer, setShowPFZLayer] = useState<boolean>(true);
  const [showRouteLayer, setShowRouteLayer] = useState<boolean>(true);
  const [showGeofenceLayer, setShowGeofenceLayer] = useState<boolean>(true);
  const [showMPALayer, setShowMPALayer] = useState<boolean>(true);

  // Loaded GIS Data
  const [gisLayers, setGisLayers] = useState<{
    imbl_boundaries: any[];
    restricted_zones: any[];
    marine_protected_areas: any[];
    ecologically_sensitive_zones: any[];
    coastal_ports: any[];
  }>({
    imbl_boundaries: [],
    restricted_zones: [],
    marine_protected_areas: [],
    ecologically_sensitive_zones: [],
    coastal_ports: []
  });

  const tileLayersRef = useRef<{
    satellite: L.TileLayer;
    bathymetry: L.TileLayer;
    dark: L.TileLayer;
  } | null>(null);

  // Load GIS layers from backend
  useEffect(() => {
    varunaAPI.getGeofenceLayers().then(data => {
      if (data && data.imbl_boundaries) {
        setGisLayers(data);
      }
    }).catch(err => console.warn('Could not load GIS layers', err));
  }, []);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const satelliteLayer = L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      {
        attribution: '&copy; Esri, Maxar, Earthstar Geographics & GEBCO Bathymetry',
        maxZoom: 18,
      }
    );

    const bathymetryLayer = L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}',
      {
        attribution: '&copy; Esri, GEBCO, NOAA, National Geographic',
        maxZoom: 16,
      }
    );

    const darkLayer = L.tileLayer(
      'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
      {
        attribution: '&copy; CARTO & OpenStreetMap',
        maxZoom: 19,
        subdomains: 'abcd'
      }
    );

    tileLayersRef.current = {
      satellite: satelliteLayer,
      bathymetry: bathymetryLayer,
      dark: darkLayer
    };

    const map = L.map(mapContainerRef.current, {
      center: [centerLat, centerLon],
      zoom: 6,
      zoomControl: false,
      layers: [satelliteLayer]
    });

    L.control.zoom({ position: 'topleft' }).addTo(map);

    map.on('mousemove', (e: L.LeafletMouseEvent) => {
      setCurrentMouseCoords({ lat: e.latlng.lat, lng: e.latlng.lng });
    });

    const layerGroup = L.layerGroup().addTo(map);
    layersRef.current = layerGroup;

    map.on('click', (e: L.LeafletMouseEvent) => {
      onSelectLocation(e.latlng.lat, e.latlng.lng);
    });

    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Switch Base Tile Layers dynamically
  useEffect(() => {
    const map = mapInstanceRef.current;
    const tiles = tileLayersRef.current;
    if (!map || !tiles) return;

    map.removeLayer(tiles.satellite);
    map.removeLayer(tiles.bathymetry);
    map.removeLayer(tiles.dark);

    if (activeTileLayer === 'satellite') map.addLayer(tiles.satellite);
    else if (activeTileLayer === 'bathymetry') map.addLayer(tiles.bathymetry);
    else if (activeTileLayer === 'dark') map.addLayer(tiles.dark);
  }, [activeTileLayer]);

  // Smooth Glide
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;
    map.flyTo([centerLat, centerLon], map.getZoom() < 5 ? 6 : map.getZoom(), {
      duration: 1.2
    });
  }, [centerLat, centerLon]);

  // Update Dynamic Map Overlays, Geofences, PFZs, and Routes
  useEffect(() => {
    const map = mapInstanceRef.current;
    const layers = layersRef.current;
    if (!map || !layers) return;

    layers.clearLayers();

    // ── 1. Render IMBL International Maritime Boundaries (Dashed Amber) ──────
    if (showGeofenceLayer && gisLayers.imbl_boundaries) {
      gisLayers.imbl_boundaries.forEach((imbl) => {
        const polyline = L.polyline(imbl.coordinates, {
          color: '#f59e0b',
          weight: 3.5,
          dashArray: '8, 8',
          opacity: 0.95
        }).addTo(layers);

        polyline.bindPopup(`
          <div style="font-family: sans-serif; font-size: 12px; color: #1e293b;">
            <h4 style="margin: 0 0 4px 0; color: #d97706; font-weight: 800;">⚠️ ${imbl.name}</h4>
            <p style="margin: 0 0 2px 0;">Region: <b>${imbl.region}</b></p>
            <p style="margin: 0; color: #b45309; font-size: 11px;">${imbl.advisory}</p>
          </div>
        `);
      });
    }

    // ── 2. Render Restricted Waters & Naval Exclusion Polygons (Red) ────────
    if (showGeofenceLayer && gisLayers.restricted_zones) {
      gisLayers.restricted_zones.forEach((rz) => {
        const poly = L.polygon(rz.polygon, {
          color: '#ef4444',
          weight: 2.5,
          fillColor: '#ef4444',
          fillOpacity: 0.28
        }).addTo(layers);

        poly.bindPopup(`
          <div style="font-family: sans-serif; font-size: 12px; color: #1e293b;">
            <h4 style="margin: 0 0 4px 0; color: #dc2626; font-weight: 800;">🚫 ${rz.name}</h4>
            <p style="margin: 0 0 2px 0;">Category: <b>${rz.category}</b></p>
            <p style="margin: 0; color: #991b1b; font-size: 11px;">${rz.reason}</p>
          </div>
        `);
      });
    }

    // ── 3. Render Marine Protected Areas (MPAs) (Emerald) ───────────────────
    if (showMPALayer && gisLayers.marine_protected_areas) {
      gisLayers.marine_protected_areas.forEach((mpa) => {
        const poly = L.polygon(mpa.polygon, {
          color: '#10b981',
          weight: 2.0,
          fillColor: '#10b981',
          fillOpacity: 0.22
        }).addTo(layers);

        poly.bindPopup(`
          <div style="font-family: sans-serif; font-size: 12px; color: #1e293b;">
            <h4 style="margin: 0 0 4px 0; color: #059669; font-weight: 800;">🌿 ${mpa.name}</h4>
            <p style="margin: 0 0 2px 0;">Category: <b>${mpa.category} (${mpa.state})</b></p>
            <p style="margin: 0; color: #065f46; font-size: 11px;">${mpa.reason}</p>
          </div>
        `);
      });
    }

    // ── 4. Render Moored Ocean Buoys ─────────────────────────────────────────
    if (showBuoys) {
      GLOBAL_BUOYS.forEach((buoy) => {
        let iconHtml = '';
        if (buoy.type === 'Moored') {
          iconHtml = `
            <div style="display: flex; flex-direction: column; align-items: center;">
              <div style="width: 14px; height: 18px; background: #ef4444; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); border: 1.5px solid #ffffff; box-shadow: 0 0 6px rgba(239,68,68,0.8);"></div>
              <span style="font-family: monospace; font-weight: 800; font-size: 10px; color: #ffffff; text-shadow: 0 0 4px #000000; margin-top: 2px; white-space: nowrap;">${buoy.id}</span>
            </div>
          `;
        } else if (buoy.type === 'OMNI') {
          iconHtml = `
            <div style="display: flex; flex-direction: column; align-items: center;">
              <div style="width: 12px; height: 12px; background: #facc15; transform: rotate(45deg); border: 1.5px solid #000000; box-shadow: 0 0 6px rgba(250,204,21,0.8);"></div>
              <span style="font-family: monospace; font-weight: 800; font-size: 10px; color: #ffffff; text-shadow: 0 0 4px #000000; margin-top: 2px; white-space: nowrap;">${buoy.id}</span>
            </div>
          `;
        } else {
          iconHtml = `
            <div style="display: flex; flex-direction: column; align-items: center;">
              <div style="width: 12px; height: 12px; background: #94a3b8; border-radius: 50%; border: 1.5px solid #ffffff; box-shadow: 0 0 4px rgba(0,0,0,0.5);"></div>
              <span style="font-family: monospace; font-weight: 800; font-size: 10px; color: #cbd5e1; text-shadow: 0 0 4px #000000; margin-top: 2px; white-space: nowrap;">${buoy.id}</span>
            </div>
          `;
        }

        const buoyIcon = L.divIcon({
          className: 'buoy-custom-icon',
          html: iconHtml,
          iconSize: [30, 30],
          iconAnchor: [15, 10]
        });

        L.marker([buoy.lat, buoy.lon], { icon: buoyIcon })
          .bindPopup(`
            <div style="font-family: sans-serif; font-size: 12px;">
              <h4 style="margin: 0 0 4px 0; color: #0284c7; font-weight: 800;">${buoy.name}</h4>
              <p style="margin: 0 0 2px 0;">Type: <b>${buoy.type} Ocean Buoy</b></p>
              <p style="margin: 0; color: #475569; font-size: 11px;">Status: ${buoy.status}</p>
            </div>
          `)
          .addTo(layers);
      });
    }

    // ── 5. Active Target Radar Pin ──────────────────────────────────────────
    const markerColor = riskScore > 65 ? '#ef4444' : riskScore > 40 ? '#f59e0b' : '#10b981';
    const activeTargetIcon = L.divIcon({
      className: 'target-radar-icon',
      html: `
        <div style="position: relative; display: flex; align-items: center; justify-content: center;">
          <div style="width: 20px; height: 20px; border-radius: 50%; background: ${markerColor}; border: 3px solid #ffffff; box-shadow: 0 0 20px ${markerColor};"></div>
          <div style="position: absolute; width: 44px; height: 44px; border-radius: 50%; border: 2px solid ${markerColor}; opacity: 0.7; animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;"></div>
        </div>
      `,
      iconSize: [44, 44],
      iconAnchor: [22, 22]
    });

    const activeMarker = L.marker([centerLat, centerLon], { icon: activeTargetIcon }).addTo(layers);
    activeMarker.bindPopup(`
      <div style="text-align: center; font-family: sans-serif;">
        <h4 style="margin: 0 0 4px 0; color: #0284c7; font-weight: 800;">Target Inspection Point</h4>
        <p style="margin: 0; font-size: 12px; color: #475569;">Lat: ${centerLat.toFixed(4)}° N | Lon: ${centerLon.toFixed(4)}° E</p>
        <div style="margin-top: 8px; padding: 4px 8px; border-radius: 6px; background: ${markerColor}22; color: ${markerColor}; font-weight: 800; font-size: 12px; border: 1px solid ${markerColor}44;">
          XGBoost Risk Score: ${riskScore.toFixed(1)} / 100
        </div>
      </div>
    `);

    // ── 6. Cyclone Track & Cone ─────────────────────────────────────────────
    if (showCycloneLayer && cycloneData) {
      const { cone_of_uncertainty = [], historical_track = [], projected_track = [], name = 'Cyclone' } = cycloneData;

      if (Array.isArray(cone_of_uncertainty) && cone_of_uncertainty.length > 0) {
        const conePoints: [number, number][] = cone_of_uncertainty.map((p) => [p.lat, p.lon]);
        L.polygon(conePoints, {
          color: '#f59e0b',
          fillColor: '#f59e0b',
          fillOpacity: 0.18,
          weight: 2,
          dashArray: '5, 5'
        }).addTo(layers);
      }

      const allTrack = [...historical_track, ...projected_track];
      if (allTrack.length > 0) {
        const trackCoords: [number, number][] = allTrack.map(t => [t.lat, t.lon]);
        L.polyline(trackCoords, { color: '#ef4444', weight: 3, opacity: 0.85 }).addTo(layers);
      }
    }

    // ── 7. Potential Fishing Zones (PFZ) & Candidate Rankings ───────────────
    if (showPFZLayer && fishingData) {
      const candidates = fishingData.all_candidates || [
        {
          zone_id: fishingData.zone_id,
          name: 'Primary PFZ Zone',
          center: fishingData.center,
          fishing_potential_score: fishingData.pfz_indicator_score,
          recommendation_badge: fishingData.pfz_indicator_score > 60 ? 'RECOMMENDED' : 'CAUTION',
          safety_score: 85
        }
      ];

      candidates.forEach((cand: any) => {
        const isRec = cand.recommendation_badge === 'RECOMMENDED';
        const isRej = cand.recommendation_badge === 'REJECTED' || cand.in_restricted_waters;
        const pfzColor = isRej ? '#ef4444' : (isRec ? '#10b981' : '#f59e0b');

        L.circle([cand.center.lat, cand.center.lon], {
          radius: 12000,
          color: pfzColor,
          fillColor: pfzColor,
          fillOpacity: 0.25,
          weight: 2
        }).addTo(layers);

        const pfzPin = L.divIcon({
          className: 'pfz-marker-pin',
          html: `
            <div style="display: flex; flex-direction: column; align-items: center; background: ${pfzColor}; padding: 3px 6px; border-radius: 8px; border: 1.5px solid #ffffff; box-shadow: 0 2px 8px rgba(0,0,0,0.5);">
              <span style="font-size: 10px; font-weight: 800; color: #ffffff; white-space: nowrap;">🐟 ${cand.name || cand.zone_id}</span>
              <span style="font-size: 9px; font-weight: 900; color: #ffffff; opacity: 0.9;">Score: ${cand.fishing_potential_score || 85}</span>
            </div>
          `,
          iconSize: [100, 34],
          iconAnchor: [50, 17]
        });

        L.marker([cand.center.lat, cand.center.lon], { icon: pfzPin })
          .bindPopup(`
            <div style="font-family: sans-serif; font-size: 12px;">
              <h4 style="margin: 0 0 4px 0; color: ${pfzColor}; font-weight: 800;">${cand.name || cand.zone_id}</h4>
              <p style="margin: 0 0 2px 0;">Potential: <b>${cand.fishing_potential_score || 85}/100</b></p>
              <p style="margin: 0 0 2px 0;">Status: <b>${cand.recommendation_badge || 'ACTIVE'}</b></p>
              <p style="margin: 0; color: #475569; font-size: 11px;">${cand.recommendation_reason || fishingData.safety_advisory}</p>
            </div>
          `)
          .addTo(layers);
      });
    }

    // ── 8. Route Pathfinder & Geofence-Aware Route Rejection ─────────────────
    if (showRouteLayer && routeData && routeData.routes) {
      routeData.routes.forEach((route) => {
        const isRec = route.route_id === routeData.recommended_route_id;
        const isRejected = route.is_rejected || false;
        
        const pathCoords: [number, number][] = route.waypoints.map(w => [w.lat, w.lon]);

        const routePoly = L.polyline(pathCoords, {
          color: isRejected ? '#ef4444' : (isRec ? '#06b6d4' : '#64748b'),
          weight: isRec ? 5 : (isRejected ? 3.5 : 3),
          opacity: isRec ? 0.95 : (isRejected ? 0.8 : 0.6),
          dashArray: isRejected ? '6, 6' : (isRec ? undefined : '4, 4')
        }).addTo(layers);

        routePoly.bindPopup(`
          <div style="font-family: sans-serif; font-size: 12px;">
            <h4 style="margin: 0 0 4px 0; color: ${isRejected ? '#ef4444' : '#06b6d4'}; font-weight: 800;">
              ${route.name} ${isRejected ? '🚫 [REJECTED]' : (isRec ? '★ [RECOMMENDED]' : '')}
            </h4>
            <p style="margin: 0 0 2px 0;">Distance: <b>${route.total_distance_km} km</b> | ETA: <b>${route.estimated_time_hours} hrs</b></p>
            <p style="margin: 0 0 2px 0;">Average Risk: <b>${route.average_risk_score}/100</b></p>
            ${isRejected ? `<p style="margin: 0; color: #dc2626; font-weight: 800; font-size: 11px;">${route.rejection_reason || 'Intersects Restricted Zone'}</p>` : ''}
          </div>
        `);
      });
    }

  }, [
    centerLat, centerLon, showBuoys, showCycloneLayer, showPFZLayer, showRouteLayer,
    showGeofenceLayer, showMPALayer, cycloneData, routeData, fishingData, riskScore, gisLayers
  ]);

  return (
    <div className="relative w-full h-full min-h-[580px] rounded-3xl overflow-hidden border border-slate-800 shadow-2xl bg-slate-950">
      {/* Map Canvas */}
      <div ref={mapContainerRef} className="w-full h-full z-0" />

      {/* Top-Right Tile Mode Switcher */}
      <div className="absolute top-4 left-14 z-[1000] flex items-center space-x-1.5 p-1 rounded-2xl bg-slate-900/90 backdrop-blur-md border border-slate-700 shadow-xl">
        <button
          onClick={() => setActiveTileLayer('satellite')}
          className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
            activeTileLayer === 'satellite'
              ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md'
              : 'text-slate-300 hover:text-white'
          }`}
        >
          Satellite
        </button>
        <button
          onClick={() => setActiveTileLayer('bathymetry')}
          className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
            activeTileLayer === 'bathymetry'
              ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md'
              : 'text-slate-300 hover:text-white'
          }`}
        >
          Bathymetry
        </button>
        <button
          onClick={() => setActiveTileLayer('dark')}
          className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
            activeTileLayer === 'dark'
              ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md'
              : 'text-slate-300 hover:text-white'
          }`}
        >
          Dark Nautical
        </button>
      </div>

      {/* Top-Right GIS Layer Legend & Toggles */}
      {showLegend ? (
        <div className="absolute top-4 right-4 z-[1000] w-72 rounded-2xl p-3.5 bg-slate-900/95 backdrop-blur-md border border-slate-700 shadow-2xl text-slate-200 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <div className="flex items-center space-x-2">
              <Sliders className="w-4 h-4 text-cyan-400" />
              <span className="font-extrabold text-xs text-white">GIS Spatial Boundaries</span>
            </div>
            <button
              onClick={() => setShowLegend(false)}
              className="p-0.5 rounded text-slate-400 hover:text-white transition-colors"
            >
              <X className="w-4 h-4 font-bold" />
            </button>
          </div>

          <div className="space-y-2 text-[11px] font-medium">
            <label className="flex items-center justify-between cursor-pointer">
              <span className="flex items-center space-x-1.5">
                <span className="w-3 h-0.5 border-t-2 border-dashed border-amber-400" />
                <span>IMBL International Border</span>
              </span>
              <input
                type="checkbox"
                checked={showGeofenceLayer}
                onChange={(e) => setShowGeofenceLayer(e.target.checked)}
                className="accent-cyan-500 cursor-pointer"
              />
            </label>

            <label className="flex items-center justify-between cursor-pointer">
              <span className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded bg-red-500/60 border border-red-500" />
                <span>Restricted Naval / Oil Zones</span>
              </span>
              <input
                type="checkbox"
                checked={showGeofenceLayer}
                onChange={(e) => setShowGeofenceLayer(e.target.checked)}
                className="accent-cyan-500 cursor-pointer"
              />
            </label>

            <label className="flex items-center justify-between cursor-pointer">
              <span className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded bg-emerald-500/60 border border-emerald-500" />
                <span>Marine Protected Areas (MPA)</span>
              </span>
              <input
                type="checkbox"
                checked={showMPALayer}
                onChange={(e) => setShowMPALayer(e.target.checked)}
                className="accent-cyan-500 cursor-pointer"
              />
            </label>

            <label className="flex items-center justify-between cursor-pointer">
              <span className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
                <span>Candidate PFZ Sectors</span>
              </span>
              <input
                type="checkbox"
                checked={showPFZLayer}
                onChange={(e) => setShowPFZLayer(e.target.checked)}
                className="accent-cyan-500 cursor-pointer"
              />
            </label>

            <label className="flex items-center justify-between cursor-pointer">
              <span className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
                <span>A* Risk-Bypassing Routes</span>
              </span>
              <input
                type="checkbox"
                checked={showRouteLayer}
                onChange={(e) => setShowRouteLayer(e.target.checked)}
                className="accent-cyan-500 cursor-pointer"
              />
            </label>

            <label className="flex items-center justify-between cursor-pointer">
              <span className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-red-400" />
                <span>Cyclone Storm Envelope</span>
              </span>
              <input
                type="checkbox"
                checked={showCycloneLayer}
                onChange={(e) => setShowCycloneLayer(e.target.checked)}
                className="accent-cyan-500 cursor-pointer"
              />
            </label>
          </div>
        </div>
      ) : (
        <button
          onClick={() => setShowLegend(true)}
          className="absolute top-4 right-4 z-[1000] px-3 py-1.5 rounded-xl bg-slate-900/90 text-slate-200 border border-slate-700 text-xs font-bold shadow-xl flex items-center space-x-1.5"
        >
          <Sliders className="w-3.5 h-3.5 text-cyan-400" />
          <span>GIS Layers</span>
        </button>
      )}

      {/* Bottom-Right Live Coordinates Bar */}
      <div className="absolute bottom-3 right-3 z-[1000] px-3 py-1.5 rounded-lg bg-slate-900/90 text-slate-200 border border-slate-700 text-xs font-mono font-extrabold shadow-md">
        Lat: {currentMouseCoords.lat.toFixed(4)}° N, Lng: {currentMouseCoords.lng.toFixed(4)}° E
      </div>

      {/* Bottom-Left Base Tile Status Pill */}
      <div className="absolute bottom-3 left-3 z-[1000] px-3 py-1.5 rounded-lg bg-slate-900/90 text-cyan-400 border border-slate-700 text-xs font-mono font-bold shadow-md uppercase">
        Layer: {activeTileLayer} | PostGIS Standard
      </div>
    </div>
  );
};
