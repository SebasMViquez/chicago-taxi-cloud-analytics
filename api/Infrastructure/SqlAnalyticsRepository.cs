using ChicagoTaxi.Api.Application;
using ChicagoTaxi.Api.Models;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace ChicagoTaxi.Api.Infrastructure;

public sealed class SqlAnalyticsRepository(
    IConfiguration configuration,
    ILogger<SqlAnalyticsRepository> logger) : IAnalyticsRepository
{
    public async Task<DashboardSummary> GetDashboardSummaryAsync(CancellationToken cancellationToken)
    {
        var runId = await GetLatestRunIdAsync(cancellationToken);
        if (runId is null)
        {
            return new DashboardSummary(
                Status: "NO_DATA",
                Message: "No completed analytics run is available yet.",
                TotalTrips: null,
                AverageFare: null,
                AverageMiles: null,
                AverageDurationMinutes: null);
        }

        await using var connection = CreateConnection();
        await connection.OpenAsync(cancellationToken);
        await using var command = connection.CreateCommand();
        command.CommandText = """
            SELECT
                q.AcceptedRows AS TotalTrips,
                fare.AverageFare,
                miles.AverageMiles,
                duration.AverageDurationMinutes
            FROM dbo.DataQualityMetrics q
            OUTER APPLY (
                SELECT
                    SUM(CAST(TripCount AS decimal(18,4)) * AverageFare)
                    / NULLIF(SUM(CAST(TripCount AS decimal(18,4))), 0) AS AverageFare
                FROM dbo.MonthlyTripTrend
                WHERE AnalyticsRunId = @runId
            ) fare
            OUTER APPLY (
                SELECT
                    SUM(CAST(TripCount AS decimal(18,4)) * AverageTripMiles)
                    / NULLIF(SUM(CAST(TripCount AS decimal(18,4))), 0) AS AverageMiles
                FROM dbo.MonthlyTripTrend
                WHERE AnalyticsRunId = @runId
            ) miles
            OUTER APPLY (
                SELECT
                    SUM(CAST(TripCount AS decimal(18,4)) * AverageDurationMinutes)
                    / NULLIF(SUM(CAST(TripCount AS decimal(18,4))), 0) AS AverageDurationMinutes
                FROM dbo.TripCostByDistanceRange
                WHERE AnalyticsRunId = @runId
            ) duration
            WHERE q.AnalyticsRunId = @runId;
            """;
        command.Parameters.AddWithValue("@runId", runId.Value);

        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        if (!await reader.ReadAsync(cancellationToken))
        {
            return new DashboardSummary("NO_DATA", "The latest analytics run has no data quality row.", null, null, null, null);
        }

        return new DashboardSummary(
            Status: "READY",
            Message: $"Showing analytics from completed run {runId.Value}.",
            TotalTrips: reader.GetInt64(reader.GetOrdinal("TotalTrips")),
            AverageFare: GetNullableDecimal(reader, "AverageFare"),
            AverageMiles: GetNullableDecimal(reader, "AverageMiles"),
            AverageDurationMinutes: GetNullableDecimal(reader, "AverageDurationMinutes"));
    }

    public Task<IReadOnlyList<DemandByHourPoint>> GetDemandByHourAsync(CancellationToken cancellationToken) =>
        QueryListAsync(
            """
            SELECT DayOfWeek, HourOfDay, TripCount
            FROM dbo.TripDemandByHour
            WHERE AnalyticsRunId = @runId
            ORDER BY DayOfWeek, HourOfDay;
            """,
            reader => new DemandByHourPoint(
                reader.GetByte(0),
                reader.GetByte(1),
                reader.GetInt64(2)),
            cancellationToken);

    public Task<IReadOnlyList<AreaAnalyticsPoint>> GetAreasAsync(CancellationToken cancellationToken) =>
        QueryListAsync(
            """
            SELECT TOP (20) PickupCommunityArea, TripCount, AverageFare, AverageTripMiles
            FROM dbo.TripDemandByPickupArea
            WHERE AnalyticsRunId = @runId
            ORDER BY TripCount DESC;
            """,
            reader => new AreaAnalyticsPoint(
                GetNullableInt32(reader, 0),
                reader.GetInt64(1),
                GetNullableDecimal(reader, 2),
                GetNullableDecimal(reader, 3)),
            cancellationToken);

    public Task<IReadOnlyList<CostDistancePoint>> GetCostDistanceAsync(CancellationToken cancellationToken) =>
        QueryListAsync(
            """
            SELECT DistanceRangeMiles, TripCount, AverageFare, AverageTripTotal, AverageDurationMinutes
            FROM dbo.TripCostByDistanceRange
            WHERE AnalyticsRunId = @runId
            ORDER BY
                CASE DistanceRangeMiles
                    WHEN '0-2' THEN 1
                    WHEN '2-5' THEN 2
                    WHEN '5-10' THEN 3
                    ELSE 4
                END;
            """,
            reader => new CostDistancePoint(
                reader.GetString(0),
                reader.GetInt64(1),
                GetNullableDecimal(reader, 2),
                GetNullableDecimal(reader, 3),
                GetNullableDecimal(reader, 4)),
            cancellationToken);

    public Task<IReadOnlyList<PaymentTypePoint>> GetPaymentTypesAsync(CancellationToken cancellationToken) =>
        QueryListAsync(
            """
            SELECT PaymentType, TripCount, TotalAmount, AverageTipPercentage
            FROM dbo.PaymentTypeSummary
            WHERE AnalyticsRunId = @runId
            ORDER BY TripCount DESC;
            """,
            reader => new PaymentTypePoint(
                reader.GetString(0),
                reader.GetInt64(1),
                GetNullableDecimal(reader, 2),
                GetNullableDecimal(reader, 3)),
            cancellationToken);

    public Task<IReadOnlyList<MonthlyTrendPoint>> GetMonthlyTrendsAsync(CancellationToken cancellationToken) =>
        QueryListAsync(
            """
            SELECT TripYear, TripMonth, TripCount, AverageFare, AverageTripMiles
            FROM dbo.MonthlyTripTrend
            WHERE AnalyticsRunId = @runId
            ORDER BY TripYear, TripMonth;
            """,
            reader => new MonthlyTrendPoint(
                reader.GetInt16(0),
                reader.GetByte(1),
                reader.GetInt64(2),
                GetNullableDecimal(reader, 3),
                GetNullableDecimal(reader, 4)),
            cancellationToken);

    public async Task<DataQualitySummary?> GetDataQualityAsync(CancellationToken cancellationToken)
    {
        var runId = await GetLatestRunIdAsync(cancellationToken);
        if (runId is null)
        {
            return null;
        }

        await using var connection = CreateConnection();
        await connection.OpenAsync(cancellationToken);
        await using var command = connection.CreateCommand();
        command.CommandText = """
            SELECT SourceRows, AcceptedRows, RejectedRows, DuplicateTripIds, NullRequiredFieldRows,
                   NullPickupAreas, NullDropoffAreas, ZeroDistanceTrips, InvalidDurationRows,
                   InvalidDistanceRows, InvalidFareRows, NegativeTotalRows, CreatedAtUtc
            FROM dbo.DataQualityMetrics
            WHERE AnalyticsRunId = @runId;
            """;
        command.Parameters.AddWithValue("@runId", runId.Value);

        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        if (!await reader.ReadAsync(cancellationToken))
        {
            return null;
        }

        return new DataQualitySummary(
            runId.Value,
            reader.GetInt64(0),
            reader.GetInt64(1),
            reader.GetInt64(2),
            GetNullableInt64(reader, 3),
            GetNullableInt64(reader, 4),
            GetNullableInt64(reader, 5),
            GetNullableInt64(reader, 6),
            GetNullableInt64(reader, 7),
            GetNullableInt64(reader, 8),
            GetNullableInt64(reader, 9),
            GetNullableInt64(reader, 10),
            GetNullableInt64(reader, 11),
            reader.GetDateTime(12));
    }

    private async Task<IReadOnlyList<T>> QueryListAsync<T>(
        string sql,
        Func<SqlDataReader, T> map,
        CancellationToken cancellationToken)
    {
        var runId = await GetLatestRunIdAsync(cancellationToken);
        if (runId is null)
        {
            return [];
        }

        await using var connection = CreateConnection();
        await connection.OpenAsync(cancellationToken);
        await using var command = connection.CreateCommand();
        command.CommandText = sql;
        command.Parameters.AddWithValue("@runId", runId.Value);

        var results = new List<T>();
        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        while (await reader.ReadAsync(cancellationToken))
        {
            results.Add(map(reader));
        }

        return results;
    }

    private async Task<long?> GetLatestRunIdAsync(CancellationToken cancellationToken)
    {
        try
        {
            await using var connection = CreateConnection();
            await connection.OpenAsync(cancellationToken);
            await using var command = connection.CreateCommand();
            command.CommandText = """
                SELECT TOP (1) AnalyticsRunId
                FROM dbo.AnalyticsRuns
                WHERE Status = 'Completed'
                ORDER BY CompletedAtUtc DESC, StartedAtUtc DESC;
                """;

            var result = await command.ExecuteScalarAsync(cancellationToken);
            return result is null or DBNull ? null : Convert.ToInt64(result);
        }
        catch (SqlException ex)
        {
            logger.LogError(ex, "Failed to load latest analytics run from Azure SQL.");
            throw;
        }
    }

    private SqlConnection CreateConnection()
    {
        var server = configuration["SQL_SERVER_NAME"] ?? configuration["SQL_SERVER"];
        var database = configuration["SQL_DATABASE_NAME"] ?? configuration["SQL_DATABASE"];
        var authMode = configuration["SQL_AUTH_MODE"] ?? "ManagedIdentity";

        if (string.IsNullOrWhiteSpace(server) || string.IsNullOrWhiteSpace(database))
        {
            throw new InvalidOperationException("SQL_SERVER_NAME and SQL_DATABASE_NAME are required.");
        }

        var host = server.Contains('.') ? server : $"{server}.database.windows.net";
        var authentication = string.Equals(authMode, "ManagedIdentity", StringComparison.OrdinalIgnoreCase)
            ? "Active Directory Managed Identity"
            : "Active Directory Default";

        var builder = new SqlConnectionStringBuilder
        {
            DataSource = $"tcp:{host},1433",
            InitialCatalog = database,
            Encrypt = true,
            TrustServerCertificate = false,
            ConnectTimeout = 30,
            Authentication = SqlAuthenticationMethod.ActiveDirectoryDefault,
        };

        if (authentication == "Active Directory Managed Identity")
        {
            builder.Authentication = SqlAuthenticationMethod.ActiveDirectoryManagedIdentity;
        }

        return new SqlConnection(builder.ConnectionString);
    }

    private static decimal? GetNullableDecimal(SqlDataReader reader, string name) =>
        GetNullableDecimal(reader, reader.GetOrdinal(name));

    private static decimal? GetNullableDecimal(SqlDataReader reader, int ordinal) =>
        reader.IsDBNull(ordinal) ? null : reader.GetDecimal(ordinal);

    private static long? GetNullableInt64(SqlDataReader reader, int ordinal) =>
        reader.IsDBNull(ordinal) ? null : reader.GetInt64(ordinal);

    private static int? GetNullableInt32(SqlDataReader reader, int ordinal) =>
        reader.IsDBNull(ordinal) ? null : reader.GetInt32(ordinal);
}
