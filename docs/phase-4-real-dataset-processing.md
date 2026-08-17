# Phase 4 - Real Dataset Local Processing

## Objective

This phase validated that the Python processor can process the real Chicago Taxi Trips dataset locally before any Azure deployment.

The validated local flow was:

```text
real CSV
  -> ingestion
  -> cleaning
  -> transformations
  -> processed/processed_trips.parquet
  -> results/*.parquet
  -> data_quality_summary.json
```

The execution was completed locally only. No Azure resources, ADLS, Azure SQL, deployments, or cloud services were used.

## Dataset Used

Dataset: Chicago Taxi Trips

Selected period: 2023-01-01 -> 2023-06-30

Local input file:

```text
C:\BigData\ChicagoTaxi\chicago_taxi_2023_01_06.csv
```

Dataset characteristics:

| Metric | Value |
| --- | ---: |
| Rows | 3,235,079 |
| Columns | 23 |
| Size bytes | 1,491,849,671 |
| Size MB | 1,422.74 |
| Size GB | 1.39 |
| SHA-256 | A059A31218EDA8908A8BCDAD67D4092278AD10BFE8B8637D8D6B91D173901E8C |

The dataset remained outside the Git repository and was not modified during Phase 4.

Input file integrity was checked before and after the final execution:

| Property | Value |
| --- | --- |
| Length | 1,491,849,671 bytes |
| LastWriteTime | 2026-08-13 19:25:12 |

Both values remained unchanged after processing.

## Issues Found With The Real Dataset

The development fixture did not fully represent the physical CSV format used by the official City of Chicago export. Two ingestion compatibility issues were discovered and fixed before the final successful run.

## Timestamp Format Issue

The fixture used ISO-like timestamps:

```text
2023-01-03 08:15:00
```

Format:

```text
%Y-%m-%d %H:%M:%S
```

The official dataset used AM/PM timestamps:

```text
01/31/2023 11:45:00 PM
```

Format:

```text
%m/%d/%Y %I:%M:%S %p
```

The first real execution failed with:

```text
polars.exceptions.ComputeError:
could not parse "01/31/2023 11:45:00 PM" as dtype datetime[us]
at column 'Trip Start Timestamp'
```

Root cause: ingestion forced `Trip Start Timestamp` and `Trip End Timestamp` directly to `pl.Datetime` during CSV reading.

Applied solution:

- Read both timestamp columns temporarily as `String`.
- Convert them explicitly after ingestion.
- Support only the two demonstrated formats: fixture ISO-like format and official AM/PM format.
- Convert invalid timestamp values to `null`.
- Leave row validity decisions to the existing cleaning and data quality logic.
- Use the same normalization logic for local CSV and ADLS ingestion paths.

## Numeric And Monetary Format Issue

After resolving timestamps, the next real execution failed with:

```text
polars.exceptions.ComputeError:
could not parse "$35.25" as dtype f64
at column 'Fare'
```

A read-only audit of the full CSV scanned 3,235,079 rows and found physical format incompatibilities only in:

- `Trip Seconds`
- `Fare`
- `Tips`
- `Tolls`
- `Extras`
- `Trip Total`

Demonstrated real formats:

```text
Trip Seconds:
1,389
1,740
1,853

Monetary fields:
$35.25
$45.50
$1,061.24
$4,444.44
$8,888.88
$8,902.63
```

The fixture used plain numeric values:

```text
1200
14.25
2.00
0
1.00
17.25
```

Applied solution:

- `Trip Seconds`: remove only comma thousands separators, then cast to `Int64`.
- Monetary columns: remove only `$` and comma thousands separators, then cast to `Float64`.
- Empty values remain `null`.
- Invalid values become `null`.
- Invalid values are never converted to zero.
- The raw CSV is not altered.
- Cleaning rules were not changed to accommodate the data.

## Validation Of Corrections

Before retrying the real dataset, the corrections were validated with small tests and the existing fixture.

Timestamp correction validation:

