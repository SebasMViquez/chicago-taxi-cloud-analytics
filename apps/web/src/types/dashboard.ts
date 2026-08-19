export type DashboardSummaryStatus = "DEVELOPMENT_NO_DATA" | "NO_DATA" | "READY";

export type DashboardSummary = {
  status: DashboardSummaryStatus;
  message: string;
  totalTrips: number | null;
  averageFare: number | null;
  averageMiles: number | null;
  averageDurationMinutes: number | null;
};

export type DemandByHourPoint = {
  dayOfWeek: number;
  hourOfDay: number;
  tripCount: number;
};

export type AreaAnalyticsPoint = {
  pickupCommunityArea: number | null;
  tripCount: number;
  averageFare: number | null;
  averageTripMiles: number | null;
};

export type CostDistancePoint = {
  distanceRangeMiles: string;
  tripCount: number;
  averageFare: number | null;
  averageTripTotal: number | null;
  averageDurationMinutes: number | null;
};

export type PaymentTypePoint = {
  paymentType: string;
  tripCount: number;
  totalAmount: number | null;
  averageTipPercentage: number | null;
};

export type MonthlyTrendPoint = {
  year: number;
  month: number;
  tripCount: number;
  averageFare: number | null;
  averageTripMiles: number | null;
};

export type DataQualitySummary = {
  analyticsRunId: number;
  sourceRows: number;
  acceptedRows: number;
  rejectedRows: number;
  duplicateTripIds: number | null;
  nullRequiredFieldRows: number | null;
  nullPickupAreas: number | null;
  nullDropoffAreas: number | null;
  zeroDistanceTrips: number | null;
  invalidDurationRows: number | null;
  invalidDistanceRows: number | null;
  invalidFareRows: number | null;
  negativeTotalRows: number | null;
  createdAtUtc: string;
};

