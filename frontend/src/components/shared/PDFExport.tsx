import React, { useState } from "react";
// @ts-ignore
import html2pdf from "html2pdf.js";

export default function PDFExport({ targetId, filename }: { targetId: string; filename: string }) {
  const [generating, setGenerating] = useState(false);

  const handleDownload = () => {
    const element = document.getElementById(targetId);
    if (!element) return;

    setGenerating(true);
    
    // Temporarily adjust styling for PDF rendering
    const originalBg = element.style.background;
    element.style.background = "#0d1117";
    element.style.padding = "20px";
    
    const opt = {
      margin: 10,
      filename: filename,
      image: { type: 'jpeg' as const, quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true, logging: false },
      jsPDF: { unit: 'mm' as const, format: 'a4' as const, orientation: 'landscape' as const }
    };

    html2pdf().set(opt).from(element).save().then(() => {
      element.style.background = originalBg;
      element.style.padding = "";
      setGenerating(false);
    });
  };

  return (
    <button 
      className="primary" 
      onClick={handleDownload}
      disabled={generating}
      style={{ padding: '6px 12px', background: 'transparent', border: '1px solid #165688', color: '#165688' }}
    >
      {generating ? 'Generating...' : 'Export PDF Brief'}
    </button>
  );
}
