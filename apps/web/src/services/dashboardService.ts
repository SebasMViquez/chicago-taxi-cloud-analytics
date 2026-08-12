import type {
  AreaAnalyticsPoint,
  CostDistancePoint,
  DashboardSummary,
  DataQualitySummary,
  DemandByHourPoint,
  MonthlyTrendPoint,
  PaymentTypePoint,
} from "../types/dashboard";
import { getJson } from "./httpClient";

export function getDashboardSummary(): Promise<DashboardSummary> {
  return getJson<DashboardSummary>("/api/dashboard/summary");
}

export function getDemandByHour(): Promise<DemandByHourPoint[]> {
  return getJson<DemandByHourPoint[]>("/api/analytics/demand/hourly");
}

export function getAreas(): Promise<AreaAnalyticsPoint[]> {
  return getJson<AreaAnalyticsPoint[]>("/api/analytics/areas");
}

export function getCostDistance(): Promise<CostDistancePoint[]> {
  return getJson<CostDistancePoint[]>("/api/analytics/cost-distance");
}

export function getPaymentTypes(): Promise<PaymentTypePoint[]> {
  return getJson<PaymentTypePoint[]>("/api/analytics/payment-types");
}

export function getMonthlyTrends(): Promise<MonthlyTrendPoint[]> {
  return getJson<MonthlyTrendPoint[]>("/api/analytics/trends/monthly");
}

export function getDataQuality(): Promise<DataQualitySummary | null> {
  return getJson<DataQualitySummary | null>("/api/data-quality");
}

