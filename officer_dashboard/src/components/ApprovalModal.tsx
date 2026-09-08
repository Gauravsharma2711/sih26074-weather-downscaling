import React, { useState } from 'react';
import { 
  X, 
  ShieldCheck, 
  AlertTriangle, 
  CloudRain, 
  Mountain, 
  Check, 
  XCircle, 
  FileText
} from 'lucide-react';
import { AdvisoryItem } from '../types';

interface ApprovalModalProps {
  advisory: AdvisoryItem | null;
  onClose: () => void;
  onApprove: (advisoryId: number, comment: string) => Promise<void>;
  onReject: (advisoryId: number, comment: string) => Promise<void>;
}

export const ApprovalModal: React.FC<ApprovalModalProps> = ({
  advisory,
  onClose,
  onApprove,
  onReject,
}) => {
  if (!advisory) return null;

  const [comment, setComment] = useState(advisory.officer_comment || '');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const blockForecastMm = advisory.block_forecast_mm || 18.5;
  const downscaledMm = advisory.rainfall_mm;
  const varianceDelta = (downscaledMm - blockForecastMm).toFixed(1);

  const handleApprove = async () => {
    setIsSubmitting(true);
    try {
      await onApprove(advisory.id, comment);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReject = async () => {
    setIsSubmitting(true);
    try {
      await onReject(advisory.id, comment);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(30, 40, 35, 0.45)',
        backdropFilter: 'blur(3px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 50,
        padding: '20px',
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        style={{
          backgroundColor: 'var(--surface)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-modal)',
          maxWidth: '720px',
          width: '100%',
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          border: '1px solid var(--ink-300)',
        }}
      >
        {/* Modal Header */}
        <div
          style={{
            padding: '20px 24px',
            borderBottom: 'var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            backgroundColor: 'var(--surface-subtle)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--primary-100)',
                color: 'var(--primary-700)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <ShieldCheck size={20} />
            </div>
            <div>
              <h2 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--ink-900)' }}>
                Advisory Inspection & Approval
              </h2>
              <p style={{ fontSize: '12px', color: 'var(--ink-500)' }}>
                {advisory.panchayat_name} Gram Panchayat • Forecast Date: {advisory.forecast_date}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--ink-500)',
              padding: '4px',
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Modal Body */}
        <div style={{ padding: '24px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Comparison Cards: Block Baseline vs ML Downscaled */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div
              style={{
                backgroundColor: 'var(--surface-subtle)',
                padding: '16px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--ink-300)',
              }}
            >
              <div className="text-label">Official IMD Block Forecast</div>
              <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--ink-700)', marginTop: '4px' }}>
                {blockForecastMm} <span style={{ fontSize: '14px' }}>mm</span>
              </div>
              <div style={{ fontSize: '12px', color: 'var(--ink-500)', marginTop: '4px' }}>
                Coarse uniform 25-50km grid
              </div>
            </div>

            <div
              style={{
                backgroundColor: 'var(--primary-050)',
                padding: '16px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--primary-100)',
              }}
            >
              <div className="text-label" style={{ color: 'var(--primary-700)' }}>
                Micro-Downscaled Prediction
              </div>
              <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--primary-700)', marginTop: '4px' }}>
                {downscaledMm} <span style={{ fontSize: '14px' }}>mm</span>
              </div>
              <div style={{ fontSize: '12px', color: 'var(--primary-700)', fontWeight: 600, marginTop: '4px' }}>
                Δ {Number(varianceDelta) >= 0 ? `+${varianceDelta}` : varianceDelta} mm difference from block avg
              </div>
            </div>
          </div>

          {/* Spatial Metadata Pill Bar */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '16px',
              padding: '10px 14px',
              backgroundColor: 'var(--surface-subtle)',
              borderRadius: 'var(--radius-sm)',
              fontSize: '12px',
              color: 'var(--ink-700)',
            }}
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Mountain size={14} color="var(--primary-600)" />
              Elevation: <strong>{advisory.elevation_m || 540} m</strong>
            </span>
            <span>•</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <CloudRain size={14} color="var(--primary-600)" />
              Rainfall Category: <strong>{advisory.rainfall_category}</strong>
            </span>
            <span>•</span>
            <span>Severity: <strong>{advisory.severity}</strong></span>
          </div>

          {/* Generated Advisory Text Preview */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
              <FileText size={16} color="var(--primary-700)" />
              <span style={{ fontSize: '14px', fontWeight: 700, color: 'var(--ink-900)' }}>
                Rule-Based Agricultural Guidance
              </span>
            </div>

            <div
              style={{
                backgroundColor: 'var(--surface-subtle)',
                padding: '16px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--ink-300)',
                display: 'flex',
                flexDirection: 'column',
                gap: '10px',
              }}
            >
              <div style={{ fontSize: '14px', fontWeight: 650, color: 'var(--ink-900)' }}>
                {advisory.advisory_title}
              </div>
              <div style={{ fontSize: '13px', color: 'var(--ink-700)', lineHeight: '20px', whiteSpace: 'pre-line' }}>
                {advisory.advisory_text}
              </div>
            </div>
          </div>

          {/* Officer Comments / Validation Remarks Field */}
          <div>
            <label
              style={{
                display: 'block',
                fontSize: '13px',
                fontWeight: 600,
                color: 'var(--ink-900)',
                marginBottom: '6px',
              }}
            >
              Extension Officer Validation Comments / Custom Advice
            </label>
            <textarea
              rows={3}
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="e.g., Verified against IMD automatic weather station radar trend. Approved for distribution to farmers."
              className="input-field"
              style={{ resize: 'vertical' }}
            />
          </div>

          {/* Verification Safety Notice */}
          <div
            style={{
              padding: '12px 14px',
              backgroundColor: 'var(--warning-100)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid rgba(199, 131, 24, 0.3)',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '10px',
              fontSize: '12px',
              color: 'var(--warning-600)',
            }}
          >
            <AlertTriangle size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
            <span>
              <strong>Operational Guarantee:</strong> Only explicitly approved advisories will be published to the Flutter mobile farmer application. Rejection prevents dissemination of anomalies.
            </span>
          </div>
        </div>

        {/* Modal Footer Actions */}
        <div
          style={{
            padding: '16px 24px',
            borderTop: 'var(--border-subtle)',
            backgroundColor: 'var(--surface-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <button
            onClick={onClose}
            className="btn-secondary"
            disabled={isSubmitting}
            style={{ padding: '8px 16px', fontSize: '13px' }}
          >
            Cancel
          </button>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <button
              onClick={handleReject}
              className="btn-danger"
              disabled={isSubmitting}
              style={{ padding: '8px 18px', fontSize: '13px' }}
            >
              <XCircle size={15} />
              <span>Reject Advisory</span>
            </button>

            <button
              onClick={handleApprove}
              className="btn-primary"
              disabled={isSubmitting}
              style={{ padding: '8px 20px', fontSize: '13px' }}
            >
              <Check size={15} />
              <span>Approve for Farmers</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
