import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import MetricCard from '../components/command-map/MetricCard';

describe('MetricCard', () => {
  it('renders label, value and note correctly', () => {
    render(<MetricCard label="Total Reports" value="12,345" note="Since yesterday" />);
    
    expect(screen.getByText('Total Reports')).toBeInTheDocument();
    expect(screen.getByText('12,345')).toBeInTheDocument();
    expect(screen.getByText('Since yesterday')).toBeInTheDocument();
  });

  it('applies the attention tone class when specified', () => {
    const { container } = render(<MetricCard label="Alerts" value="5" note="New" tone="attention" />);
    
    expect(container.firstChild).toHaveClass('metric-card');
    expect(container.firstChild).toHaveClass('attention');
  });
});
