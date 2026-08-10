using ChicagoTaxi.Api.Infrastructure;
using Xunit;

namespace ChicagoTaxi.Api.Tests;

public sealed class DevelopmentDashboardSummaryProviderTests
{
    [Fact]
    public async Task GetSummaryAsync_ReturnsClearlyMarkedDevelopmentResponse()
    {
        var provider = new DevelopmentDashboardSummaryProvider();

        var summary = await provider.GetSummaryAsync(CancellationToken.None);

        Assert.Equal("DEVELOPMENT_NO_DATA", summary.Status);
        Assert.Null(summary.TotalTrips);
        Assert.Contains("development", summary.Message, StringComparison.OrdinalIgnoreCase);
    }
}
