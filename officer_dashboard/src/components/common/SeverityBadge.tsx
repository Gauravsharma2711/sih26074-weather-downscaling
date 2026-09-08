import React from 'react';
import { AlertCircle, AlertTriangle, Info, ShieldAlert } from 'lucide-react';

interface SeverityBadgeProps {
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | string;
  size?: 'sm' | 'md';
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity, size = 'md' }) => {
  const isSm = size === 'sm';
  const padding = isSm ? '2px 8px' : '4px 10px';
  const fontSize = isSm ? '11px' : '12px';
  const iconSize = isSm ? 12 : 14;

  switch (severity.toUpperCase()) {
    case 'CRITICAL':
      return (
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            padding,
            fontSize,
            fontWeight: 700,
            borderRadius: 'var(--radius-pill)',
            backgroundColor: 'var(--danger-100)',
            color: 'var(--danger-600)',
            border: '1px solid rgba(201, 75, 67, 0.4)',
          }}
          role="status"
          aria-label="Severity: Critical"
        >
          <ShieldAlert size={iconSize} />
          <span>Critical</span>
        </span>
      );
    case 'HIGH':
      return (
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            padding,
            fontSize,
            fontWeight: 700,
            borderRadius: 'var(--radius-pill)',
            backgroundColor: 'var(--danger-100)',
            color: 'var(--danger-600)',
            border: '1px solid rgba(201, 75, 67, 0.3)',
          }}
          role="status"
          aria-label="Severity: High"
        >
          <AlertCircle size={iconSize} />
          <span>High Risk</span>
        </span>
      );
    case 'MEDIUM':
      return (
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            padding,
            fontSize,
            fontWeight: 700,
            borderRadius: 'var(--radius-pill)',
            backgroundColor: 'var(--warning-100)',
            color: 'var(--warning-600)',
            border: '1px solid rgba(199, 131, 24, 0.3)',
          }}
          role="status"
          aria-label="Severity: Medium"
        >
          <AlertTriangle size={iconSize} />
          <span>Moderate</span>
        </span>
      );
    case 'LOW':
    default:
      return (
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            padding,
            fontSize,
            fontWeight: 700,
            borderRadius: 'var(--radius-pill)',
            backgroundColor: 'var(--primary-100)',
            color: 'var(--primary-700)',
            border: '1px solid rgba(5, 107, 67, 0.3)',
          }}
          role="status"
          aria-label="Severity: Low"
        >
          <Info size={iconSize} />
          <span>Routine / Low</span>
        </span>
      );
  }
};
