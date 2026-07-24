import React from "react";
import { logFrontendEvent } from "../../api";

export type View = "Command map" | "CaseLink" | "Risk forecast" | "Governance";

const districts = ["All Karnataka", "Bengaluru Urban", "Mysuru", "Hubballi-Dharwad", "Mangaluru", "Kalaburagi"];
const crimeHeads = ["All crime heads", "Theft", "Burglary", "Cyber Fraud", "Assault", "Robbery"];

type ControlBarProps = {
  view: View;
  setView: (v: View) => void;
  district: string;
  setDistrict: (d: string) => void;
  crimeHead: string;
  setCrimeHead: (c: string) => void;
};

export default function ControlBar({ view, setView, district, setDistrict, crimeHead, setCrimeHead }: ControlBarProps) {
  return (
    <section className="controlbar">
      <div className="view-tabs">
        {(["Command map", "CaseLink", "Risk forecast", "Governance"] as View[]).map((item) => (
          <button 
            key={item} 
            className={view === item ? "active" : ""} 
            onClick={() => { 
              setView(item); 
              logFrontendEvent("view_changed", { view: item }); 
            }}
          >
            {item}
          </button>
        ))}
      </div>
      <div className="filters">
        <label>District
          <select value={district} onChange={(event) => setDistrict(event.target.value)}>
            {districts.map((item) => <option key={item}>{item}</option>)}
          </select>
        </label>
        <label>Crime type
          <select value={crimeHead} onChange={(event) => setCrimeHead(event.target.value)}>
            {crimeHeads.map((item) => <option key={item}>{item}</option>)}
          </select>
        </label>
      </div>
    </section>
  );
}
