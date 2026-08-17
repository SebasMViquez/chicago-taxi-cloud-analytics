# Phase 22 - First Cloud Execution

## Objective

Phase 22 validated the first full cloud execution of the Chicago Taxi Trips processor against the real 2023 January-June dataset.

The objective was to run the processor in Azure, read the input CSV from Azure Data Lake Storage, write the processed Parquet and analytical results back to ADLS, and load the aggregate results into Azure SQL.

## Original Expected Approach

The original plan was to execute the workload through Azure Container Apps Job, either from the Azure Portal with **Run now** or through:

```bash
az containerapp job start
```

The Container Apps Job was expected to run the published GHCR image and process:

```text
raw/chicago-taxi/2023/chicago_taxi_2023_01_06.csv
```

## Issues Encountered

During implementation, the Container Apps Job path exposed several infrastructure and runtime constraints.

| Issue | Result |
|---|---|
| Existing Container Apps Environment was Consumption-only | The job was limited by the Consumption profile resources. |
| Consumption resources were not enough for full dataset processing | The full processing workload exceeded the available capacity. |
| Attempts to use a workload profile or dedicated environment were blocked | Subscription/environment limits prevented using the desired higher-resource Container Apps profile. |
| SQL connectivity and authentication required additional corrections | The processor and database access path required fixes before a successful end-to-end cloud run. |

Because of these constraints, the successful Phase 22 execution was completed using Azure Container Instances as a batch execution alternative.

## Final Execution Runtime

| Property | Value |
|---|---|
| Runtime | Azure Container Instances |
| Container name | `aci-chicago-taxi-processor-full-dev` |
| Resource group | `rg-chicago-taxi-dev` |
| Region | `centralus` |
| Image | `ghcr.io/sebasmviquez/chicago-taxi-cloud-analytics/chicago-taxi-processing:latest` |
| Commit/version used | `6e762bb` |
| CPU / memory | 4 CPU / 16 GB |
| Restart policy | `Never` |
| SQL load | Enabled |
| SQL database | `ChicagoTaxiAnalytics` |
| Final state | `Terminated / Succeeded` |
| Exit code | `0` |

## Input and Output Configuration

| Item | Path |
|---|---|
| Input CSV | `raw/chicago-taxi/2023/chicago_taxi_2023_01_06.csv` |
| Processed output | `processed/chicago-taxi/full/processed_trips_2023_01_06_aci_floatfix.parquet` |
| Results prefix | `results/chicago-taxi/full-2023-01-06-aci-floatfix` |

## Execution Evidence

The final container execution completed successfully.

Conceptual ACI execution pattern:

```bash
az container create \
  --resource-group rg-chicago-taxi-dev \
  --name aci-chicago-taxi-processor-full-dev \
  --image ghcr.io/sebasmviquez/chicago-taxi-cloud-analytics/chicago-taxi-processing:latest \
  --cpu 4 \
  --memory 16 \
  --restart-policy Never
```

Runtime parameters and environment values were configured without documenting secrets in the repository.

Relevant log evidence:

```text
stage=sql_load run_id=7 status=completed
Wrote processed output to processed/chicago-taxi/full/processed_trips_2023_01_06_aci_floatfix.parquet
```

Final SQL run id:

```text
7
```

## SQL Validation

The final SQL load was validated against `AnalyticsRunId = 7`.

| Metric | Value |
|---|---:|
| AnalyticsRunId | 7 |
| Status | Completed |
| TotalRows | 3,235,079 |
| ValidRows | 2,885,777 |
| InvalidRows | 349,302 |

Aggregation table counts for `AnalyticsRunId = 7`:

| Table | Rows |
|---|---:|
| TripDemandByHour | 168 |
| TripDemandByDay | 181 |
| TripDemandByPickupArea | 78 |
| TripCostByDistanceRange | 4 |
| PaymentTypeSummary | 7 |
| MonthlyTripTrend | 6 |
| DataQualityMetrics | 1 |

## ADLS Validation

The processed full dataset was written to ADLS:

```text
processed/chicago-taxi/full/processed_trips_2023_01_06_aci_floatfix.parquet
```

Size:

```text
191,027,087 bytes
```

Generated analytical result files:

| Result file |
|---|
| `cost_by_distance.parquet` |
| `dashboard_summary.parquet` |
| `data_quality_summary.json` |
| `demand_by_area.parquet` |
| `demand_by_day.parquet` |
| `demand_by_hour.parquet` |
| `monthly_trends.parquet` |
| `payment_summary.parquet` |

## Fixes Completed During Phase 22

The following fixes were completed before the successful cloud execution:

- Added SQL password authentication support for the processor.
- Adjusted the SQL schema because `PickupCommunityArea` can contain `NULL` values and the original primary key design prevented nulls.
- Cleaned invalid floating-point values such as `NaN` and `Infinity` before SQL inserts.
- Added Azure SQL firewall rules and allowed Azure services/resources.
- Used Azure Container Instances managed identity for ADLS access.

## Final Result

**Phase 22 completed successfully.**

The real Chicago Taxi Trips dataset was processed in Azure using Azure Container Instances, outputs were written to ADLS, and analytical aggregates were loaded into Azure SQL with `AnalyticsRunId = 7`.

## Future Improvement

Azure Container Apps Job can be revisited later if the project moves to a dedicated workload profile or another higher-resource plan that supports the memory and CPU requirements of the full dataset workload.
