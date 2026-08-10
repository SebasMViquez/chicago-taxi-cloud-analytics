import type { DashboardSummary } from "../types/dashboard";
import { getJson } from "./httpClient";

export function getDashboardSummary(): Promise<DashboardSummary> {
  return getJson<DashboardSummary>("/api/dashboard/summary");
}

