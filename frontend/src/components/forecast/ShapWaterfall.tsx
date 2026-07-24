import React from "react";
import type { ShapDriver } from "../../types";

export default function ShapWaterfall({ drivers }: { drivers: ShapDriver[] }) {
  if (!drivers || drivers.length === 0) return <div className="empty">No drivers available</div>;

  return (
    <div className="shap-waterfall" style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '8px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#8b949e', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '4px', marginBottom: '4px' }}>
        <span style={{ flex: 1, textAlign: 'left' }}>← decreases risk</span>
        <span style={{ width: '40px' }} />
        <span style={{ flex: 1, textAlign: 'right' }}>increases risk →</span>
      </div>
      
      {drivers.map(driver => {
        const isPositive = driver.direction === "increases risk";
        const width = Math.min(Math.abs(driver.shap_value) * 100, 100);
        
        return (
          <div key={driver.feature} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}>
            <div style={{ width: '120px', textAlign: 'right', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', color: '#e6edf3' }} title={driver.readable_name}>
              {driver.readable_name}
            </div>
            
            <div style={{ flex: 1, display: 'flex', position: 'relative', height: '16px' }}>
              <div style={{ position: 'absolute', left: '50%', top: 0, bottom: 0, width: '1px', background: 'rgba(255,255,255,0.2)' }} />
              
              {isPositive ? (
                <div style={{ width: '50%', marginLeft: '50%', display: 'flex' }}>
                  <div style={{ width: `${width}%`, background: '#f16361', height: '100%', borderRadius: '0 2px 2px 0' }} />
                </div>
              ) : (
                <div style={{ width: '50%', display: 'flex', justifyContent: 'flex-end' }}>
                  <div style={{ width: `${width}%`, background: '#45c9a3', height: '100%', borderRadius: '2px 0 0 2px' }} />
                </div>
              )}
            </div>
            
            <div style={{ width: '45px', textAlign: 'right', color: isPositive ? '#f16361' : '#45c9a3', fontWeight: 'bold' }}>
              {isPositive ? '+' : ''}{driver.shap_value.toFixed(2)}
            </div>
          </div>
        );
      })}
    </div>
  );
}
