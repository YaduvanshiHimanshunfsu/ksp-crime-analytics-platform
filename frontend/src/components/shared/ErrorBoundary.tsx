import React, { Component } from "react";

type ErrorBoundaryProps = { children: React.ReactNode; fallback?: React.ReactNode };
type ErrorBoundaryState = { hasError: boolean; error: string };

export default class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: "" };
  }
  
  static getDerivedStateFromError(err: Error) {
    return { hasError: true, error: err.message };
  }
  
  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;
      
      return (
        <main className="error-boundary" style={{ padding: '2rem', color: '#f16361' }}>
          <div className="brand-mark" style={{ marginBottom: '1rem', width: '3rem', height: '3rem', fontSize: '2rem' }}>!</div>
          <h2>Something went wrong</h2>
          <p>{this.state.error}</p>
          <button className="primary" style={{ marginTop: '1rem', width: 'auto' }} onClick={() => window.location.reload()}>Reload dashboard</button>
        </main>
      );
    }
    return this.props.children;
  }
}