| Validation | Result |
| --- | --- |
| Ruff | PASS |
| Pytest | 7 passed, 0 failed |
| Fixture end-to-end input rows | 3 |
| Fixture end-to-end valid rows | 2 |
| Fixture end-to-end invalid rows | 1 |
| Fixture end-to-end | PASS |

Numeric correction validation:

| Validation | Result |
| --- | --- |
| Ruff | PASS |
| Pytest collected | 10 |
| Pytest passed | 10 |
| Pytest failed | 0 |
| Pytest skipped | 0 |
| Fixture end-to-end input rows | 3 |
| Fixture end-to-end accepted rows | 2 |
| Fixture end-to-end rejected rows | 1 |
| Fixture end-to-end | PASS |

The tests covered:

- Fixture timestamp format.
- Official AM/PM timestamp format.
- Invalid timestamp -> `null`.
- Plain `Trip Seconds`.
- `Trip Seconds` with thousands separator.
- Plain monetary values.
- Monetary values with `$`.
- Monetary values with `$` and thousands separator.
- Empty values -> `null`.
- Invalid numeric values -> `null`.
- Final dtypes.
- Existing cleaning behavior for required null fields.

## Final Real Dataset Execution

Output directory:

```text
C:\BigData\ChicagoTaxi\processing-output-2023-01-06-v3
```

Conceptual command:

```powershell
.\.venv\Scripts\python.exe src\main.py `
  --mode local `
  --input "C:\BigData\ChicagoTaxi\chicago_taxi_2023_01_06.csv" `
  --output "C:\BigData\ChicagoTaxi\processing-output-2023-01-06-v3"
