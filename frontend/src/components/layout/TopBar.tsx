import React from "react";

export default function TopBar({ isLive }: { isLive: boolean }) {
  return (
    <header className="topbar">
      <div className="brand">
        <div className="brand-mark">D</div>
        <div>
          <small>KARNATAKA STATE POLICE · SYNTHETIC DEMO</small>
          <h1>KSP Dṛṣṭi</h1>
        </div>
      </div>
      <div className="topbar-actions">
        <span className="status-pill"><i /> analyst-reviewed intelligence</span>
        <button className="profile">SP <span>⌄</span></button>
      </div>
    </header>
  );
}
