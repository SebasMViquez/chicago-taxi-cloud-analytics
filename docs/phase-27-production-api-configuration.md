# Phase 27 - Production API Configuration

## Objective

Phase 27 validated that the deployed Azure Functions API is configured for production-like access to real analytics data stored in Azure SQL.

The goal was to confirm that the API is not using development, mock, or sample data providers in Azure. Instead, the deployed Function App reads the completed analytics results from the `ChicagoTaxiAnalytics` database.

## Function App

| Setting | Value |
|---|---|
| Function App | `func-chicago-taxi-flex-dev-73e29256` |
| Resource group | `rg-chicago-taxi-dev` |
| Runtime | .NET 10 isolated |
| Hosting | Azure Functions Flex Consumption |

## Production App Settings

The following production app settings were validated:

| App setting | Value |
|---|---|
| `SQL_SERVER_NAME` | `sql-chicago-taxi-dev-cu-73e29256` |
| `SQL_DATABASE_NAME` | `ChicagoTaxiAnalytics` |
| `SQL_AUTH_MODE` | `ManagedIdentity` |
| `DASHBOARD_SUMMARY_PROVIDER` | `Sql` |

No SQL passwords or connection strings are documented in the repository.

## Provider Selection

The API uses development providers only when:

```text
DASHBOARD_SUMMARY_PROVIDER=Development
```

In Azure, the value is explicitly configured as:

```text
DASHBOARD_SUMMARY_PROVIDER=Sql
```

Therefore, the deployed API uses the SQL-backed providers:

| Component | Provider used in Azure |
|---|---|
| Analytics repository | `SqlAnalyticsRepository` |
| Dashboard summary provider | `SqlDashboardSummaryProvider` |

This confirms that the deployed API reads real analytical outputs from Azure SQL instead of local development/sample data.

## Managed Identity SQL Access

The deployed Function App uses:

```text
SQL_AUTH_MODE=ManagedIdentity
```

The Function App managed identity has read access to the `ChicagoTaxiAnalytics` database. This allows the API to query completed analytics results without storing SQL passwords in application settings or source-controlled files.

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
{"Status":"Healthy","Service":"ChicagoTaxi.Api"}
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

This response confirms that the API can read the completed run `7` analytics from Azure SQL.

## Operational Note

A temporary HTTP 500 occurred immediately after restarting the Function App. This was likely caused by the serverless host still initializing. Subsequent requests returned HTTP 200 successfully.

## Frontend Integration

Frontend applications should use this API base URL:

```text
https://func-chicago-taxi-flex-dev-73e29256.azurewebsites.net/api
```

Example environment variable:

```text
VITE_API_BASE_URL=https://func-chicago-taxi-flex-dev-73e29256.azurewebsites.net/api
```

## Final Status

**Phase 27 result: PASS**

The Azure Functions API is configured to use SQL-backed providers, authenticates to Azure SQL through managed identity, and returns real analytics data from the completed cloud processing run.

