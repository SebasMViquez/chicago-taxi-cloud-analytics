using System.Net;
using ChicagoTaxi.Api.Application;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Azure.Functions.Worker.Http;

namespace ChicagoTaxi.Api.Functions;

public sealed class AnalyticsFunctions(IAnalyticsRepository analyticsRepository)
{
    [Function("DemandByHour")]
    public async Task<HttpResponseData> DemandByHour(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "analytics/demand/hourly")] HttpRequestData request,
        CancellationToken cancellationToken)
    {
        return await JsonAsync(request, await analyticsRepository.GetDemandByHourAsync(cancellationToken), cancellationToken);
    }

    [Function("Areas")]
    public async Task<HttpResponseData> Areas(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "analytics/areas")] HttpRequestData request,
        CancellationToken cancellationToken)
    {
        return await JsonAsync(request, await analyticsRepository.GetAreasAsync(cancellationToken), cancellationToken);
    }

    [Function("CostDistance")]
    public async Task<HttpResponseData> CostDistance(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "analytics/cost-distance")] HttpRequestData request,
        CancellationToken cancellationToken)
    {
        return await JsonAsync(request, await analyticsRepository.GetCostDistanceAsync(cancellationToken), cancellationToken);
    }

    [Function("PaymentTypes")]
    public async Task<HttpResponseData> PaymentTypes(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "analytics/payment-types")] HttpRequestData request,
        CancellationToken cancellationToken)
    {
        return await JsonAsync(request, await analyticsRepository.GetPaymentTypesAsync(cancellationToken), cancellationToken);
    }

    [Function("MonthlyTrends")]
    public async Task<HttpResponseData> MonthlyTrends(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "analytics/trends/monthly")] HttpRequestData request,
        CancellationToken cancellationToken)
    {
        return await JsonAsync(request, await analyticsRepository.GetMonthlyTrendsAsync(cancellationToken), cancellationToken);
    }

    [Function("DataQuality")]
    public async Task<HttpResponseData> DataQuality(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "data-quality")] HttpRequestData request,
        CancellationToken cancellationToken)
    {
        var quality = await analyticsRepository.GetDataQualityAsync(cancellationToken);
        var response = request.CreateResponse(quality is null ? HttpStatusCode.NoContent : HttpStatusCode.OK);
        if (quality is not null)
        {
            await response.WriteAsJsonAsync(quality, cancellationToken);
        }

        return response;
    }

    private static async Task<HttpResponseData> JsonAsync<T>(
        HttpRequestData request,
        T value,
        CancellationToken cancellationToken)
    {
        var response = request.CreateResponse(HttpStatusCode.OK);
        await response.WriteAsJsonAsync(value, cancellationToken);
        return response;
    }
}
