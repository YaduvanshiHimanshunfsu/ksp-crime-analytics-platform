import React from "react";
import type { RepeatPattern } from "../../types";

export default function RepeatPatterns({ patterns }: { patterns: RepeatPattern[] }) {
  return (
    <>
      {patterns.map((pattern) => (
        <div className="pattern-row" key={pattern.entity}>
          <b>{pattern.entity}</b>
          <span>{pattern.case_count} linked cases</span>
          <span>{pattern.districts.join(" · ")}</span>
          <span>{pattern.crime_heads.join(", ")}</span>
          <small>Last seen {pattern.last_seen}</small>
        </div>
      ))}
    </>
  );
}
