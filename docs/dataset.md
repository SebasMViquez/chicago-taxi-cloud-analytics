# Dataset

## 1. Dataset

The dataset selected for the project is **Chicago Taxi Trips**.

The working academic file is a consolidated CSV containing taxi trip records for the first six months of 2023.

## 2. Source

- Source: City of Chicago Data Portal
- View used: Taxi Trips - 2023

## 3. Selected Period

Detailed period:

- Start: `2023-01-01 00:00:00`
- End: `2023-06-30 23:45:00`

Academic summary period:

- `2023-01-01` to `2023-06-30`

## 4. Subset Justification

The complete historical Chicago Taxi Trips dataset is not used in this academic project.

Instead, the selected subset covers January through June 2023. This period was chosen because the academic requirement was to work with a CSV between 100 MB and 2 GB, and the consolidated file size is 1.39 GB, which satisfies that criterion.

Using six months of data also supports temporal trend analysis while still allowing the project to analyze demand, pickup areas, cost/distance behavior, and payment methods.

## 5. Monthly Source Files

The dataset was initially downloaded as six monthly CSV files:

| Month | File | Size |
|---|---|---:|
| January | `chicago_taxi_2023_01.csv` | 180.38 MB |
| February | `chicago_taxi_2023_02.csv` | 195.23 MB |
| March | `chicago_taxi_2023_03.csv` | 256.76 MB |
| April | `chicago_taxi_2023_04.csv` | 251.01 MB |
| May | `chicago_taxi_2023_05.csv` | 262.04 MB |
| June | `chicago_taxi_2023_06.csv` | 277.32 MB |
| Total | Consolidated period | 1422.74 MB / 1.39 GB |

All six monthly files had exactly the same header.

All six monthly files ended correctly with LF before consolidation.

The monthly files were consolidated into one CSV while keeping a single header.

## 6. Definitive File

- File name: `chicago_taxi_2023_01_06.csv`
- Local development location: `C:\BigData\ChicagoTaxi\chicago_taxi_2023_01_06.csv`
- Preparation date: `2026-08-13`

The local path is documented only as a development reference. The file is not stored in the Git repository.

## 7. Size

- Bytes: `1,491,849,671`
- Megabytes: `1,422.74 MB`
- Gigabytes: `1.39 GB`

## 8. Rows and Columns

- Data rows: `3,235,079`
- Columns: `23`
- Header columns: `23`

## 9. Validations Performed

Structural validation:

| Check | Result |
|---|---:|
| HeaderColumns | 23 |
| BadColumnRows | 0 |
| DateParseErrors | 0 |
| MinTripStart | `2023-01-01 00:00:00` |
| MaxTripStart | `2023-06-30 23:45:00` |
| StructurePASS | True |
| DateRangePASS | True |
| OverallValidation | True |

## 10. SHA-256

- Algorithm: SHA256
- SHA-256: `A059A31218EDA8908A8BCDAD67D4092278AD10BFE8B8637D8D6B91D173901E8C`

## 11. Location and Git Policy

The definitive CSV is stored locally outside the repository:

```text
C:\BigData\ChicagoTaxi\chicago_taxi_2023_01_06.csv
```

The real dataset must remain outside Git. It must not be copied into the repository, committed, or pushed.

Generated raw, processed, and result data should also remain outside Git or in ignored local output folders.

## 12. Intended Cloud Architecture Usage

The validated local CSV is intended to be used conceptually in the cloud architecture as follows:

```text
Validated local CSV
  -> Azure Data Lake Storage Gen2 raw/
  -> Azure Container Apps Job
  -> processed/ and results/
  -> Azure SQL analytics
  -> Azure Functions API
```

No Azure upload, deployment, or cloud resource action is performed as part of this documentation step.
