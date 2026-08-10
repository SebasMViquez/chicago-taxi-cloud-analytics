using ChicagoTaxi.Api.Models;

namespace ChicagoTaxi.Api.Application;

public interface IDashboardSummaryProvider
{
    Task<DashboardSummary> GetSummaryAsync(CancellationToken cancellationToken);
}

