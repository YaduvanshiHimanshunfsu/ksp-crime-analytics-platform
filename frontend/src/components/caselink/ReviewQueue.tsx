import React from "react";
import type { Link } from "../../types";

export default function ReviewQueue({ links }: { links: Link[] }) {
  return (
    <>
      {links.slice(0, 4).map((link) => (
        <div className="link-row" key={`${link.left_case_id}-${link.right_case_id}`}>
          <div>
            <b>Case {link.left_case_id} ↔ Case {link.right_case_id}</b>
            <span>{link.left_district} · {link.right_district}</span>
          </div>
          <strong>{link.confidence}%</strong>
          <small>Name {Math.round(link.name_similarity * 100)}% · age gap {link.age_gap} · MO {link.same_modus_operandi ? "matches" : "differs"}</small>
          <div className="review-actions">
            <button>Confirm</button>
            <button>Reject</button>
            <button>Defer</button>
          </div>
        </div>
      ))}
    </>
  );
}
