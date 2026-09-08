import React, { useState } from 'react';
import { 
  X, 
  CheckCircle2, 
  AlertCircle, 
  Calendar, 
  CloudRain, 
  MapPin, 
  Loader2,
  Check
} from 'lucide-react';
import { AdvisoryItem } from '../types';

interface ApprovalConfirmModalProps {
  advisory: AdvisoryItem | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirmApprove: (advisoryId: number, comment: string) => Promise<void>;
}

export const ApprovalConfirmModal: React.FC<ApprovalConfirmModalProps> = ({
  advisory,
  isOpen,
  onClose,
  onConfirmApprove,
}) => {
  if (!isOpen || !advisory) return null;

  const [comment, setComment] = useState('Verified against IMD AWS station reading. Approved for farmer distribution.');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

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
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      await onConfirmApprove(advisory.id, comment);
      onClose();
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to approve advisory. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
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
      aria-labelledby="approval-modal-title"
    >
      <div
        style={{
          backgroundColor: 'var(--surface)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-modal)',
          maxWidth: '560px',
          width: '100%',
          overflow: 'hidden',
          border: '1px solid var(--ink-300)',
          animation: 'fadeIn 0.2s ease',
        }}
      >
        {/* Modal Header */}
        <div
          style={{
            padding: '18px 24px',
            backgroundColor: 'var(--primary-050)',
            borderBottom: '1px solid var(--primary-100)',
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
                backgroundColor: 'var(--primary-100)',
                color: 'var(--primary-700)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <CheckCircle2 size={20} />
            </div>
            <div>
              <h2
                id="approval-modal-title"
                style={{ fontSize: '17px', fontWeight: 700, color: 'var(--ink-900)' }}
              >
                Confirm Advisory Approval
              </h2>
              <p style={{ fontSize: '12px', color: 'var(--primary-700)', fontWeight: 500 }}>
                Release validated advisory to Farmer Mobile App
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
            {/* Error Message Alert */}
            {errorMessage && (
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
                <span>{errorMessage}</span>
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
                <span>Block: <strong>{advisory.block_name || 'Baglan'}</strong></span>
              </div>

              <div style={{ fontSize: '12px', color: 'var(--ink-700)', fontWeight: 600, marginTop: '4px' }}>
                "{advisory.advisory_title}"
              </div>
            </div>

            {/* Officer Remarks Field */}
            <div>
              <label
                htmlFor="approval-comment"
                style={{
                  display: 'block',
                  fontSize: '13px',
                  fontWeight: 600,
                  color: 'var(--ink-900)',
                  marginBottom: '6px',
                }}
              >
                Extension Officer Approval Remarks (Optional)
              </label>
              <textarea
                id="approval-comment"
                rows={3}
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Enter validation remarks or confirmation notes..."
                className="input-field"
                style={{ resize: 'vertical', fontSize: '13px' }}
                disabled={isSubmitting}
              />
              <span style={{ fontSize: '11px', color: 'var(--ink-500)', marginTop: '4px', display: 'block' }}>
                Recorded in audit trail alongside reviewing officer identifier (DR-S-PATIL-AO).
              </span>
            </div>

            {/* Operational Impact Notice */}
            <div
              style={{
                padding: '10px 14px',
                backgroundColor: 'var(--primary-050)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--primary-100)',
                fontSize: '12px',
                color: 'var(--primary-700)',
                lineHeight: '18px',
              }}
            >
              <strong>Live Dissemination:</strong> Upon approval, this advisory is immediately published to the farmer mobile app in English, Marathi, and Hindi. Silent modifications are prohibited after approval.
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
              className="btn-primary"
              style={{ padding: '8px 20px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              {isSubmitting ? (
                <>
                  <Loader2 size={15} className="spin" />
                  <span>Approving...</span>
                </>
              ) : (
                <>
                  <Check size={15} />
                  <span>Confirm Approval</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
