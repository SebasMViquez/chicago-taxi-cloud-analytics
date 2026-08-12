# Data Pipeline

The processor supports two modes:

- local: local CSV to local `processed/` and `results/`.
- adls: ADLS raw CSV to ADLS processed/results and optional Azure SQL load.

Processing stages:

1. Ingestion
2. Cleaning and validation
3. Feature engineering
4. Aggregation
5. Parquet/JSON output
6. Optional SQL load with `AnalyticsRunId`

Generated analytics:

- `dashboard_summary.parquet`
- `demand_by_hour.parquet`
- `demand_by_day.parquet`
- `demand_by_area.parquet`
- `cost_by_distance.parquet`
- `payment_summary.parquet`
- `monthly_trends.parquet`
- `data_quality_summary.json`

The real dataset is not committed to Git. Store raw, processed and results data in ADLS or local ignored folders.
