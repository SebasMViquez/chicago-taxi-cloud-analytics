# Phase 23 - Cloud Execution Logs

## Objective

Phase 23 documented the logs and troubleshooting evidence from the first successful cloud processing execution.

The original guide expected log review through Azure Container Apps Job execution history. In this project, the final successful batch execution was completed with Azure Container Instances, so the final evidence comes from ACI container logs and SQL/ADLS validation.

## Runtime Context

| Property | Value |
|---|---|
| Final runtime | Azure Container Instances |
| Container name | `aci-chicago-taxi-processor-full-dev` |
| Resource group | `rg-chicago-taxi-dev` |
| Region | `centralus` |
| Image | `ghcr.io/sebasmviquez/chicago-taxi-cloud-analytics/chicago-taxi-processing:latest` |
| Commit/version | `6e762bb` |
| Restart policy | `Never` |
| Final state | `Terminated / Succeeded` |
| Exit code | `0` |

## Original Log Source Expected

The original plan expected logs from Azure Container Apps Job, normally reviewed through:

```bash
az containerapp job execution list
az containerapp job execution show
az containerapp job logs show
```

That path was useful during troubleshooting, but it was not the final successful runtime because the Container Apps Environment was Consumption-only and could not provide enough resources for the full dataset workload under the available subscription/environment limits.

## Final Log Source Used

The final successful execution used Azure Container Instances. Logs were reviewed from the ACI container execution after the batch run completed.

Conceptual log retrieval:

```bash
az container logs \
  --resource-group rg-chicago-taxi-dev \
  --name aci-chicago-taxi-processor-full-dev
```

No secrets are required in the documentation and no credential values should be copied into logs or Markdown files.

## Final Log Evidence

The successful execution produced the following key log lines:

```text
stage=sql_load run_id=7 status=completed
Wrote processed output to processed/chicago-taxi/full/processed_trips_2023_01_06_aci_floatfix.parquet
```

These lines confirm that:

- the processor completed the SQL load step;
- SQL run id `7` was completed;
- the processed Parquet output was written to ADLS;
- the container reached normal completion.

## SQL Validation Evidence

The SQL validation for `AnalyticsRunId = 7` confirmed the completed processing run.

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

## ADLS Validation Evidence

Processed file:

```text
processed/chicago-taxi/full/processed_trips_2023_01_06_aci_floatfix.parquet
```

Size:

```text
191,027,087 bytes
```

Generated results:

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

## Troubleshooting Categories

| Category | Resolution / Outcome |
|---|---|
| GHCR image pull and registry validation | The processor image was published and pulled from GHCR successfully. |
| ADLS access through managed identity | ACI used managed identity for ADLS access. |
| SQL firewall and client IP changes | SQL firewall rules and Azure services access were adjusted during the phase. |
| SQL authentication | SQL password authentication mode was added for the processor. |
| SQL schema issue | `PickupCommunityArea` needed to allow `NULL` values instead of being blocked by the original key design. |
| SQL float values | Invalid floating-point values such as `NaN` and `Infinity` were cleaned before SQL inserts. |
| Container Apps Consumption limits | The Container Apps Job path was constrained by the Consumption-only environment. |
| Final batch runtime | Azure Container Instances was used as the successful batch runtime. |

## Final Status

**Phase 23 result: PASS**

The final cloud logs, SQL validation, and ADLS output validation confirm that the full dataset processing completed successfully through Azure Container Instances.

