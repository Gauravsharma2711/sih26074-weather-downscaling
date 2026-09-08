import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Data Retrieval Error',
  message,
  onRetry,
}) => {
  return (
    <div
      className="app-card"
      style={{
        border: '1px solid rgba(201, 75, 67, 0.3)',
        backgroundColor: 'var(--danger-100)',
        padding: '24px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
      }}
      role="alert"
    >
      <div
        style={{
          width: '48px',
          height: '48px',
          borderRadius: 'var(--radius-pill)',
          backgroundColor: '#F8D5D2',
          color: 'var(--danger-600)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '12px',
        }}
      >
        <AlertCircle size={24} />
      </div>

      <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--danger-600)', marginBottom: '4px' }}>
        {title}
      </h3>

      <p style={{ fontSize: '13px', color: 'var(--ink-700)', maxWidth: '460px', lineHeight: '20px', marginBottom: onRetry ? '16px' : '0' }}>
        {message}
      </p>

      {onRetry && (
        <button
          onClick={onRetry}
          className="btn-secondary"
          style={{
            borderColor: 'var(--danger-600)',
            color: 'var(--danger-600)',
            backgroundColor: 'var(--surface)',
            fontSize: '13px',
          }}
        >
          <RefreshCw size={14} />
          <span>Retry Connection</span>
        </button>
      )}
    </div>
  );
};