```

Execution result:

| Metric | Value |
| --- | --- |
| ExitCode | 0 |
| Elapsed | 00:00:10.1864580 |
| ElapsedSeconds | 10.186458 |

Relevant logs:

```text
stage=cleaning rows_input=3235079
stage=transform rows_output=2885777
Wrote processed output to C:\BigData\ChicagoTaxi\processing-output-2023-01-06-v3\processed\processed_trips.parquet
```

## Data Quality Summary

The generated `data_quality_summary.json` was valid and contained:

| Metric | Value |
| --- | ---: |
| source_rows | 3,235,079 |
| accepted_rows | 2,885,777 |
| rejected_rows | 349,302 |
| duplicate_trip_ids | 0 |
| null_required_field_rows | 4,589 |
| null_pickup_areas | 151,516 |
| null_dropoff_areas | 309,666 |
| zero_distance_trips | 342,436 |
| invalid_duration_rows | 64,384 |
| invalid_distance_rows | 342,436 |
| invalid_fare_rows | 0 |
| negative_total_rows | 0 |

Main consistency check:

```text
2,885,777 + 349,302 = 3,235,079
```

Result: PASS.

The individual data quality metrics may overlap and must not be summed together to calculate `rejected_rows`.

## Processed Parquet

Generated file:

```text
processed/processed_trips.parquet
```

Validation:

| Metric | Value |
| --- | ---: |
| Rows | 2,885,777 |
| Columns | 34 |
| Size bytes | 197,541,799 |
| Size MB | 188.3905 |
| Readable | PASS |

The resulting schema includes normalized original fields and derived features, including:

- `year`
- `month`
- `day`
- `day_of_week`
- `hour`
- `is_weekend`
- `duration_minutes`
- `cost_per_mile`
- `average_speed_mph`
- `tip_percentage`
- `distance_range`

## Generated Results

Generated result files:

| File | Bytes | MB |
| --- | ---: | ---: |
| `cost_by_distance.parquet` | 2,074 | 0.0020 |
| `dashboard_summary.parquet` | 1,574 | 0.0015 |
| `data_quality_summary.json` | 318 | 0.0003 |
| `demand_by_area.parquet` | 3,385 | 0.0032 |
| `demand_by_day.parquet` | 2,095 | 0.0020 |
| `demand_by_hour.parquet` | 1,916 | 0.0018 |
| `monthly_trends.parquet` | 1,958 | 0.0019 |
| `payment_summary.parquet` | 1,709 | 0.0016 |

## Five Analytical Questions

The generated outputs cover the five academic analytical questions:

| Analytical Question | Output | Rows | Columns | Status |
| --- | --- | ---: | ---: | --- |
| Temporal demand | `demand_by_hour.parquet` | 168 | 3 | PASS |
| Temporal demand | `demand_by_day.parquet` | 181 | 2 | PASS |
| Areas with highest activity | `demand_by_area.parquet` | 78 | 4 | PASS |
| Cost vs distance | `cost_by_distance.parquet` | 4 | 5 | PASS |
| Payment methods | `payment_summary.parquet` | 7 | 4 | PASS |
| Temporal trends | `monthly_trends.parquet` | 6 | 5 | PASS |

Auxiliary dashboard output:

| Output | Rows | Columns | Status |
| --- | ---: | ---: | --- |
| `dashboard_summary.parquet` | 1 | 4 | PASS |

All analytical outputs were readable, present, and non-empty.

## Monthly Trends

`monthly_trends.parquet` contains exactly the selected period months:

```text
2023-01
2023-02
2023-03
2023-04
2023-05
2023-06
```

Columns:

- `year`
- `month`
- `trip_count`
- `average_fare`
- `average_trip_miles`

Validation:

| Check | Result |
| --- | --- |
| Six months present | PASS |
| January through June present | PASS |
| July or later absent | PASS |

## Output Sizes

| Output Area | Bytes | MB | GB |
| --- | ---: | ---: | ---: |
| `processed/` | 197,541,799 | 188.3905 | |
| `results/` | 15,029 | 0.0143 | |
| Total | 197,556,828 | 188.4049 | 0.183989 |

## Performance Observation

Input:

| Metric | Value |
| --- | ---: |
| Input bytes | 1,491,849,671 |
| Input size GB | 1.39 |
| Input rows | 3,235,079 |
| ElapsedSeconds | 10.186458 |
| RowsPerSecond | approximately 317,590 |
| MBPerSecond | approximately 139.67 |

This is a single local execution observation, not a formal benchmark. The result should not be automatically extrapolated to Azure.

## Security And Git Policy

Phase 4 respected the repository and cloud safety boundaries:

- The real dataset remained outside the Git repository.
- Generated outputs remained outside the Git repository.
- No Azure services were used.
- No ADLS access was used.
- No Azure SQL access was used.
- No deployment was executed.
- No commit, push, or merge was performed.

Output location:

```text
C:\BigData\ChicagoTaxi\processing-output-2023-01-06-v3
```

Expected Git status after this documentation task:

```text
 M processing/src/ingestion/csv_reader.py
 M processing/src/storage/sql_writer.py
 M processing/tests/test_processing.py
?? docs/dataset.md
?? docs/phase-2-docker-validation.md
?? docs/phase-2-python-validation.md
?? docs/phase-4-real-dataset-processing.md
```

`processing/src/storage/sql_writer.py` is a previous Phase 2 Ruff modernization change and is not part of the Phase 4 ingestion corrections.

## Non-Blocking Warnings

Non-blocking warnings observed during the phase:

- Older permission warnings related to `processing/pytest-cache-files-*` directories.
- Git warnings about possible future LF -> CRLF conversion on modified files.

These warnings did not affect processor exit code, generated outputs, or the final Phase 4 result.

## Checkpoint 4

CHECKPOINT 4 - PASS

Reasons:

- The processor processed 1.39 GB locally.
- 3,235,079 input rows were recognized.
- `processed_trips.parquet` was generated and validated.
- Analytical result files were generated and validated.
- `data_quality_summary.json` was generated and validated.
- The five academic analytical questions are covered.
- January through June 2023 are present in `monthly_trends`.
- The final execution completed with ExitCode 0.
- The input dataset remained intact.
- Dataset and outputs stayed outside Git.
- No Azure services were used.

Conceptual conclusion: the processor is validated locally and can later be considered for cloud execution through Azure Container Apps Job.

This document does not claim that Azure Container Apps execution has already been validated.
