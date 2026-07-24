export type Hotspot = {
  id: string;
  district: string;
  station: string;
  crime_head: string;
  latitude: number;
  longitude: number;
  incidents_28d: number;
  change: number;
  risk_score: number;
};

export type Trend = { week: string; incidents: number; expected: number; anomaly: boolean };

export type Alert = {
  id: string;
  title: string;
  district: string;
  risk_score: number;
  confidence: string;
  reason: string;
  credibility: { reported_source_share: number; geo_complete: number; model_status: string };
};

export type ShapDriver = {
  feature: string;
  readable_name: string;
  shap_value: number;
  direction: "increases risk" | "decreases risk";
  feature_value: number | null;
};

export type Forecast = {
  area: string;
  district: string;
  crime_head: string;
  next_week_range: number[];
  risk_score: number;
  drivers: ShapDriver[];
  use: string;
};

export type Link = {
  left_case_id: string;
  right_case_id: string;
  left_name: string;
  right_name: string;
  left_district: string;
  right_district: string;
  confidence: number;
  name_similarity: number;
  age_gap: number;
  same_modus_operandi: boolean;
  status: string;
};

export type Network = {
  nodes: { id: string; label: string; person: string; district: string }[];
  edges: { source: string; target: string; confidence: number }[];
};

export type Overview = {
  total_cases: number;
  last_28_days: number;
  change_percent: number;
  active_alerts: number;
  reported_source_share: number;
  latest_data_date: string;
  synthetic_notice: string;
};

export type Correlation = { factor: string; finding: string; caveat: string };
export type RepeatPattern = { entity: string; case_count: number; districts: string[]; crime_heads: string[]; last_seen: string; status: string };

export type DistrictDrilldown = {
  district: string;
  total_cases: number;
  stations: { station: string; total_cases: number; top_crime: string; recent_cases: number }[];
};

export type DistrictBenchmark = {
  district: string;
  cases_reported: number;
};

export type DistrictTrend = {
  year: number;
  total_crimes: number;
};

export type CalibrationReport = {
  status: string;
  synthetic_total?: number;
  real_total_2025?: number;
  scale_factor?: number;
  district_correlation?: number;
  interpretation?: string;
};

export type ModelCard = {
  model_version: string;
  algorithm: string;
  feature_count: number;
  train_rows: number;
  test_rows: number;
  temporal_split: string;
  model_mae: number;
  baseline_mae: number;
  improvement_percent: number;
  prohibited_use?: string;
  explainability?: string;
  data_sources?: Record<string, string>;
};
