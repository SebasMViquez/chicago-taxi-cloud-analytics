using ChicagoTaxi.Api.Application;
using ChicagoTaxi.Api.Infrastructure;
using Microsoft.Azure.Functions.Worker.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

var builder = FunctionsApplication.CreateBuilder(args);

builder.ConfigureFunctionsWebApplication();

builder.Services.AddScoped<IDashboardSummaryProvider, DevelopmentDashboardSummaryProvider>();

builder.Build().Run();
