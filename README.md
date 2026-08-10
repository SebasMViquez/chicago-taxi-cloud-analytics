# Chicago Taxi Cloud Analytics

University big data processing project for the public Chicago Taxi Trips dataset.

The target architecture processes CSV data into Azure Data Lake Storage Gen2, stores processed files as Parquet, writes dashboard-ready aggregates to Azure SQL Database, exposes those aggregates through Azure Functions, and serves a React dashboard through Azure Static Web Apps.

## Dataset

Source: <https://www.kaggle.com/datasets/chicago/chicago-taxi-trips-bq>

The original dataset is CSV and can be very large. Do not commit the full dataset, local extracts, generated Parquet files, or Data Lake outputs.

## Repository structure

```text
apps/web/              React + TypeScript frontend
api/                   Azure Functions isolated worker API
api.Tests/             .NET API tests
processing/            Python processing foundation
database/              Azure SQL analytical schema
infra/bicep/           Initial Infrastructure as Code
docs/                  Architecture documentation
.github/workflows/     Validation-only CI
```

## Local requirements

- .NET SDK 10.0.302
- Node.js 24.10.0 and npm 11.6.1
- Python 3.13 for the processor
- Docker, Azure CLI, Bicep CLI and Azure Functions Core Tools are optional for this first phase

PowerShell may block `npm.ps1`; use `npm.cmd`.

## Run frontend

```powershell
cd apps/web
npm.cmd install
npm.cmd run dev
```

Open <http://localhost:5173/dashboard>.

## Run API

```powershell
dotnet restore
dotnet build
dotnet run --project api/ChicagoTaxi.Api.csproj
```

Azure Functions Core Tools can also be used later if installed. The API currently exposes:

- `GET /api/health`
- `GET /api/dashboard/summary`

## Run processor

```powershell
cd processing
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python src/main.py --input tests/fixtures/chicago_taxi_sample.csv --output .local-output
pytest
```

The included CSV fixture is fictitious and exists only for technical tests.

## Run tests

```powershell
cd apps/web
npm.cmd run lint
npm.cmd run build

cd ../..
dotnet test

cd processing
pytest
```

## Future Azure architecture

```text
Dataset
  -> ADLS Gen2 raw
  -> Azure Container Apps Job
  -> ADLS Gen2 processed/results
  -> Azure SQL Database
  -> Azure Functions API
  -> React / Azure Static Web Apps
```

See `docs/architecture.md` for the Data Lake layout and layer responsibilities.

## Current status

This repository is in phase 1. It contains a professional base architecture and a first vertical slice with development-only responses. It does not deploy Azure resources, process the real dataset, or present mock values as real analytics.

