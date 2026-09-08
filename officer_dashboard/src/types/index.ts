export interface PanchayatItem {
  panchayat_id: number;
  lgd_code: number;
  panchayat_name: string;
  block_name: string;
  district_name: string;
  latitude: number;
  longitude: number;
  elevation_m: number;
}

export interface PanchayatPagination {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: PanchayatItem[];
}

export interface AdvisoryItem {
  id: number;
  panchayat_id: number;
  forecast_id: number;
  forecast_date: string;
  rainfall_mm: number;
  rainfall_category: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  advisory_title: string;
  advisory_text: string;
  status: 'DRAFT' | 'APPROVED' | 'REJECTED';
  rule_id?: string;
  rule_version?: string;
  officer_id?: string | null;
  officer_comment?: string | null;
  approved_at?: string | null;
  created_at?: string;
  // Spatial & forecast metadata resolved for detail view
  panchayat_name?: string;
  block_name?: string;
  district_name?: string;
  elevation_m?: number;
  latitude?: number;
  longitude?: number;
  block_forecast_mm?: number;
  actual_observed_rainfall_mm?: number | null;
  forecast_issue_date?: string;
  model_name?: string;
  model_version?: string;
}

export interface DownscaledForecastDetail {
  id: number;
  panchayat_id: number;
  panchayat_name: string;
  block_name: string;
  district_name: string;
  forecast_date: string;
  forecast_issue_date: string;
  lead_days: number;
  block_forecast_rainfall_mm: number;
  downscaled_rainfall_mm: number;
  model_name: string;
  model_version: string;
  confidence?: number | null;
}

export interface OfficerApprovePayload {
  officer_id: string;
  officer_comment?: string;
}

export interface OfficerRejectPayload {
  officer_id: string;
  officer_comment?: string;
}

export interface GenerateForecastPayload {
  panchayat_id: number;
  forecast_date: string;
  forecast_issue_date: string;
}
