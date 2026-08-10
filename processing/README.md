# Chicago Taxi Processing

Local foundation for the future Azure Container Apps Job.

This phase only supports a tiny local CSV used for technical tests. It does not download or process the real Kaggle dataset.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python src/main.py --input tests/fixtures/chicago_taxi_sample.csv --output .local-output
pytest
```

Outputs under `.local-output` are local development artifacts and must not be committed.

