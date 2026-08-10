export type DashboardSummaryStatus = "DEVELOPMENT_NO_DATA" | "READY";

export type DashboardSummary = {
  status: DashboardSummaryStatus;
  message: string;
  totalTrips: number | null;
  averageFare: number | null;
  averageMiles: number | null;
  averageDurationMinutes: number | null;
};

