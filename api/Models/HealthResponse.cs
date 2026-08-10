namespace ChicagoTaxi.Api.Models;

public sealed record HealthResponse(string Status, string Service, DateTimeOffset CheckedAtUtc);

