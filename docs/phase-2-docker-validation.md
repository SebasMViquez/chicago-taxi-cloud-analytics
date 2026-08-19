# Phase 2 - Docker Processor Validation

## Objective

The objective of this validation was to confirm that the Python processor previously validated locally can also be built and executed inside a Linux container, while producing results equivalent to the local Python execution.

This validation was completed before moving toward Azure Container Apps.

## Docker Environment

- Docker version: 29.7.2
- Docker context: `desktop-linux`
- Base image: `python:3.13-slim`
- Built image: `chicago-taxi-processing`
- OS: linux
- Architecture: amd64
- ENTRYPOINT: `python src/main.py`

## Dockerfile Validation

The Dockerfile was inspected and validated without modification:

- `WORKDIR` is `/app`.
- `pyproject.toml` is copied into the image.
- `README.md` is copied into the image.
- `src/` is copied into the image.
- Dependencies are installed with `pip install --no-cache-dir .`.
- `tests/` is not included in the image because it is excluded by `.dockerignore`.
- The fixture was provided through a bind mount.
- The container currently uses the default user from the base image.

## Docker Build Validation

Build command:

```powershell
docker build -t chicago-taxi-processing processing
```

Result: PASS

- BuildKit completed 11/11 steps.
- Observed duration: approximately 49.8 seconds.

The observed duration is environment-specific and should not be treated as an expected constant for future builds.

## Local Bind Mount Strategy

The fixture was not baked into the Docker image. Instead, the container was tested with bind mounts:

- Host fixture: `processing/tests/fixtures/chicago_taxi_sample.csv`
- Container input: `/data/input/chicago_taxi_sample.csv`
- Fixture mount mode: read-only
- Host output: `processing/.local-output-docker/`
- Container output: `/data/output`

This approach validates the same runtime image while keeping test datasets out of the image and preserving the production-oriented `.dockerignore` behavior.

## Container Execution

The container execution was conceptually equivalent to:

```powershell
docker run --rm `
  [input bind mount] `
  [output bind mount] `
  chicago-taxi-processing `
  --mode local `
  --input /data/input/chicago_taxi_sample.csv `
  --output /data/output
```

Observed result:

- Input rows: 3
- Output/accepted rows: 2
- Rejected rows: 1

Observed logs:

```text
stage=cleaning rows_input=3
stage=transform rows_output=2
```

`processed_trips.parquet` was written successfully to the mounted output directory.

## Generated Outputs

Docker generated outputs under:

```text
processing/.local-output-docker/
  processed/
    processed_trips.parquet
  results/
    cost_by_distance.parquet
    dashboard_summary.parquet
    data_quality_summary.json
    demand_by_area.parquet
    demand_by_day.parquet
    demand_by_hour.parquet
    monthly_trends.parquet
    payment_summary.parquet
```

## Parquet Validation

The Docker-generated Parquet files were opened and validated with the local Python environment.

Processed output:

- `processed_trips.parquet`: 2 rows, 30 columns, VALID

Analytics outputs:

- `cost_by_distance.parquet`: 2 rows, 5 columns, VALID
- `dashboard_summary.parquet`: 1 row, 4 columns, VALID
- `demand_by_area.parquet`: 2 rows, 4 columns, VALID
- `demand_by_day.parquet`: 1 row, 2 columns, VALID
- `demand_by_hour.parquet`: 2 rows, 3 columns, VALID
- `monthly_trends.parquet`: 1 row, 5 columns, VALID
- `payment_summary.parquet`: 2 rows, 4 columns, VALID

All files were opened and validated. Validation did not rely only on file existence.

## Data Quality Validation

The Docker-generated `data_quality_summary.json` was opened and validated.

Key metrics:

- `source_rows`: 3
- `accepted_rows`: 2
- `rejected_rows`: 1

The complete JSON structure was also validated. These numbers come only from the fictitious technical fixture.

## Local Python vs Docker Equivalence

Docker outputs from:

`processing/.local-output-docker/`

were semantically compared with the local Python outputs from:

`processing/.local-output/`

The comparison checked:

- Row counts
- Column counts
- Schemas
- Values
- Analytics aggregates
- Data quality metrics

Result: MATCH for all outputs.

Exact binary comparison of Parquet files was not used because Parquet metadata can differ while the data remains semantically equivalent.

## Git Safety

`processing/.local-output-docker/` was confirmed to be ignored by Git through existing ignore rules, including:

- `processed/`
- `results/`
- `*.parquet`

The Docker outputs did not appear as tracked or untracked changes in `git status`.

`.gitignore` was not modified.

## Codex Sandbox Limitation

Docker CLI became visible from Codex after the environment was restarted, but the Codex sandbox did not have permission to access the Docker Desktop Linux Engine named pipe:

```text
npipe:////./pipe/dockerDesktopLinuxEngine
```

Because of that sandbox limitation:

- `docker build` and `docker run` were executed from the user's normal PowerShell session.
- Codex then performed a read-only validation of the generated outputs.
- Docker Desktop itself was operational.

This was a Codex sandbox limitation, not a Dockerfile issue, processor issue, production limitation, or Azure limitation.

## Container Cleanup

The container was executed with:

```text
--rm
```

The later check:

```powershell
docker ps -a --filter "ancestor=chicago-taxi-processing"
```

did not show persistent test containers.

The local image was intentionally retained:

```text
chicago-taxi-processing
```

## Important Limitation

The dataset used in this validation is a fictitious technical fixture. The generated metrics must not be interpreted as real Chicago Taxi Trips analytical results.

## Final Status

Phase 2.3 Docker Processor Validation: PASS
