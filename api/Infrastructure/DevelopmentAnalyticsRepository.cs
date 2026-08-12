using ChicagoTaxi.Api.Application;
using ChicagoTaxi.Api.Models;

namespace ChicagoTaxi.Api.Infrastructure;

public sealed class DevelopmentAnalyticsRepository : IAnalyticsRepository
{
    public Task<DashboardSummary> GetDashboardSummaryAsync(CancellationToken cancellationToken) =>
        new DevelopmentDashboardSummaryProvider().GetSummaryAsync(cancellationToken);

    public Task<IReadOnlyList<DemandByHourPoint>> GetDemandByHourAsync(CancellationToken cancellationToken) =>
        Task.FromResult<IReadOnlyList<DemandByHourPoint>>([]);

    public Task<IReadOnlyList<AreaAnalyticsPoint>> GetAreasAsync(CancellationToken cancellationToken) =>
        Task.FromResult<IReadOnlyList<AreaAnalyticsPoint>>([]);

    public Task<IReadOnlyList<CostDistancePoint>> GetCostDistanceAsync(CancellationToken cancellationToken) =>
        Task.FromResult<IReadOnlyList<CostDistancePoint>>([]);

    public Task<IReadOnlyList<PaymentTypePoint>> GetPaymentTypesAsync(CancellationToken cancellationToken) =>
        Task.FromResult<IReadOnlyList<PaymentTypePoint>>([]);

    public Task<IReadOnlyList<MonthlyTrendPoint>> GetMonthlyTrendsAsync(CancellationToken cancellationToken) =>
        Task.FromResult<IReadOnlyList<MonthlyTrendPoint>>([]);

    public Task<DataQualitySummary?> GetDataQualityAsync(CancellationToken cancellationToken) =>
        Task.FromResult<DataQualitySummary?>(null);
}
