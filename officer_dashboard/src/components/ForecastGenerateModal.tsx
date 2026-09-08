import React, { useState } from 'react';
import { X, Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';
import { PanchayatItem, DownscaledForecastDetail } from '../types';

interface ForecastGenerateModalProps {
  isOpen: boolean;
  onClose: () => void;
  panchayats: PanchayatItem[];
  preselectedPanchayat?: PanchayatItem | null;
  onGenerate: (panchayatId: number, targetDate: string, issueDate: string) => Promise<DownscaledForecastDetail>;
}

export const ForecastGenerateModal: React.FC<ForecastGenerateModalProps> = ({
  isOpen,
  onClose,
  panchayats,
  preselectedPanchayat,
  onGenerate,
}) => {
  if (!isOpen) return null;

  const [selectedPanchayatId, setSelectedPanchayatId] = useState<number>(
    preselectedPanchayat?.panchayat_id || (panchayats[0]?.panchayat_id ?? 1001)
  );
  const [forecastDate, setForecastDate] = useState('2026-09-09');
  const [issueDate, setIssueDate] = useState('2026-09-08');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DownscaledForecastDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen && !loading) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, loading, onClose]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await onGenerate(selectedPanchayatId, forecastDate, issueDate);
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Failed to generate forecast');
    } finally {
      setLoading(false);
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
        zIndex: 60,
        padding: '20px',
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget && !loading) onClose();
      }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="forecast-modal-title"
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
        }}
      >
        {/* Header */}
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
                backgroundColor: 'var(--primary-050)',
                color: 'var(--primary-700)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Sparkles size={20} />
            </div>
            <div>
              <h2 id="forecast-modal-title" style={{ fontSize: '18px', fontWeight: 700, color: 'var(--ink-900)' }}>
                Run ML Weather Downscaling
              </h2>
              <p style={{ fontSize: '12px', color: 'var(--ink-500)' }}>
                Micro-level spatial downscaling from Block to Gram Panchayat
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            disabled={loading}
            aria-label="Close dialog"
            style={{ background: 'none', border: 'none', cursor: loading ? 'not-allowed' : 'pointer', color: 'var(--ink-500)', padding: '4px' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Form or Result View */}
        <div style={{ padding: '24px' }}>
          {!result ? (
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label htmlFor="target-panchayat-select" style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                  Target Gram Panchayat
                </label>
                <select
                  id="target-panchayat-select"
                  value={selectedPanchayatId}
                  onChange={(e) => setSelectedPanchayatId(Number(e.target.value))}
                  className="input-field"
                  disabled={loading}
                >
                  {panchayats.map((p) => (
                    <option key={p.panchayat_id} value={p.panchayat_id}>
                      {p.panchayat_name} ({p.block_name} • Elev: {p.elevation_m}m)
                    </option>
                  ))}
                </select>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label htmlFor="forecast-target-date" style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                    Forecast Target Date
                  </label>
                  <input
                    id="forecast-target-date"
                    type="date"
                    value={forecastDate}
                    onChange={(e) => setForecastDate(e.target.value)}
                    className="input-field"
                    required
                    disabled={loading}
                  />
                </div>
                <div>
                  <label htmlFor="forecast-issue-date" style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>
                    Forecast Issue Date
                  </label>
                  <input
                    id="forecast-issue-date"
                    type="date"
                    value={issueDate}
                    onChange={(e) => setIssueDate(e.target.value)}
                    className="input-field"
                    required
                    disabled={loading}
                  />
                </div>
              </div>

              {error && (
                <div
                  style={{
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'var(--danger-100)',
                    color: 'var(--danger-600)',
                    fontSize: '13px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                  }}
                >
                  <AlertCircle size={16} />
                  <span>{error}</span>
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '8px' }}>
                <button type="button" onClick={onClose} className="btn-secondary" style={{ fontSize: '13px' }}>
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary"
                  style={{ fontSize: '13px' }}
                >
                  <Sparkles size={14} />
                  <span>{loading ? 'Running ML Inference...' : 'Execute Downscaling'}</span>
                </button>
              </div>
            </form>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  color: 'var(--primary-700)',
                  backgroundColor: 'var(--primary-050)',
                  padding: '12px 16px',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--primary-100)',
                }}
              >
                <CheckCircle2 size={20} />
                <span style={{ fontWeight: 600 }}>Downscaled Forecast Generated Successfully!</span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div style={{ backgroundColor: 'var(--surface-subtle)', padding: '14px', borderRadius: 'var(--radius-sm)' }}>
                  <div className="text-label">Block Baseline</div>
                  <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--ink-700)', marginTop: '4px' }}>
                    {result.block_forecast_rainfall_mm} mm
                  </div>
                </div>

                <div style={{ backgroundColor: 'var(--primary-050)', padding: '14px', borderRadius: 'var(--radius-sm)' }}>
                  <div className="text-label" style={{ color: 'var(--primary-700)' }}>Panchayat Downscaled</div>
                  <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--primary-700)', marginTop: '4px' }}>
                    {result.downscaled_rainfall_mm} mm
                  </div>
                </div>
              </div>

              <div style={{ fontSize: '12px', color: 'var(--ink-500)', lineHeight: '18px' }}>
                <div>Model: <strong>{result.model_name} ({result.model_version})</strong></div>
                <div>Target Date: <strong>{result.forecast_date}</strong> (Lead: {result.lead_days} day)</div>
              </div>

              <button
                onClick={() => {
                  setResult(null);
                  onClose();
                }}
                className="btn-primary"
                style={{ width: '100%', marginTop: '8px' }}
              >
                Done & View in Review Queue
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
