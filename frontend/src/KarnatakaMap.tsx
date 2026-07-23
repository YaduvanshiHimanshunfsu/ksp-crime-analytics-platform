import { useEffect, useRef } from "react";
import L from "leaflet";
import type { Alert, Hotspot } from "./types";

function riskColor(score: number) {
  if (score >= 85) return "#f16361";
  if (score >= 70) return "#f5b942";
  return "#45c9a3";
}

export default function KarnatakaMap({ hotspots, selected, onSelectHotspot, onSelectDistrict }: { hotspots: Hotspot[]; selected: Alert | null; onSelectHotspot: (hotspot: Hotspot) => void; onSelectDistrict: (district: string) => void }) {
  const mapRef = useRef<HTMLDivElement>(null);
  const leafletRef = useRef<L.Map | null>(null);

  useEffect(() => {
    if (!mapRef.current) return;
    if (!leafletRef.current) {
      leafletRef.current = L.map(mapRef.current).setView([15.3173, 75.7139], 6);
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
      }).addTo(leafletRef.current);
    }
    const map = leafletRef.current;
    
    map.eachLayer((layer: L.Layer) => {
      if (layer instanceof L.CircleMarker) map.removeLayer(layer);
    });

    hotspots.forEach(spot => {
      L.circleMarker([spot.latitude, spot.longitude], {
        radius: 6 + spot.risk_score / 15,
        color: riskColor(spot.risk_score),
        fillColor: riskColor(spot.risk_score),
        fillOpacity: 0.5,
        weight: 1
      }).bindTooltip(`${spot.station} (${spot.district})<br>Risk: ${spot.risk_score}<br>Cases: ${spot.incidents_28d}`)
        .on('click', () => {
          onSelectHotspot(spot);
          onSelectDistrict(spot.district);
        })
        .addTo(map);
    });
  }, [hotspots, onSelectHotspot, onSelectDistrict]);

  return <div className="map-frame" style={{ position: "relative" }}>
    <div ref={mapRef} style={{ height: "420px", width: "100%", borderRadius: "8px", background: "#0a0a0a" }} />
    <div className="map-legend"><span><i className="legend-low" /> monitored</span><span><i className="legend-high" style={{ background: "#f16361" }}/> elevated</span></div>
  </div>;
}
