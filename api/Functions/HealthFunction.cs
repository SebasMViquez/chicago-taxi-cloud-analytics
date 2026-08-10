using System.Net;
using ChicagoTaxi.Api.Models;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Azure.Functions.Worker.Http;

namespace ChicagoTaxi.Api.Functions;

public sealed class HealthFunction
{
    [Function("Health")]
    public async Task<HttpResponseData> Run(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "health")] HttpRequestData request)
    {
        var response = request.CreateResponse(HttpStatusCode.OK);
        await response.WriteAsJsonAsync(
            new HealthResponse("Healthy", "ChicagoTaxi.Api", DateTimeOffset.UtcNow));

        return response;
    }
}

