import { useState, useEffect } from "react";
import { loadDashboard, logFrontendEvent, getDistrictDrilldown } from "../api";
import type { Alert, Hotspot, Network, Trend, DistrictDrilldown, Overview, Forecast, Link, Correlation, RepeatPattern } from "../types";

export type DashboardData = {
  summary: Overview;
  mapHotspots: Hotspot[];
  chartTrends: Trend[];
  currentAlerts: Alert[];
  currentForecasts: Forecast[];
  currentLinks: Link[];
  currentNetwork: Network;
  currentCorrelations: Correlation[];
  patterns: RepeatPattern[];
  isLive: boolean;
};

export function useDashboardData(district: string, crimeHead: string) {
  const [data, setData] = useState<DashboardData | null>(null);
  const [drilldown, setDrilldown] = useState<DistrictDrilldown | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);

    loadDashboard(district, crimeHead)
      .then((bundle) => {
        if (active) setData(bundle);
      })
      .catch((err) => {
        if (active) setError(err.message || "Failed to load dashboard data");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    logFrontendEvent("dashboard_filter_changed", { district, crime_head: crimeHead });
    
    if (district !== "All Karnataka") {
      getDistrictDrilldown(district)
        .then(res => { if (active) setDrilldown(res.data); })
        .catch(() => { if (active) setDrilldown(null); });
    } else {
      setDrilldown(null);
    }

    return () => { active = false; };
  }, [district, crimeHead]);

  return { data, drilldown, loading, error };
}
