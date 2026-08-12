namespace ChicagoTaxi.Api.Models;

public sealed record DemandByHourPoint(
    int DayOfWeek,
    int HourOfDay,
    long TripCount);

public sealed record AreaAnalyticsPoint(
    int PickupCommunityArea,
    long TripCount,
    decimal? AverageFare,
    decimal? AverageTripMiles);

public sealed record CostDistancePoint(
    string DistanceRangeMiles,
    long TripCount,
    decimal? AverageFare,
    decimal? AverageTripTotal,
    decimal? AverageDurationMinutes);

public sealed record PaymentTypePoint(
    string PaymentType,
    long TripCount,
    decimal? TotalAmount,
    decimal? AverageTipPercentage);

public sealed record MonthlyTrendPoint(
    int Year,
    int Month,
    long TripCount,
    decimal? AverageFare,
    decimal? AverageTripMiles);

public sealed record DataQualitySummary(
    long AnalyticsRunId,
    long SourceRows,
    long AcceptedRows,
    long RejectedRows,
    long? DuplicateTripIds,
    long? NullRequiredFieldRows,
    long? NullPickupAreas,
    long? NullDropoffAreas,
    long? ZeroDistanceTrips,
    long? InvalidDurationRows,
    long? InvalidDistanceRows,
    long? InvalidFareRows,
    long? NegativeTotalRows,
    DateTime CreatedAtUtc);
