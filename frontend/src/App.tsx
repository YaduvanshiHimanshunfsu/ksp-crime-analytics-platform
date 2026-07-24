import { useState } from "react";
import { useDashboardData } from "./hooks/useDashboardData";
import TopBar from "./components/layout/TopBar";
import ControlBar, { View } from "./components/layout/ControlBar";
import SyntheticNotice from "./components/layout/SyntheticNotice";
import CommandMapView from "./components/command-map/CommandMapView";
import CaseLinkView from "./components/caselink/CaseLinkView";
import ForecastView from "./components/forecast/ForecastView";
import GovernanceView from "./components/governance/GovernanceView";
import ErrorBoundary from "./components/shared/ErrorBoundary";
import LoadingSpinner from "./components/shared/LoadingSpinner";

export default function App() {
  const [district, setDistrict] = useState("All Karnataka");
  const [crimeHead, setCrimeHead] = useState("All crime heads");
  const [view, setView] = useState<View>("Command map");
  
  const { data, drilldown, loading, error } = useDashboardData(district, crimeHead);
  
  if (loading) return <main className="loading"><LoadingSpinner message="Loading KSP Dṛṣṭi…" /></main>;
  if (error) return <main className="error"><div className="error">{error}</div></main>;
  if (!data) return null;

  return (
    <main className="app-shell">
      <TopBar isLive={data.isLive} />
      <SyntheticNotice notice={data.summary.synthetic_notice} isLive={data.isLive} />
      <ControlBar 
        view={view} 
        setView={setView} 
        district={district} 
        setDistrict={setDistrict} 
        crimeHead={crimeHead} 
        setCrimeHead={setCrimeHead} 
      />
      
      <ErrorBoundary key={view}>
        {view === "Command map" && <CommandMapView data={data} district={district} setDistrict={setDistrict} drilldown={drilldown} />}
        {view === "CaseLink" && <CaseLinkView data={data} />}
        {view === "Risk forecast" && <ForecastView data={data} />}
        {view === "Governance" && <GovernanceView data={data} district={district} />}
      </ErrorBoundary>
    </main>
  );
}
