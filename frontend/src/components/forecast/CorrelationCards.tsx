import React from "react";
import type { Correlation } from "../../types";

export default function CorrelationCards({ correlations }: { correlations: Correlation[] }) {
  return (
    <section className="correlation-section">
      <p className="eyebrow">SOCIO-ECONOMIC AND CONTEXTUAL ASSOCIATIONS</p>
      {correlations.map((item) => (
        <article className="correlation-card" key={item.factor}>
          <h3>{item.factor}</h3>
          <p>{item.finding}</p>
          <small>{item.caveat}</small>
        </article>
      ))}
    </section>
  );
}
