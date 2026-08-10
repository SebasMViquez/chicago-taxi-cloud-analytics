using System.Net;
using ChicagoTaxi.Api.Application;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Azure.Functions.Worker.Http;

namespace ChicagoTaxi.Api.Functions;

public sealed class DashboardSummaryFunction(IDashboardSummaryProvider dashboardSummaryProvider)
{
    [Function("DashboardSummary")]
    public async Task<HttpResponseData> Run(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "dashboard/summary")] HttpRequestData request,
        CancellationToken cancellationToken)
    {
        var summary = await dashboardSummaryProvider.GetSummaryAsync(cancellationToken);
        var response = request.CreateResponse(HttpStatusCode.OK);
        await response.WriteAsJsonAsync(summary, cancellationToken);

        return response;
    }
}

