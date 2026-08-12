using ChicagoTaxi.Api.Models;

namespace ChicagoTaxi.Api.Application;

public interface IAnalyticsRepository
{
    Task<DashboardSummary> GetDashboardSummaryAsync(CancellationToken cancellationToken);

    Task<IReadOnlyList<DemandByHourPoint>> GetDemandByHourAsync(CancellationToken cancellationToken);

    Task<IReadOnlyList<AreaAnalyticsPoint>> GetAreasAsync(CancellationToken cancellationToken);

    Task<IReadOnlyList<CostDistancePoint>> GetCostDistanceAsync(CancellationToken cancellationToken);

    Task<IReadOnlyList<PaymentTypePoint>> GetPaymentTypesAsync(CancellationToken cancellationToken);

    Task<IReadOnlyList<MonthlyTrendPoint>> GetMonthlyTrendsAsync(CancellationToken cancellationToken);

    Task<DataQualitySummary?> GetDataQualityAsync(CancellationToken cancellationToken);
}
