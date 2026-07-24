import React, { useState, useCallback } from "react";
import type { DashboardData } from "../../hooks/useDashboardData";
import type { Alert, Hotspot } from "../../types";
import { logFrontendEvent } from "../../api";
import MetricCard from "./MetricCard";
import TrendChart from "./TrendChart";
import IntelligenceCard from "./IntelligenceCard";
import DrilldownPanel from "./DrilldownPanel";
import DistrictBenchmark from "../public-data/DistrictBenchmark";
import KarnatakaMap from "../../KarnatakaMap";

type Props = {
  data: DashboardData;
  district: string;
  setDistrict: (dist: string) => void;
  drilldown: any;
};

export default function CommandMapView({ data, district, setDistrict, drilldown }: Props) {
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(data.currentAlerts[0] ?? null);

  const handleSelectHotspot = useCallback((spot: Hotspot) => {
    setSelectedAlert(data.currentAlerts.find(a => a.id === spot.id) ?? null);
    logFrontendEvent("hotspot_selected", { hotspot_id: spot.id, station: spot.station, district: spot.district });
  }, [data.currentAlerts]);

  const handleSelectDistrict = useCallback((dist: string) => {
    setDistrict(dist);
    logFrontendEvent("district_selected", { district: dist });
  }, [setDistrict]);

  return (
    <section className="dashboard-grid">
      <aside className="left-rail">
        <p className="eyebrow">STATE SITUATION</p>
        <MetricCard 
          label="Reported cases" 
          value={data.summary.total_cases.toLocaleString()} 
          note="selected synthetic dataset" 
        />
        <MetricCard 
          label="Last 28 days" 
          value={data.summary.last_28_days.toString()} 
          note={`${data.summary.change_percent >= 0 ? "+" : ""}${data.summary.change_percent}% vs prior 28 days`} 
          tone={data.summary.change_percent > 0 ? "attention" : "positive"} 
        />
        <MetricCard 
          label="Active review alerts" 
          value={data.summary.active_alerts.toString()} 
          note="advisory only" 
        />
        <div className="layer-control">
          <p className="eyebrow">MAP LAYERS</p>
          <label><input type="checkbox" defaultChecked /> Credibility-scored hotspots</label>
          <label><input type="checkbox" defaultChecked /> Trend anomalies</label>
          <label><input type="checkbox" /> Reviewed case density</label>
        </div>
        
        <DistrictBenchmark />
      </aside>

      <section className="map-column">
        <div className="section-heading">
          <div>
            <p className="eyebrow">PLACE-BASED INTELLIGENCE</p>
            <h2>Where reported patterns need attention</h2>
          </div>
          <span className="date-pill">Data through {data.summary.latest_data_date}</span>
        </div>
        
        <KarnatakaMap 
          hotspots={data.mapHotspots} 
          selected={selectedAlert} 
          onSelectHotspot={handleSelectHotspot} 
          onSelectDistrict={handleSelectDistrict} 
        />
        
        <article className="panel trend-panel">
          <div className="panel-title">
            <div>
              <p className="eyebrow">TREND AND ANOMALY DETECTION</p>
              <h3>Weekly reported incidents</h3>
            </div>
            <span className="legend-line">Observed <i /> Expected</span>
          </div>
          <TrendChart points={data.chartTrends} />
        </article>
      </section>

      <aside className="right-rail">
        <IntelligenceCard selectedAlert={selectedAlert} />
        <DrilldownPanel drilldown={drilldown} />
      </aside>
    </section>
  );
}
