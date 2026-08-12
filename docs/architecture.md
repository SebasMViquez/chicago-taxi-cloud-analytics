# Architecture

```mermaid
flowchart LR
    Dataset[Chicago Taxi Trips CSV] --> Raw[ADLS Gen2 raw]
    Raw --> Job[Azure Container Apps Job]
    Job --> Processed[ADLS Gen2 processed Parquet]
    Job --> Results[ADLS Gen2 results]
    Job --> SQL[Azure SQL analytical aggregates]
    SQL --> API[Azure Functions API]
    API --> Web[React / Azure Static Web Apps]
```

## Layers

- Dataset: public Chicago Taxi Trips CSV from Kaggle. The full dataset is never committed to Git.
- ADLS Raw: immutable source files organized by dataset and year.
- Container Apps Job: Python, Polars, PyArrow, Azure Identity and ODBC SQL writer.
- ADLS Processed: cleaned and enriched Parquet.
- ADLS Results: aggregate Parquet and data quality summary JSON.
- Azure SQL: dashboard-ready aggregates keyed by `AnalyticsRunId`.
- Azure Functions API: stable HTTP contracts for the frontend.
- React / Static Web Apps: user interface; it never connects directly to Azure SQL.

## Data Lake layout

```text
raw/
  chicago-taxi/
    2023/
      taxi_trips.csv

processed/
  chicago-taxi/
    year=2023/
      processed_trips.parquet

results/
  chicago-taxi/
    latest/
      dashboard_summary.parquet
      demand_by_hour.parquet
      demand_by_day.parquet
      demand_by_area.parquet
      payment_summary.parquet
      monthly_trends.parquet
      cost_by_distance.parquet
      data_quality_summary.json
```

## Security posture

The Azure implementation uses Managed Identity and RBAC for application workloads. Secrets, connection strings, storage keys, datasets, CSV exports and Parquet outputs must not be committed.
