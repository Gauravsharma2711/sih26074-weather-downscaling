import React, { useState } from 'react';
import { 
  LayoutDashboard, 
  FileCheck2, 
  CloudRain, 
  Building2, 
  History, 
  Sparkles, 
  ShieldCheck, 
  RefreshCw,
  MapPin,
  Menu,
  X,
  Compass
} from 'lucide-react';
import { DemoPanchayatSelector } from './DemoPanchayatSelector';
import { PanchayatItem } from '../types';

interface AppShellProps {
  currentTab: 'dashboard' | 'forecasts' | 'review' | 'audit' | 'panchayats';
  onSelectTab: (tab: 'dashboard' | 'forecasts' | 'review' | 'audit' | 'panchayats') => void;
  pendingCount: number;
  onOpenGenerateModal: () => void;
  onRefresh: () => void;
  isRefreshing: boolean;
  forecastDate: string;
  onSelectDemoPanchayat?: (panchayat: PanchayatItem) => void;
  selectedDemoPanchayatId?: number | null;
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({
  currentTab,
  onSelectTab,
  pendingCount,
  onOpenGenerateModal,
  onRefresh,
  isRefreshing,
  forecastDate,
  onSelectDemoPanchayat,
  selectedDemoPanchayatId,
  children,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleNavClick = (tab: 'dashboard' | 'forecasts' | 'review' | 'audit' | 'panchayats') => {
    onSelectTab(tab);
    setMobileMenuOpen(false);
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', position: 'relative' }}>
      {/* Left Navigation Sidebar (Desktop & Tablet) */}
      <aside
        style={{
          width: '260px',
          backgroundColor: 'var(--surface)',
          borderRight: 'var(--border-subtle)',
          display: 'flex',
          flexDirection: 'column',
          position: 'sticky',
          top: 0,
          height: '100vh',
          zIndex: 30,
        }}
        aria-label="Officer Portal Sidebar Navigation"
      >
        {/* Brand Header */}
        <div
          style={{
            padding: '24px 20px',
            borderBottom: 'var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
          }}
        >
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--primary-050)',
              border: '1px solid var(--primary-100)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--primary-700)',
            }}
          >
            <CloudRain size={22} strokeWidth={2.2} />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '18px', color: 'var(--primary-700)', lineHeight: '22px' }}>
              GramSevak
            </div>
            <div style={{ fontSize: '11px', color: 'var(--ink-500)', fontWeight: 500 }}>
              Officer Agro-Advisory Portal
            </div>
          </div>
        </div>

        {/* Region Scope Jurisdiction Card */}
        <div style={{ padding: '16px 20px 8px 20px' }}>
          <div
            style={{
              backgroundColor: 'var(--surface-subtle)',
              border: '1px solid var(--ink-100)',
              borderRadius: 'var(--radius-sm)',
              padding: '10px 12px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
            }}
          >
            <MapPin size={16} color="var(--primary-600)" />
            <div>
              <div style={{ fontSize: '10px', color: 'var(--ink-500)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
                Pilot Jurisdiction
              </div>
              <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--ink-900)' }}>
                Nashik • Baglan Block
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Items */}
        <nav style={{ flex: 1, padding: '12px 12px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <button
            onClick={() => handleNavClick('dashboard')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '12px 14px',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              backgroundColor: currentTab === 'dashboard' ? 'var(--primary-050)' : 'transparent',
              color: currentTab === 'dashboard' ? 'var(--primary-700)' : 'var(--ink-700)',
              fontWeight: currentTab === 'dashboard' ? 700 : 500,
              fontSize: '14px',
              cursor: 'pointer',
              textAlign: 'left',
              width: '100%',
              transition: 'all 0.15s ease',
            }}
            aria-current={currentTab === 'dashboard' ? 'page' : undefined}
          >
            <LayoutDashboard size={18} strokeWidth={currentTab === 'dashboard' ? 2.2 : 1.75} />
            <span>Dashboard Overview</span>
          </button>

          <button
            onClick={() => handleNavClick('forecasts')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '12px 14px',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              backgroundColor: currentTab === 'forecasts' ? 'var(--primary-050)' : 'transparent',
              color: currentTab === 'forecasts' ? 'var(--primary-700)' : 'var(--ink-700)',
              fontWeight: currentTab === 'forecasts' ? 700 : 500,
              fontSize: '14px',
              cursor: 'pointer',
              textAlign: 'left',
              width: '100%',
              transition: 'all 0.15s ease',
            }}
            aria-current={currentTab === 'forecasts' ? 'page' : undefined}
          >
            <Compass size={18} strokeWidth={currentTab === 'forecasts' ? 2.2 : 1.75} />
            <span>Panchayat Forecasts</span>
          </button>

          <button
            onClick={() => handleNavClick('review')}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '12px 14px',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              backgroundColor: currentTab === 'review' ? 'var(--primary-050)' : 'transparent',
              color: currentTab === 'review' ? 'var(--primary-700)' : 'var(--ink-700)',
              fontWeight: currentTab === 'review' ? 700 : 500,
              fontSize: '14px',
              cursor: 'pointer',
              width: '100%',
              transition: 'all 0.15s ease',
            }}
            aria-current={currentTab === 'review' ? 'page' : undefined}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <FileCheck2 size={18} strokeWidth={currentTab === 'review' ? 2.2 : 1.75} />
              <span>Advisory Review</span>
            </div>
            {pendingCount > 0 && (
              <span
                style={{
                  backgroundColor: 'var(--warning-100)',
                  color: 'var(--warning-600)',
                  fontSize: '11px',
                  fontWeight: 700,
                  padding: '2px 8px',
                  borderRadius: 'var(--radius-pill)',
                  border: '1px solid rgba(199, 131, 24, 0.3)',
                }}
              >
                {pendingCount}
              </span>
            )}
          </button>

          <button
            onClick={() => handleNavClick('panchayats')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '12px 14px',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              backgroundColor: currentTab === 'panchayats' ? 'var(--primary-050)' : 'transparent',
              color: currentTab === 'panchayats' ? 'var(--primary-700)' : 'var(--ink-700)',
              fontWeight: currentTab === 'panchayats' ? 700 : 500,
              fontSize: '14px',
              cursor: 'pointer',
              textAlign: 'left',
              width: '100%',
              transition: 'all 0.15s ease',
            }}
            aria-current={currentTab === 'panchayats' ? 'page' : undefined}
          >
            <Building2 size={18} strokeWidth={currentTab === 'panchayats' ? 2.2 : 1.75} />
            <span>Panchayat Directory</span>
          </button>

          <button
            onClick={() => handleNavClick('audit')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '12px 14px',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              backgroundColor: currentTab === 'audit' ? 'var(--primary-050)' : 'transparent',
              color: currentTab === 'audit' ? 'var(--primary-700)' : 'var(--ink-700)',
              fontWeight: currentTab === 'audit' ? 700 : 500,
              fontSize: '14px',
              cursor: 'pointer',
              textAlign: 'left',
              width: '100%',
              transition: 'all 0.15s ease',
            }}
            aria-current={currentTab === 'audit' ? 'page' : undefined}
          >
            <History size={18} strokeWidth={currentTab === 'audit' ? 2.2 : 1.75} />
            <span>Approval Audit Log</span>
          </button>

          <div style={{ margin: '16px 8px 8px 8px', borderTop: 'var(--border-subtle)' }} />

          {/* Quick Action: Trigger On-Demand ML Downscaling */}
          <button
            onClick={onOpenGenerateModal}
            className="btn-secondary"
            style={{
              justifyContent: 'flex-start',
              padding: '10px 14px',
              fontSize: '13px',
              color: 'var(--primary-700)',
              borderColor: 'var(--primary-100)',
              backgroundColor: 'var(--primary-050)',
            }}
          >
            <Sparkles size={16} color="var(--primary-600)" />
            <span>Run ML Downscaling</span>
          </button>
        </nav>

        {/* Officer Identity Footer */}
        <div
          style={{
            padding: '16px 20px',
            borderTop: 'var(--border-subtle)',
            backgroundColor: 'var(--surface-subtle)',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
          }}
        >
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: 'var(--radius-pill)',
              backgroundColor: 'var(--primary-700)',
              color: 'var(--surface)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 700,
              fontSize: '13px',
            }}
          >
            AO
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: '13px', fontWeight: 650, color: 'var(--ink-900)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              Dr. S. Patil
            </div>
            <div style={{ fontSize: '11px', color: 'var(--ink-500)', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <ShieldCheck size={12} color="var(--primary-600)" />
              <span>Agromet SMS Officer</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        {/* Top Header Bar */}
        <header
          style={{
            height: '70px',
            backgroundColor: 'var(--surface)',
            borderBottom: 'var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 32px',
            position: 'sticky',
            top: 0,
            zIndex: 20,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {/* Tablet Menu Toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="btn-secondary"
              style={{ padding: '8px', display: 'none' }}
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X size={18} /> : <Menu size={18} />}
            </button>

            <div>
              <div style={{ fontSize: '11px', color: 'var(--ink-500)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Ministry of Earth Sciences • India Meteorological Department
              </div>
              <h1 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--ink-900)' }}>
                {currentTab === 'dashboard' && 'District Agromet Overview'}
                {currentTab === 'forecasts' && 'Panchayat Micro-Forecasts'}
                {currentTab === 'review' && 'Advisory Approval Queue'}
                {currentTab === 'panchayats' && 'Panchayat Geospatial Registry'}
                {currentTab === 'audit' && 'Historical Verification & Audit Trail'}
              </h1>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {/* Forecast Date Indicator */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '6px 14px',
                borderRadius: 'var(--radius-pill)',
                backgroundColor: 'var(--surface-subtle)',
                border: '1px solid var(--ink-300)',
                fontSize: '12px',
                color: 'var(--ink-700)',
                fontWeight: 600,
              }}
            >
              <span>Target: <strong>{forecastDate}</strong></span>
            </div>

            {/* Live System Status Pill */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '6px 14px',
                borderRadius: 'var(--radius-pill)',
                backgroundColor: 'var(--primary-050)',
                border: '1px solid var(--primary-100)',
                fontSize: '12px',
                fontWeight: 600,
                color: 'var(--primary-700)',
              }}
            >
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--primary-500)' }} />
              <span>System Live • Baglan Block</span>
            </div>

            {/* Development / Demo Real Panchayat Selector */}
            {onSelectDemoPanchayat && (
              <DemoPanchayatSelector
                onSelectPanchayat={onSelectDemoPanchayat}
                selectedPanchayatId={selectedDemoPanchayatId}
              />
            )}

            {/* Refresh Button */}
            <button
              onClick={onRefresh}
              className="btn-secondary"
              style={{ padding: '8px 14px', fontSize: '13px' }}
              title="Refresh Live Data"
              aria-label="Refresh Dashboard Data"
            >
              <RefreshCw size={14} className={isRefreshing ? 'spin' : ''} />
              <span>Refresh</span>
            </button>
          </div>
        </header>

        {/* Page Content Container */}
        <main
          style={{
            flex: 1,
            padding: '32px',
            maxWidth: '1440px',
            width: '100%',
            margin: '0 auto',
          }}
          tabIndex={-1}
        >
          {children}
        </main>
      </div>
    </div>
  );
};
