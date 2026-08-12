import { useQuery } from "@tanstack/react-query";
import {
  getAreas,
  getCostDistance,
  getDashboardSummary,
  getDataQuality,
  getDemandByHour,
  getMonthlyTrends,
  getPaymentTypes,
} from "../services/dashboardService";

export function useDashboardSummary() {
  return useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: getDashboardSummary,
  });
}

export function useDemandByHour() {
  return useQuery({
    queryKey: ["analytics", "demand-hourly"],
    queryFn: getDemandByHour,
  });
}

export function useAreas() {
  return useQuery({
    queryKey: ["analytics", "areas"],
    queryFn: getAreas,
  });
}

export function useCostDistance() {
  return useQuery({
    queryKey: ["analytics", "cost-distance"],
    queryFn: getCostDistance,
  });
}

export function usePaymentTypes() {
  return useQuery({
    queryKey: ["analytics", "payment-types"],
    queryFn: getPaymentTypes,
  });
}

export function useMonthlyTrends() {
  return useQuery({
    queryKey: ["analytics", "monthly-trends"],
    queryFn: getMonthlyTrends,
  });
}

export function useDataQuality() {
  return useQuery({
    queryKey: ["data-quality"],
    queryFn: getDataQuality,
  });
}

