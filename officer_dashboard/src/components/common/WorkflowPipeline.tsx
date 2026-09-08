import React from 'react';
import { 
  Building2, 
  Cpu, 
  CloudRain, 
  FileText, 
  UserCheck, 
  CheckCircle2, 
  ArrowRight 
} from 'lucide-react';

interface WorkflowPipelineProps {
  activeStep?: number;
}

export const WorkflowPipeline: React.FC<WorkflowPipelineProps> = () => {
  const steps = [
    {
      id: 1,
      title: 'Block Forecast',
      subtitle: 'Official IMD 25-50km',
      icon: <Building2 size={16} />,
    },
    {
      id: 2,
      title: 'ML Downscaling',
      subtitle: 'Terrain & Geo Features',
      icon: <Cpu size={16} />,
    },
    {
      id: 3,
      title: 'Panchayat Forecast',
      subtitle: 'Hyper-local 3-8km',
      icon: <CloudRain size={16} />,
    },
    {
      id: 4,
      title: 'Agro-Advisory',
      subtitle: 'Deterministic Rules',
      icon: <FileText size={16} />,
    },
    {
      id: 5,
      title: 'Officer Review',
      subtitle: 'Human-in-the-Loop',
      icon: <UserCheck size={16} />,
    },
    {
      id: 6,
      title: 'Farmer Delivery',
      subtitle: 'Approved Guidance',
      icon: <CheckCircle2 size={16} />,
    },
  ];

  return (
    <div
      className="app-card"
      style={{
        backgroundColor: 'var(--surface)',
        border: '1px solid var(--primary-100)',
        padding: '16px 20px',
      }}
      role="region"
      aria-label="GramSevak Workflow Pipeline"
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
        <span className="text-label" style={{ color: 'var(--primary-700)' }}>
          GramSevak End-to-End Operational Pipeline
        </span>
        <span style={{ fontSize: '11px', color: 'var(--ink-500)', fontWeight: 500 }}>
          MoES / IMD Agromet Protocol
        </span>
      </div>

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          overflowX: 'auto',
          gap: '8px',
          paddingBottom: '4px',
        }}
      >
        {steps.map((step, idx) => (
          <React.Fragment key={step.id}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                minWidth: '140px',
                backgroundColor: 'var(--surface-subtle)',
                padding: '8px 12px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--ink-100)',
              }}
            >
              <div
                style={{
                  width: '30px',
                  height: '30px',
                  borderRadius: 'var(--radius-pill)',
                  backgroundColor: 'var(--primary-050)',
                  color: 'var(--primary-700)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}
              >
                {step.icon}
              </div>
              <div style={{ minWidth: 0 }}>
                <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--ink-900)', whiteSpace: 'nowrap' }}>
                  {step.title}
                </div>
                <div style={{ fontSize: '10px', color: 'var(--ink-500)', whiteSpace: 'nowrap' }}>
                  {step.subtitle}
                </div>
              </div>
            </div>

            {idx < steps.length - 1 && (
              <ArrowRight size={14} color="var(--ink-300)" style={{ flexShrink: 0 }} />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};
