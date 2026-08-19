# Phase 22 - Cloud Job Debugging

## Summary

During Phase 22, the first cloud execution of the Azure Container Apps Job exposed two separate issues:

1. The initial execution failed with `OOMKilled`.
2. After increasing Job resources, the Job reached the processor code and failed on timestamp parsing.

The processor fix was made in code, but no commit, push, GHCR rebuild, or Job retry has been executed yet.

## Job Resource Adjustment

The Job resources were increased to:

```text
cpu: 2
memory: 4Gi
ephemeralStorage: 8Gi
```

After this adjustment, the Job no longer failed due to memory and surfaced the real CSV parsing issue.

## Error Evidence

Azure logs showed:

```text
polars.exceptions.ComputeError:
could not parse `"01/31/2023 11:45:00 PM"` as dtype `datetime[us]`
at column 'Trip Start Timestamp'
```

The traceback pointed to:

```text
processing/src/ingestion/csv_reader.py
read_adls_csv()
pl.read_csv(BytesIO(content), try_parse_dates=True, schema_overrides=CHICAGO_TAXI_SCHEMA)
```

## Root Cause

The deployed image still attempted to let Polars parse date columns automatically while reading the ADLS CSV.

The official Chicago Taxi CSV uses AM/PM timestamps such as:

```text
01/31/2023 11:45:00 PM
```

That format was not handled correctly by automatic parsing in the cloud image.

## Code Changes

Updated files:

- `processing/src/ingestion/csv_reader.py`
- `processing/tests/test_processing.py`

The ingestion logic now:

- Reads `Trip Start Timestamp` and `Trip End Timestamp` initially as text.
- Avoids automatic date parsing with `try_parse_dates=True`.
- Converts timestamps explicitly to `pl.Datetime`.
- Supports both known formats:
  - `%Y-%m-%d %H:%M:%S`
  - `%m/%d/%Y %I:%M:%S %p`
- Uses tolerant conversion with `strict=False`, so invalid timestamps become `null`.
- Keeps compatibility with downstream cleaning and transformations, which expect datetime columns.

The existing normalization for real CSV numeric formats is also preserved:

- `Trip Seconds` with thousands separators.
- Monetary columns with `$` and comma thousands separators.

## Test Coverage

Added test:

```text
test_read_adls_csv_parses_city_timestamp_format
```

This test simulates a small ADLS CSV payload in memory with:

```text
01/31/2023 11:45:00 PM
02/01/2023 12:15:00 AM
```

It verifies that both timestamp columns are converted to `Datetime`.

## Validation Commands

Commands executed locally:

```powershell
.\.venv\Scripts\ruff.exe check .
```

Result:

```text
All checks passed!
```

```powershell
.\.venv\Scripts\python.exe -m pytest --basetemp C:\tmp\... -p no:cacheprovider
```

Result:

```text
11 passed in 1.80s
```

## Important Note

The Azure Container Apps Job may still be using an older GHCR image until the fix is committed, pushed, and the processor image is rebuilt/published.

The next cloud retry should only happen after the corrected image is available in GHCR and the Job is confirmed to reference that image.

## Remaining Work

Next controlled steps:

1. Review the code diff.
2. Commit only the approved processor parsing fix and tests.
3. Push to `Integraciones_CLOUD`.
4. Rebuild and publish the processor image to GHCR.
5. Confirm the Container Apps Job uses the updated image.
6. Retry the Container Apps Job in a controlled execution.

No Container Apps Job retry, dataset upload, SQL data load, or Azure configuration change was performed as part of this documentation step.
