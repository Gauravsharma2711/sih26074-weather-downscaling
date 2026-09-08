import React, { useState } from 'react';
import { 
  Search, 
  ArrowUpDown, 
  Mountain, 
  ExternalLink, 
  Sparkles,
  Calendar
} from 'lucide-react';
import { AdvisoryItem, PanchayatItem } from '../types';
import { StatusBadge } from './common/StatusBadge';
import { ForecastValue } from './common/ForecastValue';
import { EmptyState } from './common/EmptyState';

interface PanchayatForecastSectionProps {
  panchayats: PanchayatItem[];
  advisories: AdvisoryItem[];
  onReviewAdvisory: (advisory: AdvisoryItem) => void;
  onGenerateForecast: (panchayat: PanchayatItem) => void;
}

export const PanchayatForecastSection: React.FC<PanchayatForecastSectionProps> = ({
  panchayats,
  advisories,
  onReviewAdvisory,
  onGenerateForecast,
}) => {
  const [search, setSearch] = useState('');
  const [selectedBlock, setSelectedBlock] = useState('ALL');
  const [sortBy, setSortBy] = useState<'name' | 'rainfall' | 'difference'>('rainfall');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const blockForecastMm = 18.5; // Official IMD Block Forecast for Baglan

  // Merge Panchayat spatial data with latest advisory/forecast record
  const rows = panchayats.map((p) => {
    const adv = advisories.find((a) => a.panchayat_id === p.panchayat_id);
    const downscaledMm = adv?.rainfall_mm ?? 18.5;
    const diff = downscaledMm - blockForecastMm;
    const advisoryStatus = adv?.status ?? 'DRAFT';
    const forecastDate = adv?.forecast_date ?? '2026-09-09';

    return {
      panchayat: p,
      advisory: adv,
      blockForecastMm,
      downscaledMm,
      diff,
      advisoryStatus,
      forecastDate,
    };
  });

  const filteredRows = rows.filter((r) => {
    const matchesSearch =
      r.panchayat.panchayat_name.toLowerCase().includes(search.toLowerCase()) ||
      r.panchayat.block_name.toLowerCase().includes(search.toLowerCase()) ||
      String(r.panchayat.panchayat_id).includes(search);
    const matchesBlock = selectedBlock === 'ALL' || r.panchayat.block_name.toLowerCase() === selectedBlock.toLowerCase();
    return matchesSearch && matchesBlock;
  });

  filteredRows.sort((a, b) => {
    let comp = 0;
    if (sortBy === 'name') comp = a.panchayat.panchayat_name.localeCompare(b.panchayat.panchayat_name);
    if (sortBy === 'rainfall') comp = a.downscaledMm - b.downscaledMm;
    if (sortBy === 'difference') comp = Math.abs(a.diff) - Math.abs(b.diff);
    return sortOrder === 'desc' ? -comp : comp;
  });

  const toggleSort = (field: 'name' | 'rainfall' | 'difference') => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Section Title & Description */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 className="text-section-title">Panchayat Micro-Forecast Downscaling Matrix</h2>
          <p className="text-body" style={{ fontSize: '13px', color: 'var(--ink-500)' }}>
            Comparing uniform IMD Block forecast with ML-downscaled Gram Panchayat predictions.
          </p>
        </div>

        {/* Controls: Search, Filter, Sort */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <div style={{ position: 'relative', width: '240px' }}>
            <Search
              size={15}
              style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--ink-500)' }}
            />
            <input
              type="text"
              placeholder="Search Panchayat..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input-field"
              style={{ paddingLeft: '34px', fontSize: '13px' }}
              aria-label="Search Panchayat records"
            />
          </div>

          <select
            value={selectedBlock}
            onChange={(e) => setSelectedBlock(e.target.value)}
            className="input-field"
            style={{ width: '140px', fontSize: '13px' }}
            aria-label="Filter by block"
          >
            <option value="ALL">All Blocks</option>
            <option value="Baglan">Baglan</option>
            <option value="Dindori">Dindori</option>
            <option value="Surgana">Surgana</option>
          </select>
        </div>
      </div>

      {/* Main Table / List Component */}
      {filteredRows.length === 0 ? (
        <EmptyState
          title="No Matching Panchayat Forecasts Found"
          description="No Gram Panchayats match your current search query or block filter."
          actionText="Clear Filters"
          onAction={() => {
            setSearch('');
            setSelectedBlock('ALL');
          }}
        />
      ) : (
        <div className="app-card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ overflowX: 'auto' }}>
            <table
              style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}
              aria-label="Panchayat micro-forecast downscaling comparison matrix"
            >
              <caption className="sr-only">
                Panchayat micro-forecast downscaling matrix comparing IMD block baseline forecasts with GramSevak downscaled predictions.
              </caption>
              <thead>
                <tr style={{ backgroundColor: 'var(--surface-subtle)', borderBottom: '1px solid var(--ink-300)' }}>
                  <th
                    scope="col"
                    aria-sort={sortBy === 'name' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'}
                    style={{ padding: '14px 18px', fontWeight: 650, color: 'var(--ink-700)' }}
                  >
                    <button
                      type="button"
                      onClick={() => toggleSort('name')}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        cursor: 'pointer',
                        font: 'inherit',
                        color: 'inherit',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: 0,
                      }}
                      aria-label={`Sort by Gram Panchayat name, currently ${sortBy === 'name' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'unsorted'}`}
                    >
                      <span>Gram Panchayat</span>
                      <ArrowUpDown size={13} color="var(--ink-500)" />
                    </button>
                  </th>
                  <th scope="col" style={{ padding: '14px 18px', fontWeight: 650, color: 'var(--ink-700)' }}>
                    Block
                  </th>
                  <th scope="col" style={{ padding: '14px 18px', fontWeight: 650, color: 'var(--ink-700)' }}>
                    Block Forecast
                  </th>
                  <th
                    scope="col"
                    aria-sort={sortBy === 'rainfall' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'}
                    style={{ padding: '14px 18px', fontWeight: 650, color: 'var(--ink-700)' }}
                  >
                    <button
                      type="button"
                      onClick={() => toggleSort('rainfall')}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        cursor: 'pointer',
                        font: 'inherit',
                        color: 'inherit',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: 0,
                      }}
                      aria-label={`Sort by downscaled rainfall amount, currently ${sortBy === 'rainfall' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'unsorted'}`}
                    >
                      <span>Downscaled Rainfall</span>
                      <ArrowUpDown size={13} color="var(--ink-500)" />
                    </button>
                  </th>
                  <th
                    scope="col"
                    aria-sort={sortBy === 'difference' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'}
                    style={{ padding: '14px 18px', fontWeight: 650, color: 'var(--ink-700)' }}
                  >
                    <button
                      type="button"
                      onClick={() => toggleSort('difference')}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        cursor: 'pointer',
                        font: 'inherit',
                        color: 'inherit',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: 0,
                      }}
                      aria-label={`Sort by rainfall difference, currently ${sortBy === 'difference' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'unsorted'}`}
                    >
                      <span>Difference (Δ)</span>
                      <ArrowUpDown size={13} color="var(--ink-500)" />
                    </button>
                  </th>
                  <th scope="col" style={{ padding: '14px 18px', fontWeight: 650, color: 'var(--ink-700)' }}>
                    Target Date
                  </th>
                  <th scope="col" style={{ padding: '14px 18px', fontWeight: 650, color: 'var(--ink-700)' }}>
                    Advisory Status
                  </th>
                  <th scope="col" style={{ padding: '14px 18px', fontWeight: 650, color: 'var(--ink-700)', textAlign: 'right' }}>
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredRows.map((row) => (
                  <tr
                    key={row.panchayat.panchayat_id}
                    style={{ borderBottom: '1px solid var(--border-subtle)', transition: 'background-color 0.15s ease' }}
                    className="table-row-hover"
                  >
                    {/* Panchayat Name with Elevation */}
                    <td style={{ padding: '14px 18px' }}>
                      <div style={{ fontWeight: 700, color: 'var(--ink-900)' }}>
                        {row.panchayat.panchayat_name}
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: 'var(--ink-500)', marginTop: '2px' }}>
                        <Mountain size={12} color="var(--primary-600)" aria-hidden="true" />
                        <span>{row.panchayat.elevation_m}m elevation</span>
                      </div>
                    </td>

                    {/* Block */}
                    <td style={{ padding: '14px 18px', color: 'var(--ink-700)' }}>
                      {row.panchayat.block_name}
                    </td>

                    {/* Block Forecast Rainfall */}
                    <td style={{ padding: '14px 18px' }}>
                      <span style={{ fontWeight: 600, color: 'var(--ink-700)' }}>
                        {row.blockForecastMm.toFixed(1)} mm
                      </span>
                    </td>

                    {/* Downscaled Rainfall */}
                    <td style={{ padding: '14px 18px' }}>
                      <ForecastValue rainfallMm={row.downscaledMm} size="md" />
                    </td>

                    {/* Difference (Delta) */}
                    <td style={{ padding: '14px 18px' }}>
                      <span
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '2px',
                          fontWeight: 700,
                          fontSize: '12px',
                          padding: '2px 8px',
                          borderRadius: 'var(--radius-pill)',
                          backgroundColor:
                            Math.abs(row.diff) > 10
                              ? 'var(--danger-100)'
                              : Math.abs(row.diff) > 4
                              ? 'var(--warning-100)'
                              : 'var(--primary-100)',
                          color:
                            Math.abs(row.diff) > 10
                              ? 'var(--danger-600)'
                              : Math.abs(row.diff) > 4
                              ? 'var(--warning-600)'
                              : 'var(--primary-700)',
                        }}
                      >
                        {row.diff >= 0 ? `+${row.diff.toFixed(1)}` : row.diff.toFixed(1)} mm
                      </span>
                    </td>

                    {/* Forecast Date */}
                    <td style={{ padding: '14px 18px', color: 'var(--ink-700)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Calendar size={13} color="var(--ink-500)" aria-hidden="true" />
                        <span>{row.forecastDate}</span>
                      </div>
                    </td>

                    {/* Advisory Status */}
                    <td style={{ padding: '14px 18px' }}>
                      <StatusBadge status={row.advisoryStatus} size="sm" />
                    </td>

                    {/* Actions */}
                    <td style={{ padding: '14px 18px', textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                        {row.advisory ? (
                          <button
                            type="button"
                            onClick={() => onReviewAdvisory(row.advisory!)}
                            className={row.advisoryStatus === 'DRAFT' ? 'btn-primary' : 'btn-secondary'}
                            style={{ padding: '6px 12px', fontSize: '12px' }}
                            aria-label={`${row.advisoryStatus === 'DRAFT' ? 'Review & approve' : 'Inspect'} advisory for ${row.panchayat.panchayat_name}`}
                          >
                            <ExternalLink size={13} aria-hidden="true" />
                            <span>{row.advisoryStatus === 'DRAFT' ? 'Review & Approve' : 'Inspect'}</span>
                          </button>
                        ) : (
                          <button
                            type="button"
                            onClick={() => onGenerateForecast(row.panchayat)}
                            className="btn-primary"
                            style={{ padding: '6px 12px', fontSize: '12px' }}
                            aria-label={`Generate ML downscaled forecast for ${row.panchayat.panchayat_name}`}
                          >
                            <Sparkles size={13} aria-hidden="true" />
                            <span>Generate ML</span>
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
