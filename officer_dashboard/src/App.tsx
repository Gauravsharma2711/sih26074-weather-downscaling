import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  Clock, 
  CheckCircle2, 
  MapPin, 
  Calendar, 
  Compass,
  AlertTriangle
} from 'lucide-react';
import { AppShell } from './components/AppShell';
import { MetricCard } from './components/MetricCard';
import { WeatherHeroCard } from './components/WeatherHeroCard';
import { AdvisoryReviewQueue } from './components/AdvisoryReviewQueue';
import { PanchayatForecastSection } from './components/PanchayatForecastSection';
import { PanchayatGrid } from './components/PanchayatGrid';
import { AuditLogView } from './components/AuditLogView';
import { ApprovalConfirmModal } from './components/ApprovalConfirmModal';
import { RejectionModal } from './components/RejectionModal';
import { AdvisoryDetailModal } from './components/AdvisoryDetailModal';
import { ForecastGenerateModal } from './components/ForecastGenerateModal';
import { PanchayatDetailView } from './components/PanchayatDetailView';
import { WorkflowPipeline } from './components/common/WorkflowPipeline';
import { SkeletonLoader } from './components/common/SkeletonLoader';
import { ErrorState } from './components/common/ErrorState';
import { ApiService } from './services/api';
import { PanchayatItem, AdvisoryItem, DownscaledForecastDetail } from './types';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<'dashboard' | 'forecasts' | 'review' | 'audit' | 'panchayats'>('dashboard');
  const [panchayats, setPanchayats] = useState<PanchayatItem[]>([]);
  const [advisories, setAdvisories] = useState<AdvisoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Selected Panchayat for Detail Screen
  const [selectedPanchayatDetail, setSelectedPanchayatDetail] = useState<PanchayatItem | null>(null);

  // Modals state for review workflow
  const [selectedAdvisoryForApproval, setSelectedAdvisoryForApproval] = useState<AdvisoryItem | null>(null);
  const [selectedAdvisoryForRejection, setSelectedAdvisoryForRejection] = useState<AdvisoryItem | null>(null);
  const [selectedAdvisoryForDetail, setSelectedAdvisoryForDetail] = useState<AdvisoryItem | null>(null);

  const [isGenerateModalOpen, setIsGenerateModalOpen] = useState(false);
  const [preselectedPanchayatForGen, setPreselectedPanchayatForGen] = useState<PanchayatItem | null>(null);

  // Notification Toast
  const [toastMessage, setToastMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  const forecastDate = '2026-09-09';
  const districtName = 'Nashik';

  const showToast = (text: string, type: 'success' | 'error' = 'success') => {
    setToastMessage({ text, type });
    setTimeout(() => setToastMessage(null), 4000);
  };

  const loadData = async () => {
    setError(null);
    try {
      const [panchayatRes, advisoriesRes] = await Promise.all([
        ApiService.getPanchayats(),
        ApiService.getOfficerAdvisories(),
      ]);
      setPanchayats(panchayatRes.items);
      setAdvisories(advisoriesRes);
    } catch (err: any) {
      console.error('Error loading officer dashboard data:', err);
      setError('Unable to load latest advisory and downscaled forecast records from API.');
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRefresh = () => {
    setIsRefreshing(true);
    loadData();
  };

  // Submit Approval to backend
  const handleApproveAdvisory = async (advisoryId: number, comment: string) => {
    try {
      const updated = await ApiService.approveAdvisory(advisoryId, {
        officer_id: 'DR-S-PATIL-AO',
        officer_comment: comment || 'Verified against AWS ground trends. Approved for farmer distribution.',
      });
      showToast(`Advisory for ${updated.panchayat_name || 'Panchayat'} approved and published to Farmer App!`);
      await loadData();
    } catch (err: any) {
      showToast(`Approval failed: ${err.message}`, 'error');
      throw err;
    }
  };

  // Submit Rejection to backend
  const handleRejectAdvisory = async (advisoryId: number, reason: string) => {
    try {
      const updated = await ApiService.rejectAdvisory(advisoryId, {
        officer_id: 'DR-S-PATIL-AO',
        officer_comment: reason,
      });
      showToast(`Advisory for ${updated.panchayat_name || 'Panchayat'} rejected and logged in audit trail.`);
      await loadData();
    } catch (err: any) {
      showToast(`Rejection failed: ${err.message}`, 'error');
      throw err;
    }
  };

  // Trigger On-Demand Inference
  const handleGenerateForecast = async (
    panchayatId: number,
    targetDate: string,
    issueDate: string
  ): Promise<DownscaledForecastDetail> => {
    const res = await ApiService.generateForecast({
      panchayat_id: panchayatId,
      forecast_date: targetDate,
      forecast_issue_date: issueDate,
    });
    showToast(`Downscaled forecast generated for ${res.panchayat_name}!`);
    await loadData();
    return res;
  };

  const draftCount = advisories.filter((a) => a.status === 'DRAFT').length;
  const approvedCount = advisories.filter((a) => a.status === 'APPROVED').length;
  const totalForecastsAvailable = panchayats.length;

  const activeDetailAdvisory = selectedPanchayatDetail
    ? advisories.find((a) => a.panchayat_id === selectedPanchayatDetail.panchayat_id)
    : null;

  return (
    <AppShell
      currentTab={currentTab}
      onSelectTab={(tab) => {
        setSelectedPanchayatDetail(null);
        setCurrentTab(tab);
      }}
      pendingCount={draftCount}
      onOpenGenerateModal={() => {
        setPreselectedPanchayatForGen(null);
        setIsGenerateModalOpen(true);
      }}
      onRefresh={handleRefresh}
      isRefreshing={isRefreshing}
      forecastDate={forecastDate}
      onSelectDemoPanchayat={(p) => {
        setSelectedPanchayatDetail(p);
        showToast(`Loaded live Panchayat: ${p.panchayat_name} (${p.block_name} Block)`);
      }}
      selectedDemoPanchayatId={selectedPanchayatDetail?.panchayat_id}
    >
      {/* Toast Notification */}
      {toastMessage && (
        <div
          style={{
            position: 'fixed',
            bottom: '24px',
            right: '24px',
            backgroundColor: toastMessage.type === 'error' ? 'var(--danger-600)' : 'var(--ink-900)',
            color: 'var(--surface)',
            padding: '12px 20px',
            borderRadius: 'var(--radius-pill)',
            boxShadow: 'var(--shadow-modal)',
            fontSize: '13px',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            zIndex: 100,
            animation: 'fadeIn 0.2s ease',
          }}
          role="status"
        >
          {toastMessage.type === 'error' ? (
            <AlertTriangle size={16} color="#FFFFFF" />
          ) : (
            <CheckCircle2 size={16} color="var(--primary-500)" />
          )}
          <span>{toastMessage.text}</span>
        </div>
      )}

      {/* Loading State */}
      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <SkeletonLoader type="metric" count={4} />
          <SkeletonLoader type="card" count={3} />
        </div>
      ) : error ? (
        /* Error State */
        <ErrorState
          title="Connection Error"
          message={error}
          onRetry={loadData}
        />
      ) : selectedPanchayatDetail ? (
        /* PANCHAYAT DETAIL SCREEN */
        <PanchayatDetailView
          panchayat={selectedPanchayatDetail}
          advisory={activeDetailAdvisory}
          onBack={() => setSelectedPanchayatDetail(null)}
          onApproveAdvisory={(adv) => setSelectedAdvisoryForApproval(adv)}
          onRejectAdvisory={(adv) => setSelectedAdvisoryForRejection(adv)}
          onOpenGenerateModal={(p) => {
            setPreselectedPanchayatForGen(p);
            setIsGenerateModalOpen(true);
          }}
        />
      ) : (
        /* Active Tab Content */
        <>
          {/* TAB 1: DASHBOARD OVERVIEW */}
          {currentTab === 'dashboard' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }} className="fade-in">
              {/* Workflow Pipeline Diagram */}
              <WorkflowPipeline />

              {/* Overview Metrics Cards */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                  gap: '20px',
                }}
              >
                {/* 1. District & Jurisdiction */}
                <MetricCard
                  label="Pilot District"
                  value={districtName}
                  subtext="Baglan Block Jurisdiction"
                  icon={<MapPin size={20} />}
                  accentColor="var(--primary-700)"
                />

                {/* 2. Forecast Date & Availability */}
                <MetricCard
                  label="Forecast Date"
                  value={forecastDate}
                  subtext={`${totalForecastsAvailable} of ${totalForecastsAvailable} Forecasts Available`}
                  icon={<Calendar size={20} />}
                  trend={{
                    text: '100% Synced',
                    isPositive: true,
                  }}
                  accentColor="var(--primary-600)"
                />

                {/* 3. Panchayat Count */}
                <MetricCard
                  label="Panchayat Count"
                  value={panchayats.length}
                  subtext="Monitored in Baglan Block"
                  icon={<Building2 size={20} />}
                  accentColor="var(--primary-700)"
                />

                {/* 4. Advisories Pending Review */}
                <MetricCard
                  label="Advisories Pending Review"
                  value={draftCount}
                  subtext="Require human officer approval"
                  icon={<Clock size={20} />}
                  trend={{
                    text: draftCount > 0 ? `${draftCount} Need Review` : 'All Clear',
                    isPositive: draftCount === 0,
                    color: draftCount > 0 ? 'var(--warning-600)' : 'var(--primary-700)',
                  }}
                  accentColor="var(--warning-600)"
                />

                {/* 5. Approved Advisories */}
                <MetricCard
                  label="Approved Advisories"
                  value={approvedCount}
                  subtext="Active on Farmer Mobile App"
                  icon={<CheckCircle2 size={20} />}
                  trend={{
                    text: 'Verified by Officer',
                    isPositive: true,
                  }}
                  accentColor="var(--primary-700)"
                />
              </div>

              {/* Weather Downscaling Hero Card */}
              <WeatherHeroCard
                advisories={advisories}
                onReviewClick={(advisory) => {
                  setSelectedAdvisoryForDetail(advisory);
                }}
              />

              {/* Quick Jump: Priority Review Queue Preview */}
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                  <div>
                    <h2 className="text-section-title">Priority Advisory Review Queue</h2>
                    <p className="text-body" style={{ fontSize: '13px', color: 'var(--ink-500)' }}>
                      Inspect and validate deterministic agricultural advisories before mobile delivery.
                    </p>
                  </div>

                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button
                      onClick={() => setCurrentTab('forecasts')}
                      className="btn-secondary"
                      style={{ padding: '6px 14px', fontSize: '12px' }}
                    >
                      <Compass size={13} />
                      <span>View All Forecasts</span>
                    </button>
                    <button
                      onClick={() => setCurrentTab('review')}
                      className="btn-primary"
                      style={{ padding: '6px 14px', fontSize: '12px' }}
                    >
                      <span>Full Review Queue ({advisories.length})</span>
                    </button>
                  </div>
                </div>

                <AdvisoryReviewQueue
                  advisories={advisories}
                  onApproveAdvisory={handleApproveAdvisory}
                  onRejectAdvisory={handleRejectAdvisory}
                />
              </div>
            </div>
          )}

          {/* TAB 2: PANCHAYAT FORECASTS SECTION */}
          {currentTab === 'forecasts' && (
            <div className="fade-in">
              <PanchayatForecastSection
                panchayats={panchayats}
                advisories={advisories}
                onReviewAdvisory={(a) => {
                  setSelectedAdvisoryForDetail(a);
                }}
                onGenerateForecast={(p) => {
                  setPreselectedPanchayatForGen(p);
                  setIsGenerateModalOpen(true);
                }}
              />
            </div>
          )}

          {/* TAB 3: ADVISORY REVIEW SECTION */}
          {currentTab === 'review' && (
            <div className="fade-in">
              <AdvisoryReviewQueue
                advisories={advisories}
                onApproveAdvisory={handleApproveAdvisory}
                onRejectAdvisory={handleRejectAdvisory}
              />
            </div>
          )}

          {/* TAB 4: PANCHAYAT GEOSPATIAL DIRECTORY */}
          {currentTab === 'panchayats' && (
            <div className="fade-in">
              <PanchayatGrid
                panchayats={panchayats}
                onSelectPanchayat={(p) => {
                  setSelectedPanchayatDetail(p);
                }}
                onGenerateForPanchayat={(p) => {
                  setPreselectedPanchayatForGen(p);
                  setIsGenerateModalOpen(true);
                }}
              />
            </div>
          )}

          {/* TAB 5: AUDIT LOG */}
          {currentTab === 'audit' && (
            <div className="fade-in">
              <AuditLogView advisories={advisories} />
            </div>
          )}
        </>
      )}

      {/* Modal: Advisory Full Detail View */}
      <AdvisoryDetailModal
        advisory={selectedAdvisoryForDetail}
        isOpen={Boolean(selectedAdvisoryForDetail)}
        onClose={() => setSelectedAdvisoryForDetail(null)}
        onRequestApprove={(adv) => {
          setSelectedAdvisoryForDetail(null);
          setSelectedAdvisoryForApproval(adv);
        }}
        onRequestReject={(adv) => {
          setSelectedAdvisoryForDetail(null);
          setSelectedAdvisoryForRejection(adv);
        }}
      />

      {/* Modal: Advisory Approval Confirmation Dialog */}
      <ApprovalConfirmModal
        advisory={selectedAdvisoryForApproval}
        isOpen={Boolean(selectedAdvisoryForApproval)}
        onClose={() => setSelectedAdvisoryForApproval(null)}
        onConfirmApprove={handleApproveAdvisory}
      />

      {/* Modal: Advisory Rejection Dialog */}
      <RejectionModal
        advisory={selectedAdvisoryForRejection}
        isOpen={Boolean(selectedAdvisoryForRejection)}
        onClose={() => setSelectedAdvisoryForRejection(null)}
        onConfirmReject={handleRejectAdvisory}
      />

      {/* Modal: On-Demand ML Inference */}
      <ForecastGenerateModal
        isOpen={isGenerateModalOpen}
        onClose={() => setIsGenerateModalOpen(false)}
        panchayats={panchayats}
        preselectedPanchayat={preselectedPanchayatForGen}
        onGenerate={handleGenerateForecast}
      />
    </AppShell>
  );
};
