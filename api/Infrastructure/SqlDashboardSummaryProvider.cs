using ChicagoTaxi.Api.Application;
using ChicagoTaxi.Api.Models;

namespace ChicagoTaxi.Api.Infrastructure;

public sealed class SqlDashboardSummaryProvider(IAnalyticsRepository analyticsRepository)
    : IDashboardSummaryProvider
{
    public Task<DashboardSummary> GetSummaryAsync(CancellationToken cancellationToken) =>
        analyticsRepository.GetDashboardSummaryAsync(cancellationToken);
}
