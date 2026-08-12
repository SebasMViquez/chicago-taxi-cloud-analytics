# Database

Azure SQL stores dashboard-ready aggregates, not the full Chicago Taxi Trips dataset.

The full trip-level data belongs in ADLS Gen2 as raw CSV and processed Parquet. The tables in `migrations/001_initial_schema.sql` are intentionally analytical and keyed by `AnalyticsRunId` so processing runs can be audited and compared.

The processor writes aggregate rows for the latest run, and the API reads the most recent completed run. `AnalyticsRuns` records source path and row counts; `DataQualityMetrics` records validation outcomes.

