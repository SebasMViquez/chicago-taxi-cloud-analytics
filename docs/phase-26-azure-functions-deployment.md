# Phase 26 - Azure Functions Deployment

## Objective

Phase 26 deployed and validated the HTTP API for the Chicago Taxi Cloud Analytics project on Azure Functions.

The objective was to publish the .NET isolated Azure Functions API, connect it to the `ChicagoTaxiAnalytics` Azure SQL database through managed identity, validate the HTTP endpoints, and provide the final API base URL for frontend integration.

## Local Validation Before Deployment

Before the cloud deployment, the API was validated locally.

| Validation | Result |
|---|---|
| `dotnet restore` | Succeeded |
| `dotnet build --configuration Release` | Succeeded |
| `dotnet test` | Succeeded |

These checks confirmed that dependencies restored correctly, the Release build compiled, and the test suite passed before publishing the API.

## Original Function App Issue

The original Function App created by infrastructure was:

```text
func-chicago-taxi-dev-73e29256
```

It was running on the classic Linux Consumption plan:

| Setting | Value |
|---|---|
| SKU | `Y1 / Dynamic` |
| Runtime | `DOTNET-ISOLATED|10.0` |

The API package was uploaded successfully to this Function App, but trigger sync failed. The app returned:

```text
503 Service Unavailable
```

The function list command also failed with:

```text
Bad Request
```

Because the project uses .NET 10 isolated on Linux, the deployment was moved to a new Flex Consumption Function App.

## Flex Consumption Function App

Final successful Function App:

| Setting | Value |
|---|---|
| Name | `func-chicago-taxi-flex-dev-73e29256` |
| Resource group | `rg-chicago-taxi-dev` |
| Region | Central US |
| Hosting plan | Flex Consumption |
| Runtime | `dotnet-isolated` |
| Runtime version | `10.0` |
| Managed Identity | System assigned enabled |
| API SQL authentication mode | ManagedIdentity |
| SQL server | `sql-chicago-taxi-dev-cu-73e29256` |
| SQL database | `ChicagoTaxiAnalytics` |

The Flex Consumption deployment completed successfully, trigger sync completed successfully, and the Function host status was:

```text
Running
```

## Managed Identity and SQL Permissions

A database user was created for the Function App system-assigned managed identity:

```text
func-chicago-taxi-flex-dev-73e29256
```

The identity was granted:

```text
db_datareader
```

This gives the API read-only access to the analytical tables in `ChicagoTaxiAnalytics`.

## Published HTTP Functions

The Flex Consumption Function App published the following HTTP-triggered functions.

| Function | Endpoint |
|---|---|
| Areas | `https://func-chicago-taxi-flex-dev-73e29256.azurewebsites.net/api/analytics/areas` |
| CostDistance | `https://func-chicago-taxi-flex-dev-73e29256.azurewebsites.net/api/analytics/cost-distance` |
| DashboardSummary | `https://func-chicago-taxi-flex-dev-73e29256.azurewebsites.net/api/dashboard/summary` |
| DataQuality | `https://func-chicago-taxi-flex-dev-73e29256.azurewebsites.net/api/data-quality` |
| DemandByHour | `https://func-chicago-taxi-flex-dev-73e29256.azurewebsites.net/api/analytics/demand/hourly` |
| Health | `https://func-chicago-taxi-flex-dev-73e29256.azurewebsites.net/api/health` |
| MonthlyTrends | `https://func-chicago-taxi-flex-dev-73e29256.azurewebsites.net/api/analytics/trends/monthly` |
| PaymentTypes | `https://func-chicago-taxi-flex-dev-73e29256.azurewebsites.net/api/analytics/payment-types` |

## Health Endpoint Validation

Request:

```http
GET https://func-chicago-taxi-flex-dev-73e29256.azurewebsites.net/api/health
```

Response:

```text
StatusCode: 200
```

```json
{"Status":"Healthy","Service":"ChicagoTaxi.Api","CheckedAtUtc":"2026-08-17T06:48:03.9158136+00:00"}
```

## Dashboard Summary Validation

Request:

```http
GET https://func-chicago-taxi-flex-dev-73e29256.azurewebsites.net/api/dashboard/summary
```

Response:

```text
StatusCode: 200
```

```json
{"Status":"READY","Message":"Showing analytics from completed run 7.","TotalTrips":2885777,"AverageFare":22.724878,"AverageMiles":7.237749,"AverageDurationMinutes":21.861388}
```

This confirms that the API can read the completed analytics run from Azure SQL through managed identity.

## Frontend Integration Guide

Frontend applications should use the Flex Consumption Function App as the API base URL:

```text
https://func-chicago-taxi-flex-dev-73e29256.azurewebsites.net/api
```

Example environment variable:

```text
VITE_API_BASE_URL=https://func-chicago-taxi-flex-dev-73e29256.azurewebsites.net/api
```

The old Function App should not be used for frontend integration:

```text
func-chicago-taxi-dev-73e29256
```

That app was hosted on the classic Linux Consumption plan and returned `503 Service Unavailable` after deployment. The working API is:

```text
func-chicago-taxi-flex-dev-73e29256
```

## Final Status

**Phase 26 result: PASS**

The API was successfully deployed to Azure Functions Flex Consumption, trigger sync completed, the Function host was running, SQL access through managed identity worked, and the health/dashboard endpoints returned HTTP 200 responses.

