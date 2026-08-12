import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ChartPanel } from "../../components/charts/ChartPanel";
import { MetricCard } from "../../components/charts/MetricCard";
import { StatusPanel } from "../../components/ui/StatusPanel";
import {
  useAreas,
  useCostDistance,
  useDashboardSummary,
  useDataQuality,
  useDemandByHour,
  useMonthlyTrends,
  usePaymentTypes,
} from "../../hooks/useDashboardSummary";
import { formatMonth, formatNullableMetric } from "../../utils/formatting";

const chartColors = ["#126b87", "#d9822b", "#476f55", "#7c3f58", "#475569"];

export function DashboardPage() {
  const summaryQuery = useDashboardSummary();
  const monthlyTrendsQuery = useMonthlyTrends();
  const demandByHourQuery = useDemandByHour();
  const areasQuery = useAreas();
  const costDistanceQuery = useCostDistance();
  const paymentTypesQuery = usePaymentTypes();
  const dataQualityQuery = useDataQuality();

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

  const monthlyTrends = (monthlyTrendsQuery.data ?? []).map((point) => ({
    ...point,
    label: formatMonth(point.year, point.month),
  }));
  const demandByHour = (demandByHourQuery.data ?? []).map((point) => ({
    ...point,
    label: `${point.dayOfWeek}/${point.hourOfDay.toString().padStart(2, "0")}:00`,
  }));
  const areas = areasQuery.data ?? [];
  const costDistance = costDistanceQuery.data ?? [];
  const paymentTypes = paymentTypesQuery.data ?? [];
  const dataQuality = dataQualityQuery.data;
  const analyticsFailed =
    monthlyTrendsQuery.isError ||
    demandByHourQuery.isError ||
    areasQuery.isError ||
    costDistanceQuery.isError ||
    paymentTypesQuery.isError ||
    dataQualityQuery.isError;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-semibold text-ink">Chicago Taxi Trips Analytics</h2>
        <p className="mt-2 max-w-3xl text-slate-600">
          Dashboard-ready aggregates from the latest completed analytics run.
        </p>
      </div>

      <StatusPanel status="ready" title={summary.status} message={summary.message} />

      {analyticsFailed ? (
        <StatusPanel
          status="error"
          title="Analytics unavailable"
          message="One or more analytical endpoints could not be loaded."
        />
      ) : null}

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Total trips" value={formatNullableMetric(summary.totalTrips)} />
        <MetricCard label="Average fare" value={formatNullableMetric(summary.averageFare, "$")} />
        <MetricCard label="Average miles" value={formatNullableMetric(summary.averageMiles)} />
        <MetricCard
          label="Average duration"
          value={formatNullableMetric(summary.averageDurationMinutes, undefined, " min")}
        />
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <ChartPanel title="Monthly trends" isEmpty={monthlyTrends.length === 0}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={monthlyTrends} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="label" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Line type="monotone" dataKey="tripCount" stroke="#126b87" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartPanel>

        <ChartPanel title="Demand by day and hour" isEmpty={demandByHour.length === 0}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={demandByHour} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="label" tick={{ fontSize: 11 }} interval="preserveStartEnd" />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="tripCount" fill="#126b87" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartPanel>

        <ChartPanel title="Top pickup areas" isEmpty={areas.length === 0}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={areas.slice(0, 10)}
              layout="vertical"
              margin={{ top: 8, right: 16, left: 12, bottom: 8 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis type="number" tick={{ fontSize: 12 }} />
              <YAxis type="category" dataKey="pickupCommunityArea" width={44} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="tripCount" fill="#476f55" radius={[0, 3, 3, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartPanel>

        <ChartPanel title="Payment types" isEmpty={paymentTypes.length === 0}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={paymentTypes}
                dataKey="tripCount"
                nameKey="paymentType"
                innerRadius={54}
                outerRadius={96}
                paddingAngle={2}
              >
                {paymentTypes.map((entry, index) => (
                  <Cell key={entry.paymentType} fill={chartColors[index % chartColors.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartPanel>

        <ChartPanel title="Cost by distance" isEmpty={costDistance.length === 0}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={costDistance} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="distanceRangeMiles" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="averageTripTotal" fill="#d9822b" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartPanel>

        <section className="rounded border border-slate-200 bg-white p-4 shadow-sm">
          <h3 className="text-sm font-semibold uppercase text-slate-500">Data quality</h3>
          {dataQuality ? (
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <MetricCard label="Source rows" value={formatNullableMetric(dataQuality.sourceRows)} />
              <MetricCard label="Accepted rows" value={formatNullableMetric(dataQuality.acceptedRows)} />
              <MetricCard label="Rejected rows" value={formatNullableMetric(dataQuality.rejectedRows)} />
              <MetricCard
                label="Invalid fare rows"
                value={formatNullableMetric(dataQuality.invalidFareRows)}
              />
            </div>
          ) : (
            <div className="mt-4 flex h-60 items-center justify-center rounded border border-dashed border-slate-300 text-sm text-slate-500">
              No data available
            </div>
          )}
        </section>
      </section>
    </div>
  );
}
