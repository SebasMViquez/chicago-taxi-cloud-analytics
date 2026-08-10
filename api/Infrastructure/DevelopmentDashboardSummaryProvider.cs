using ChicagoTaxi.Api.Application;
using ChicagoTaxi.Api.Models;

namespace ChicagoTaxi.Api.Infrastructure;

public sealed class DevelopmentDashboardSummaryProvider : IDashboardSummaryProvider
{
    public Task<DashboardSummary> GetSummaryAsync(CancellationToken cancellationToken)
    {
        var summary = new DashboardSummary(
            Status: "DEVELOPMENT_NO_DATA",
            Message: "No analytical results have been processed yet. This development response is not based on the real Chicago Taxi Trips dataset.",
            TotalTrips: null,
            AverageFare: null,
            AverageMiles: null,
            AverageDurationMinutes: null);

        return Task.FromResult(summary);
    }
}

