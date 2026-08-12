using ChicagoTaxi.Api.Application;
using ChicagoTaxi.Api.Infrastructure;
using Microsoft.Azure.Functions.Worker.Builder;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

var builder = FunctionsApplication.CreateBuilder(args);

builder.ConfigureFunctionsWebApplication();

var dashboardProvider = builder.Configuration["DASHBOARD_SUMMARY_PROVIDER"];
if (string.Equals(dashboardProvider, "Development", StringComparison.OrdinalIgnoreCase))
{
    builder.Services.AddScoped<IDashboardSummaryProvider, DevelopmentDashboardSummaryProvider>();
    builder.Services.AddScoped<IAnalyticsRepository, DevelopmentAnalyticsRepository>();
}
else
{
    builder.Services.AddScoped<IAnalyticsRepository, SqlAnalyticsRepository>();
    builder.Services.AddScoped<IDashboardSummaryProvider, SqlDashboardSummaryProvider>();
}

builder.Build().Run();
