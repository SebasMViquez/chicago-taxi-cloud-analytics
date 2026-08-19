using System.Text.Json;
using ChicagoTaxi.Api.Models;
using Xunit;

namespace ChicagoTaxi.Api.Tests;

public sealed class AreaAnalyticsPointTests
{
    [Fact]
    public void AreaAnalyticsPoint_AllowsNullPickupCommunityArea()
    {
        var point = new AreaAnalyticsPoint(
            PickupCommunityArea: null,
            TripCount: 123357,
            AverageFare: 31.79m,
            AverageTripMiles: 10.82m);

        var json = JsonSerializer.Serialize(point);

        Assert.Null(point.PickupCommunityArea);
        Assert.Contains("\"PickupCommunityArea\":null", json);
    }
}
