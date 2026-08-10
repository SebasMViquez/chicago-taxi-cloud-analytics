# Database

Azure SQL stores dashboard-ready aggregates, not the full Chicago Taxi Trips dataset.

The full trip-level data belongs in ADLS Gen2 as raw CSV and processed Parquet. The tables in `migrations/001_initial_schema.sql` are intentionally analytical and keyed by `AnalyticsRunId` so future processing runs can be audited and compared.

Only one supporting index is included initially: `IX_AnalyticsRuns_Status_StartedAtUtc`, for locating recent completed runs. Additional indexes should be added after query patterns are known.

