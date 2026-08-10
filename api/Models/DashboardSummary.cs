namespace ChicagoTaxi.Api.Models;

public sealed record DashboardSummary(
    string Status,
    string Message,
    long? TotalTrips,
    decimal? AverageFare,
    decimal? AverageMiles,
    decimal? AverageDurationMinutes);

