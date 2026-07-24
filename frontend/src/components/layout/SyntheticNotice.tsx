import React from "react";

export default function SyntheticNotice({ notice, isLive }: { notice: string, isLive: boolean }) {
  return (
    <>
      {!isLive && <div className="offline-banner">Live backend disconnected. Showing offline mock data.</div>}
      <section className="notice"><b>Demonstration data only.</b> {notice}</section>
    </>
  );
}
