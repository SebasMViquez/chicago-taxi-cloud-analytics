# Chicago Taxi Processing

Processor for the Chicago Taxi Trips analytics pipeline.

It supports local CSV processing and Azure Data Lake Storage Gen2 processing with Managed Identity. The included fixture is still tiny and fictitious; the real Kaggle dataset must be downloaded and uploaded externally.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python src/main.py --mode local --input tests/fixtures/chicago_taxi_sample.csv --output .local-output
pytest
```

Outputs under `.local-output` are local development artifacts and must not be committed.

## Run in Azure Container Apps Job

The Docker image reads runtime configuration from environment variables:

- `PROCESSING_MODE=adls`
- `PROCESSING_INPUT_PATH=raw/chicago-taxi/2023/taxi_trips.csv`
- `PROCESSING_PROCESSED_PATH=processed/chicago-taxi/year=2023/processed_trips.parquet`
- `PROCESSING_RESULTS_PREFIX=results/chicago-taxi/latest`
- `PROCESSING_LOAD_SQL=true`
- `AZURE_STORAGE_ACCOUNT_NAME`
- `AZURE_STORAGE_CONTAINER_NAME=chicago-taxi`
- `SQL_SERVER_NAME`
- `SQL_DATABASE_NAME`
- `SQL_AUTH_MODE=ManagedIdentity`

