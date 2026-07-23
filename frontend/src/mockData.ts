import type { Alert, Correlation, Forecast, Hotspot, Link, Network, Overview, RepeatPattern, Trend } from "./types";

export const overview: Overview = {
  total_cases: 3470,
  last_28_days: 278,
  change_percent: 11.4,
  active_alerts: 8,
  reported_source_share: 88,
  latest_data_date: "2026-07-22",
  synthetic_notice: "Synthetic, schema-faithful demonstration data - not live police intelligence.",
};

export const hotspots: Hotspot[] = [
  { id: "h3-demo-0", district: "Mysuru", station: "Nazarbad", crime_head: "Theft", latitude: 12.3, longitude: 76.64, incidents_28d: 12, change: 5, risk_score: 99 },
  { id: "h3-demo-1", district: "Bengaluru Urban", station: "Jayanagar", crime_head: "Cyber Fraud", latitude: 12.93, longitude: 77.58, incidents_28d: 9, change: 3, risk_score: 86 },
  { id: "h3-demo-2", district: "Mangaluru", station: "Bunder", crime_head: "Burglary", latitude: 12.91, longitude: 74.86, incidents_28d: 8, change: 1, risk_score: 78 },
  { id: "h3-demo-3", district: "Hubballi-Dharwad", station: "Vidyanagar", crime_head: "Theft", latitude: 15.36, longitude: 75.12, incidents_28d: 7, change: 2, risk_score: 75 },
  { id: "h3-demo-4", district: "Kalaburagi", station: "Gulbarga", crime_head: "Robbery", latitude: 17.33, longitude: 76.83, incidents_28d: 6, change: 0, risk_score: 66 },
];

export const trends: Trend[] = [
  { week: "2026-04-20", incidents: 52, expected: 48, anomaly: false }, { week: "2026-04-27", incidents: 47, expected: 49, anomaly: false },
  { week: "2026-05-04", incidents: 56, expected: 49, anomaly: false }, { week: "2026-05-11", incidents: 61, expected: 51, anomaly: false },
  { week: "2026-05-18", incidents: 72, expected: 54, anomaly: true }, { week: "2026-05-25", incidents: 69, expected: 58, anomaly: false },
  { week: "2026-06-01", incidents: 76, expected: 61, anomaly: false }, { week: "2026-06-08", incidents: 81, expected: 65, anomaly: false },
  { week: "2026-06-15", incidents: 91, expected: 70, anomaly: false }, { week: "2026-06-22", incidents: 102, expected: 75, anomaly: true },
  { week: "2026-06-29", incidents: 89, expected: 81, anomaly: false }, { week: "2026-07-06", incidents: 96, expected: 85, anomaly: false },
  { week: "2026-07-13", incidents: 108, expected: 89, anomaly: false }, { week: "2026-07-20", incidents: 44, expected: 92, anomaly: false },
];

export const alerts: Alert[] = hotspots.map((hotspot, index) => ({
  id: hotspot.id,
  title: `${hotspot.crime_head} pattern near ${hotspot.station}`,
  district: hotspot.district,
  risk_score: hotspot.risk_score,
  confidence: index < 3 ? "High" : "Review required",
  reason: `${hotspot.incidents_28d} reports in 28 days; change of ${hotspot.change >= 0 ? "+" : ""}${hotspot.change} vs previous period.`,
  credibility: { reported_source_share: 88, geo_complete: 100, model_status: "advisory - analyst review required" },
}));

export const forecasts: Forecast[] = hotspots.map((hotspot) => ({
  area: hotspot.station,
  district: hotspot.district,
  crime_head: hotspot.crime_head,
  next_week_range: [1, 4],
  risk_score: hotspot.risk_score,
  drivers: ["recent reported-incident trend", "same-category 28-day activity", "calendar and seasonal pattern"],
  use: "Prioritise analyst review; not a person-level prediction or patrol directive.",
}));

export const links: Link[] = [
  { left_case_id: "5", right_case_id: "11", left_name: "S. Pasha", right_name: "S. Pasha", left_district: "Hubballi-Dharwad", right_district: "Mysuru", confidence: 100, name_similarity: 1, age_gap: 0, same_modus_operandi: true, status: "candidate_review_required" },
  { left_case_id: "209", right_case_id: "5", left_name: "S. Pasha", right_name: "S. Pasha", left_district: "Bengaluru Urban", right_district: "Hubballi-Dharwad", confidence: 100, name_similarity: 1, age_gap: 0, same_modus_operandi: true, status: "candidate_review_required" },
  { left_case_id: "301", right_case_id: "644", left_name: "A. Kumar", right_name: "Arun Kumar", left_district: "Mysuru", right_district: "Mangaluru", confidence: 82, name_similarity: 0.75, age_gap: 1, same_modus_operandi: true, status: "candidate_review_required" },
];

export const network: Network = {
  nodes: [
    { id: "5", label: "Case 5", person: "S. Pasha", district: "Hubballi-Dharwad" }, { id: "11", label: "Case 11", person: "S. Pasha", district: "Mysuru" },
    { id: "209", label: "Case 209", person: "S. Pasha", district: "Bengaluru Urban" }, { id: "301", label: "Case 301", person: "A. Kumar", district: "Mysuru" },
    { id: "644", label: "Case 644", person: "Arun Kumar", district: "Mangaluru" },
  ],
  edges: [{ source: "5", target: "11", confidence: 100 }, { source: "5", target: "209", confidence: 100 }, { source: "301", target: "644", confidence: 82 }],
};

export const correlations: Correlation[] = [
  { factor: "Festival calendar", finding: "+18.0% observed count difference on configured calendar dates.", caveat: "Association only; sample size and reporting effects apply." },
  { factor: "High rainfall periods", finding: "411 synthetic cases fall in the high-rainfall band.", caveat: "Not evidence that rainfall causes crime." },
  { factor: "Data-source mix", finding: "88% are reported/citizen-source records.", caveat: "Police-observed events remain outside the risk-training target." },
];

export const repeatPatterns: RepeatPattern[] = [
  { entity: "Reviewed entity Alpha", case_count: 47, districts: ["Bengaluru Urban", "Mysuru", "Mangaluru"], crime_heads: ["Theft", "Burglary"], last_seen: "2026-07-19", status: "Case-history tracking after analyst confirmation" },
  { entity: "Reviewed entity Beta", case_count: 39, districts: ["Hubballi-Dharwad", "Mysuru"], crime_heads: ["Theft", "Robbery"], last_seen: "2026-07-18", status: "Case-history tracking after analyst confirmation" },
];

