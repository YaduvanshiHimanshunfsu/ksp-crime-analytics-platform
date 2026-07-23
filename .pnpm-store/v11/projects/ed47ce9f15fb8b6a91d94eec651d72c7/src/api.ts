import { alerts, correlations, forecasts, hotspots, links, network, overview, repeatPatterns, trends } from "./mockData";
import type { Alert, Correlation, Forecast, Hotspot, Link, Network, Overview, RepeatPattern, Trend } from "./types";

const API_ROOT = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function get<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${API_ROOT}${path}`);
    if (!response.ok) throw new Error("API unavailable");
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export async function loadDashboard(district: string, crimeHead: string) {
  const query = new URLSearchParams();
  if (district !== "All Karnataka") query.set("district", district);
  if (crimeHead !== "All crime heads") query.set("crime_head", crimeHead);
  const suffix = query.size ? `?${query}` : "";
  const [summary, mapHotspots, chartTrends, currentAlerts, currentForecasts, currentLinks, currentNetwork, currentCorrelations, patterns] = await Promise.all([
    get<Overview>(`/api/v1/overview${suffix}`, overview), get<Hotspot[]>(`/api/v1/hotspots${suffix}`, hotspots), get<Trend[]>(`/api/v1/trends${suffix}`, trends),
    get<Alert[]>(`/api/v1/alerts${suffix}`, alerts), get<Forecast[]>(`/api/v1/risk-forecast${suffix}`, forecasts), get<Link[]>("/api/v1/case-links", links),
    get<Network>("/api/v1/network", network), get<Correlation[]>(`/api/v1/correlations${suffix}`, correlations), get<RepeatPattern[]>("/api/v1/repeat-patterns", repeatPatterns),
  ]);
  return { summary, mapHotspots, chartTrends, currentAlerts, currentForecasts, currentLinks, currentNetwork, currentCorrelations, patterns };
}

