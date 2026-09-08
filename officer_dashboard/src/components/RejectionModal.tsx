import React, { useState } from 'react';
import { 
  X, 
  AlertTriangle, 
  AlertCircle, 
  Calendar, 
  CloudRain, 
  MapPin, 
  Loader2,
  XCircle
} from 'lucide-react';
import { AdvisoryItem } from '../types';

interface RejectionModalProps {
  advisory: AdvisoryItem | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirmReject: (advisoryId: number, reason: string) => Promise<void>;
}

const PRESET_REJECTION_REASONS = [
  'Micro-climate downscaled forecast anomaly detected',
  'Ground IMD AWS radar trend contradicts rainfall estimate',
  'Terrain slope elevation requires manual recalibration',
  'Agronomic rule recommendation mismatch with local crop phenology',
  'Significant lead-time shift in convective cloud cover',
];

export const RejectionModal: React.FC<RejectionModalProps> = ({
  advisory,
  isOpen,
  onClose,
  onConfirmReject,
}) => {
  if (!isOpen || !advisory) return null;

  const [reason, setReason] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen && !isSubmitting) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, isSubmitting, onClose]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reason.trim()) {
      setValidationError('A specific rejection reason is required for the audit trail.');
      return;
    }
    setValidationError(null);
    setApiError(null);
    setIsSubmitting(true);
    try {
      await onConfirmReject(advisory.id, reason.trim());
      onClose();
    } catch (err: any) {
      setApiError(err.message || 'Failed to reject advisory. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSelectPreset = (preset: string) => {
    setReason(preset);
    setValidationError(null);
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(30, 40, 35, 0.55)',
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 60,
        padding: '20px',
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget && !isSubmitting) onClose();
      }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="rejection-modal-title"
    >
      <div
        style={{
          backgroundColor: 'var(--surface)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-modal)',
          maxWidth: '560px',
          width: '100%',
          overflow: 'hidden',
          border: '1px solid var(--danger-300)',
          animation: 'fadeIn 0.2s ease',
        }}
      >
        {/* Modal Header */}
        <div
          style={{
            padding: '18px 24px',
            backgroundColor: 'var(--danger-100)',
            borderBottom: '1px solid var(--danger-300)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'rgba(217, 45, 32, 0.15)',
                color: 'var(--danger-600)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <AlertTriangle size={20} />
            </div>
            <div>
              <h2
                id="rejection-modal-title"
                style={{ fontSize: '17px', fontWeight: 700, color: 'var(--danger-600)' }}
              >
                Reject Agricultural Advisory
              </h2>
              <p style={{ fontSize: '12px', color: 'var(--ink-700)', fontWeight: 500 }}>
                Discard draft from farmer delivery and record reason
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            disabled={isSubmitting}
            style={{
              background: 'none',
              border: 'none',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              color: 'var(--ink-500)',
              padding: '4px',
            }}
            aria-label="Close dialog"
          >
            <X size={20} />
          </button>
        </div>

        {/* Modal Form */}
        <form onSubmit={handleSubmit}>
          <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '18px' }}>
            {/* API Error Alert */}
            {apiError && (
              <div
                style={{
                  padding: '12px 14px',
                  backgroundColor: 'var(--danger-100)',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--danger-300)',
                  color: 'var(--danger-600)',
                  fontSize: '13px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <AlertCircle size={16} style={{ flexShrink: 0 }} />
                <span>{apiError}</span>
              </div>
            )}

            {/* Target Advisory Summary Card */}
            <div
              style={{
                backgroundColor: 'var(--surface-subtle)',
                padding: '14px 16px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--ink-300)',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '14px', fontWeight: 700, color: 'var(--ink-900)' }}>
                  <MapPin size={15} color="var(--primary-700)" />
                  <span>{advisory.panchayat_name} Gram Panchayat</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', color: 'var(--ink-500)' }}>
                  <Calendar size={13} />
                  <span>{advisory.forecast_date}</span>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '12px', color: 'var(--ink-700)' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <CloudRain size={13} color="var(--primary-700)" />
                  Downscaled: <strong>{advisory.rainfall_mm} mm</strong> ({advisory.rainfall_category})
                </span>
                <span>•</span>
                <span>Severity: <strong>{advisory.severity}</strong></span>
              </div>
            </div>

            {/* Preset Rejection Reason Chips */}
            <div>
              <label
                style={{
                  display: 'block',
                  fontSize: '12px',
                  fontWeight: 600,
                  color: 'var(--ink-700)',
                  marginBottom: '8px',
                }}
              >
                Quick Select Common Reasons:
              </label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {PRESET_REJECTION_REASONS.map((preset, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSelectPreset(preset)}
                    disabled={isSubmitting}
                    style={{
                      fontSize: '11px',
                      padding: '4px 10px',
                      borderRadius: 'var(--radius-pill)',
                      border: reason === preset ? '1px solid var(--danger-600)' : '1px solid var(--ink-300)',
                      backgroundColor: reason === preset ? 'var(--danger-100)' : 'var(--surface)',
                      color: reason === preset ? 'var(--danger-600)' : 'var(--ink-700)',
                      fontWeight: reason === preset ? 600 : 400,
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    {preset}
                  </button>
                ))}
              </div>
            </div>

            {/* Rejection Reason Textarea */}
            <div>
              <label
                htmlFor="rejection-reason"
                style={{
                  display: 'block',
                  fontSize: '13px',
                  fontWeight: 600,
                  color: 'var(--ink-900)',
                  marginBottom: '6px',
                }}
              >
                Rejection Reason / Officer Remarks <span style={{ color: 'var(--danger-600)' }}>*</span>
              </label>
              <textarea
                id="rejection-reason"
                rows={3}
                value={reason}
                onChange={(e) => {
                  setReason(e.target.value);
                  if (e.target.value.trim()) setValidationError(null);
                }}
                placeholder="Explain why this forecast/advisory is rejected (e.g., radar cloud shift, sensor variance)..."
                className="input-field"
                style={{
                  resize: 'vertical',
                  fontSize: '13px',
                  borderColor: validationError ? 'var(--danger-600)' : undefined,
                }}
                disabled={isSubmitting}
              />
              {validationError && (
                <span style={{ fontSize: '12px', color: 'var(--danger-600)', marginTop: '4px', display: 'block', fontWeight: 500 }}>
                  {validationError}
                </span>
              )}
            </div>

            {/* Audit & Workflow Notice */}
            <div
              style={{
                padding: '10px 14px',
                backgroundColor: 'var(--surface-subtle)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--ink-300)',
                fontSize: '12px',
                color: 'var(--ink-700)',
                lineHeight: '18px',
              }}
            >
              <strong>Audit Safety:</strong> Rejecting moves this advisory to the <code>REJECTED</code> state. It will not be visible on farmer devices. A new downscaling run must be triggered to produce an updated forecast.
            </div>
          </div>

          {/* Modal Actions */}
          <div
            style={{
              padding: '16px 24px',
              borderTop: 'var(--border-subtle)',
              backgroundColor: 'var(--surface-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-end',
              gap: '12px',
            }}
          >
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="btn-secondary"
              style={{ padding: '8px 16px', fontSize: '13px' }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="btn-danger"
              style={{ padding: '8px 20px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              {isSubmitting ? (
                <>
                  <Loader2 size={15} className="spin" />
                  <span>Rejecting...</span>
                </>
              ) : (
                <>
                  <XCircle size={15} />
                  <span>Confirm Rejection</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
