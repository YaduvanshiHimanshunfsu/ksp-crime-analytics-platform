import React from "react";

type MetricCardProps = {
  label: string;
  value: string;
  note: string;
  tone?: "default" | "attention" | "positive";
};

export default function MetricCard({ label, value, note, tone = "default" }: MetricCardProps) {
  return (
    <article className={`metric-card ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{note}</small>
    </article>
  );
}
