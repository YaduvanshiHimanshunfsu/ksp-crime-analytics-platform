import { alerts, correlations, forecasts, hotspots, links, network, overview, repeatPatterns, trends } from "./mockData";
import type { Alert, Correlation, Forecast, Hotspot, Link, Network, Overview, RepeatPattern, Trend, DistrictBenchmark, DistrictTrend, CalibrationReport, ModelCard } from "./types";

const API_ROOT = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export function logFrontendEvent(event: string, details: Record<string, string | number | boolean> = {}) {
  void fetch(`${API_ROOT}/api/v1/telemetry`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ event, details }),
  }).catch(() => undefined);
}

export async function submitAlertFeedback(alertId: string, useful: boolean, reason: string) {
  try {
    const response = await fetch(`${API_ROOT}/api/v1/alerts/${alertId}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ useful, reason }),
    });
    return response.ok;
  } catch {
    return false;
  }
}

async function get<T>(path: string, fallback: T): Promise<{ data: T; live: boolean }> {
  try {
    const response = await fetch(`${API_ROOT}${path}`);
    if (!response.ok) throw new Error("API unavailable");
    return { data: (await response.json()) as T, live: true };
  } catch {
    return { data: fallback, live: false };
  }
}

export async function loadDashboard(district: string, crimeHead: string) {
  const query = new URLSearchParams();
  if (district !== "All Karnataka") query.set("district", district);
  if (crimeHead !== "All crime heads") query.set("crime_head", crimeHead);
  const suffix = query.size ? `?${query}` : "";
  const [
    { data: summary, live: liveOverview },
    { data: mapHotspots, live: liveHotspots },
    { data: chartTrends, live: liveTrends },
    { data: currentAlerts, live: liveAlerts },
    { data: currentForecasts, live: liveForecasts },
    { data: currentLinks, live: liveLinks },
    { data: currentNetwork, live: liveNetwork },
    { data: currentCorrelations, live: liveCorrelations },
    { data: patterns, live: livePatterns }
  ] = await Promise.all([
    get<Overview>(`/api/v1/overview${suffix}`, overview), get<Hotspot[]>(`/api/v1/hotspots${suffix}`, hotspots), get<Trend[]>(`/api/v1/trends${suffix}`, trends),
    get<Alert[]>(`/api/v1/alerts${suffix}`, alerts), get<Forecast[]>(`/api/v1/risk-forecast${suffix}`, forecasts), get<Link[]>("/api/v1/case-links", links),
    get<Network>("/api/v1/network", network), get<Correlation[]>(`/api/v1/correlations${suffix}`, correlations), get<RepeatPattern[]>("/api/v1/repeat-patterns", repeatPatterns),
  ]);
  
  const isLive = liveOverview || liveHotspots || liveTrends || liveAlerts || liveForecasts || liveLinks || liveNetwork || liveCorrelations || livePatterns;
  return { summary, mapHotspots, chartTrends, currentAlerts, currentForecasts, currentLinks, currentNetwork, currentCorrelations, patterns, isLive };
}

export async function getDistrictDrilldown(district: string) {
  return get(`/api/v1/district-drilldown?district=${encodeURIComponent(district)}`, { district, total_cases: 0, stations: [] });
}

export async function getDistrictBenchmark() {
  return get<{ district: string; cases_reported: number }[]>(`/api/v1/district-benchmark`, []);
}

export async function getDistrictTrends(district: string) {
  return get<{ year: number; total_crimes: number }[]>(`/api/v1/district-trends?district=${encodeURIComponent(district)}`, []);
}

export async function getCalibrationReport() {
  return get(`/api/v1/calibration-report`, { status: "offline" });
}

export async function getModelCard() {
  return get(`/api/v1/model-card`, { error: "offline" });
}
