import React from 'react';
import { Clock, CheckCircle2, XCircle } from 'lucide-react';

interface StatusBadgeProps {
  status: 'DRAFT' | 'APPROVED' | 'REJECTED' | string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const isSm = size === 'sm';
  const padding = isSm ? '2px 8px' : '4px 12px';
  const fontSize = isSm ? '11px' : '12px';
  const iconSize = isSm ? 12 : 14;

  switch (status.toUpperCase()) {
    case 'APPROVED':
      return (
        <span
          className="status-chip status-chip-approved"
          style={{ padding, fontSize }}
          role="status"
          aria-label="Status: Approved"
        >
          <CheckCircle2 size={iconSize} strokeWidth={2} />
          <span>Approved</span>
        </span>
      );
    case 'REJECTED':
      return (
        <span
          className="status-chip status-chip-rejected"
          style={{ padding, fontSize }}
          role="status"
          aria-label="Status: Rejected"
        >
          <XCircle size={iconSize} strokeWidth={2} />
          <span>Rejected</span>
        </span>
      );
    case 'DRAFT':
    default:
      return (
        <span
          className="status-chip status-chip-draft"
          style={{ padding, fontSize }}
          role="status"
          aria-label="Status: Pending Review"
        >
          <Clock size={iconSize} strokeWidth={2} />
          <span>Pending Review</span>
        </span>
      );
  }
};
