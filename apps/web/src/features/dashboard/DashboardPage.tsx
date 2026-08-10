import { MetricCard } from "../../components/charts/MetricCard";
import { StatusPanel } from "../../components/ui/StatusPanel";
import { useDashboardSummary } from "../../hooks/useDashboardSummary";
import { formatNullableMetric } from "../../utils/formatting";

export function DashboardPage() {
  const summaryQuery = useDashboardSummary();

  if (summaryQuery.isLoading) {
    return (
      <StatusPanel
        status="loading"
        title="Loading dashboard summary"
        message="Checking whether analytical results are available."
      />
    );
  }

  if (summaryQuery.isError) {
    return (
      <StatusPanel
        status="error"
        title="API unavailable"
        message="The dashboard summary endpoint could not be reached. Start the Azure Functions API locally and try again."
      />
    );
  }

  const summary = summaryQuery.data;

  if (!summary) {
    return (
      <StatusPanel
        status="error"
        title="Summary unavailable"
        message="The API response did not include a dashboard summary."
      />
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-semibold text-ink">Chicago Taxi Trips Analytics</h2>
        <p className="mt-2 max-w-3xl text-slate-600">
          Initial vertical slice for the university big data processing project.
        </p>
      </div>

      <StatusPanel status="ready" title={summary.status} message={summary.message} />

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Total trips" value={formatNullableMetric(summary.totalTrips)} />
        <MetricCard label="Average fare" value={formatNullableMetric(summary.averageFare, "$")} />
        <MetricCard label="Average miles" value={formatNullableMetric(summary.averageMiles)} />
        <MetricCard
          label="Average duration"
          value={formatNullableMetric(summary.averageDurationMinutes, undefined, " min")}
        />
      </section>
    </div>
  );
}
