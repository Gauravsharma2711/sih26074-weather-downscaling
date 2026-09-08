import React from 'react';
import { CheckCircle2, XCircle, Calendar, UserCheck } from 'lucide-react';
import { AdvisoryItem } from '../types';

interface AuditLogViewProps {
  advisories: AdvisoryItem[];
}

export const AuditLogView: React.FC<AuditLogViewProps> = ({ advisories }) => {
  const auditedItems = advisories.filter((a) => a.officer_id || a.status !== 'DRAFT');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h2 className="text-section-title">Historical Approval Audit Trail</h2>
        <p className="text-body" style={{ fontSize: '13px', color: 'var(--ink-500)' }}>
          Immutable log of all advisory reviews, extension officer signatures, and dissemination decisions.
        </p>
      </div>

      <div className="app-card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto', width: '100%' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
            <caption className="sr-only">
              Historical approval audit trail showing reviewed advisories, reviewing officers, and dissemination decisions.
            </caption>
            <thead>
              <tr style={{ backgroundColor: 'var(--surface-subtle)', borderBottom: '1px solid var(--ink-300)' }}>
                <th scope="col" style={{ padding: '14px 18px', fontWeight: 650, color: 'var(--ink-700)' }}>Panchayat</th>
                <th scope="col" style={{ padding: '14px 18px', fontWeight: 650, color: 'var(--ink-700)' }}>Forecast Date</th>
                <th scope="col" style={{ padding: '14px 18px', fontWeight: 650, color: 'var(--ink-700)' }}>Rainfall</th>
                <th scope="col" style={{ padding: '14px 18px', fontWeight: 650, color: 'var(--ink-700)' }}>Status</th>
                <th scope="col" style={{ padding: '14px 18px', fontWeight: 650, color: 'var(--ink-700)' }}>Reviewed By</th>
                <th scope="col" style={{ padding: '14px 18px', fontWeight: 650, color: 'var(--ink-700)' }}>Officer Remarks</th>
                <th scope="col" style={{ padding: '14px 18px', fontWeight: 650, color: 'var(--ink-700)' }}>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {auditedItems.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ padding: '32px', textAlign: 'center', color: 'var(--ink-500)' }}>
                    No historical audit logs recorded yet.
                  </td>
                </tr>
              ) : (
              auditedItems.map((item) => (
                <tr
                  key={item.id}
                  style={{
                    borderBottom: '1px solid var(--border-subtle)',
                    transition: 'background-color 0.15s ease',
                  }}
                >
                  <td style={{ padding: '14px 18px', fontWeight: 600, color: 'var(--ink-900)' }}>
                    {item.panchayat_name || `Panchayat ${item.panchayat_id}`}
                  </td>
                  <td style={{ padding: '14px 18px', color: 'var(--ink-700)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Calendar size={13} color="var(--ink-500)" />
                      <span>{item.forecast_date}</span>
                    </div>
                  </td>
                  <td style={{ padding: '14px 18px', fontWeight: 600 }}>
                    {item.rainfall_mm} mm
                  </td>
                  <td style={{ padding: '14px 18px' }}>
                    {item.status === 'APPROVED' ? (
                      <span className="status-chip status-chip-approved" style={{ fontSize: '11px', padding: '2px 8px' }}>
                        <CheckCircle2 size={12} /> Approved
                      </span>
                    ) : item.status === 'REJECTED' ? (
                      <span className="status-chip status-chip-rejected" style={{ fontSize: '11px', padding: '2px 8px' }}>
                        <XCircle size={12} /> Rejected
                      </span>
                    ) : (
                      <span className="status-chip status-chip-draft" style={{ fontSize: '11px', padding: '2px 8px' }}>
                        Draft
                      </span>
                    )}
                  </td>
                  <td style={{ padding: '14px 18px', color: 'var(--ink-900)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <UserCheck size={14} color="var(--primary-600)" />
                      <span>{item.officer_id || 'System / Auto'}</span>
                    </div>
                  </td>
                  <td style={{ padding: '14px 18px', color: 'var(--ink-700)', maxWidth: '240px' }}>
                    <span style={{ fontSize: '12px', fontStyle: item.officer_comment ? 'normal' : 'italic' }}>
                      {item.officer_comment || 'No additional remarks.'}
                    </span>
                  </td>
                  <td style={{ padding: '14px 18px', color: 'var(--ink-500)', fontSize: '12px' }}>
                    {item.approved_at ? new Date(item.approved_at).toLocaleString() : '—'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
        </div>
      </div>
    </div>
  );
};
