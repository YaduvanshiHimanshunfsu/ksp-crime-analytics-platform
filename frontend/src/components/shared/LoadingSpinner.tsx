import React from "react";

export default function LoadingSpinner({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="loading-state" style={{ padding: '4rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', color: '#8b949e' }}>
      <div className="loader" style={{ width: '32px', height: '32px', border: '3px solid rgba(255,255,255,0.1)', borderTopColor: '#165688', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
      <span>{message}</span>
      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
