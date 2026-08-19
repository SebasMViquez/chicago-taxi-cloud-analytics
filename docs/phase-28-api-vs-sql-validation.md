# Phase 28 - API vs SQL Validation

## Objective

Phase 28 validated that the deployed Azure Functions API returns the same analytics data stored in Azure SQL for the final full processing run.

The validation focused on comparing API responses against SQL results from:

```text
AnalyticsRunId = 7
```

## Environment

| Item | Value |
|---|---|
| Function App | `func-chicago-taxi-flex-dev-73e29256` |
| Resource group | `rg-chicago-taxi-dev` |
| API base URL | `https://func-chicago-taxi-flex-dev-73e29256.azurewebsites.net/api` |
| SQL server | `sql-chicago-taxi-dev-cu-73e29256` |
| SQL database | `ChicagoTaxiAnalytics` |
| Final analytics run | `AnalyticsRunId = 7` |

No secrets, passwords, connection strings, or local environment values are documented here.

## SQL Baseline

Baseline query concept:

```sql
SELECT AnalyticsRunId, DayOfWeek, HourOfDay, TripCount
FROM dbo.TripDemandByHour
WHERE AnalyticsRunId = 7
  AND DayOfWeek = 4
  AND HourOfDay = 17;
```

SQL result:

| AnalyticsRunId | DayOfWeek | HourOfDay | TripCount |
|---:|---:|---:|---:|
| 7 | 4 | 17 | 34,200 |

## API Baseline Validation

Endpoint:

```http
GET /api/analytics/demand/hourly
```

The API returned HTTP 200 and included the same data:

| Field | Value |
|---|---:|
| DayOfWeek | 4 |
| HourOfDay | 17 |
| TripCount | 34,200 |

This confirms that the API response matched the SQL baseline for the sampled demand-by-hour record.

## Endpoint Validation Results

| Endpoint | Result |
|---|---|
| `GET /api/health` | HTTP 200 |
| `GET /api/dashboard/summary` | HTTP 200 |
| `GET /api/analytics/demand/hourly` | HTTP 200 |
| `GET /api/analytics/areas` | HTTP 200 after fix |
| `GET /api/analytics/payment-types` | HTTP 200 |
| `GET /api/data-quality` | HTTP 200 |
| `GET /api/analytics/cost-distance` | HTTP 200 |
| `GET /api/analytics/trends/monthly` | HTTP 200 |

## Areas Endpoint Issue

During Phase 28, the endpoint:

```http
GET /api/analytics/areas
```

initially returned HTTP 500.

SQL evidence showed that `dbo.TripDemandByPickupArea` contained one expected row where:

```text
PickupCommunityArea = NULL
```

This row represents real Chicago Taxi Trips data where the pickup community area was missing.

The row included:

| Field | Value |
|---|---:|
| PickupCommunityArea | NULL |
| TripCount | 123,357 |
| AverageFare | 31.79 |
| AverageTripMiles | 10.82 |

## Root Cause

The API model and SQL mapper originally assumed that pickup community area was always present:

```csharp
int PickupCommunityArea
reader.GetInt32(0)
```

When SQL returned `NULL`, `reader.GetInt32(0)` failed and caused the endpoint to return HTTP 500.

## Code Fix Summary

The API was updated to support missing pickup community areas safely.

| File | Change |
|---|---|
| `api/Models/AnalyticsResponses.cs` | `AreaAnalyticsPoint.PickupCommunityArea` changed from `int` to `int?`. |
| `api/Infrastructure/SqlAnalyticsRepository.cs` | `GetAreasAsync` now uses `GetNullableInt32(reader, 0)`. |
| `api/Infrastructure/SqlAnalyticsRepository.cs` | Added helper `GetNullableInt32(...)`. |
| `api.Tests/AreaAnalyticsPointTests.cs` | Added test proving `PickupCommunityArea = null` is supported and serialized. |

The API now returns missing pickup areas as JSON `null` instead of failing.

Expected JSON behavior:

```json
"PickupCommunityArea": null
```

## Build, Test, and Publish Validation

Validation after the fix:

| Step | Result |
|---|---|
| `dotnet restore` | Passed |
| `dotnet build .\ChicagoTaxiCloudAnalytics.sln -c Release` | Passed |
| `dotnet test .\ChicagoTaxiCloudAnalytics.sln -c Release` | Passed |
| Azure Functions publish | Completed successfully |

Test result:

| Metric | Value |
|---|---:|
| Total | 2 |
| Succeeded | 2 |
| Failed | 0 |

## Final Areas Endpoint Result

After the fix and publish, the endpoint:

```http
GET /api/analytics/areas
```

returned HTTP 200.

The response included the missing-area row:

```json
{
  "PickupCommunityArea": null,
  "TripCount": 123357,
  "AverageFare": 31.79,
  "AverageTripMiles": 10.82
}
```

## Frontend Note

Frontend code should treat `PickupCommunityArea` as nullable for the areas chart or table.

Recommended handling:

- display missing pickup community areas as `Unknown`, `Missing`, or a similar label;
- do not assume every areas record has a numeric community area id;
- preserve the row because it represents real source-data quality from the Chicago Taxi Trips dataset.

## Final Status

**Phase 28 result: PASS**

The Azure Functions API now returns SQL-backed analytics consistently, the areas endpoint handles `NULL` pickup community areas safely, and all validated HTTP endpoints returned HTTP 200.

