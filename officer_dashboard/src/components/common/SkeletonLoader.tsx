import React from 'react';

interface SkeletonLoaderProps {
  type?: 'card' | 'table' | 'hero' | 'metric';
  count?: number;
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({ type = 'card', count = 3 }) => {
  if (type === 'metric') {
    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px' }}>
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="app-card" style={{ height: '120px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div className="skeleton" style={{ height: '14px', width: '40%' }} />
            <div className="skeleton" style={{ height: '36px', width: '60%' }} />
            <div className="skeleton" style={{ height: '12px', width: '80%' }} />
          </div>
        ))}
      </div>
    );
  }

  if (type === 'table') {
    return (
      <div className="app-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
        <div className="skeleton" style={{ height: '24px', width: '30%' }} />
        {Array.from({ length: count }).map((_, i) => (
          <div key={i} className="skeleton" style={{ height: '48px', width: '100%' }} />
        ))}
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="app-card" style={{ height: '140px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <div className="skeleton" style={{ height: '18px', width: '35%' }} />
            <div className="skeleton" style={{ height: '18px', width: '15%', borderRadius: '999px' }} />
          </div>
          <div className="skeleton" style={{ height: '40px', width: '100%' }} />
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <div className="skeleton" style={{ height: '14px', width: '45%' }} />
            <div className="skeleton" style={{ height: '28px', width: '20%', borderRadius: '999px' }} />
          </div>
        </div>
      ))}
    </div>
  );
};
