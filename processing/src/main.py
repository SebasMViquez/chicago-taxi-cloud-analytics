from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
from tempfile import TemporaryDirectory

import polars as pl

from analytics.aggregations import all_aggregations
from cleaning.quality import clean_trips, summarize_quality
from ingestion.csv_reader import read_local_csv, scan_adls_csv
from storage.adls import write_adls_file_from_path
from storage.parquet_writer import write_adls_json, write_adls_parquet, write_json, write_parquet
from storage.sql_writer import AnalyticsSqlWriter, SqlConfig
from transformations.trip_features import add_trip_features

LOGGER = logging.getLogger("chicago_taxi_processing")
REQUIRED_COLUMNS = [
    "Trip ID",
    "Trip Start Timestamp",
    "Trip End Timestamp",
    "Trip Seconds",
    "Trip Miles",
    "Fare",
    "Trip Total",
    "Payment Type",
]


def process_file(input_path: Path, output_dir: Path, load_sql: bool = False) -> Path:
    trips = read_local_csv(input_path)
    return _process_frame(trips, str(input_path), output_dir=output_dir, load_sql=load_sql)


def process_adls_file(
    file_system: str,
    input_path: str,
    processed_path: str,
    results_prefix: str,
    load_sql: bool = False,
) -> str:
    with TemporaryDirectory() as temp_dir:
        local_input = Path(temp_dir) / "input.csv"
        local_processed = Path(temp_dir) / "processed_trips.parquet"
        trips = scan_adls_csv(file_system, input_path, local_input)
        _process_adls_lazy_frame(
            trips,
            input_path,
            file_system=file_system,
            processed_path=processed_path,
            results_prefix=results_prefix,
            local_processed_path=local_processed,
            load_sql=load_sql,
        )
        return processed_path


def _collect_lazy(frame: pl.LazyFrame) -> pl.DataFrame:
    return frame.collect(engine="streaming")


def _row_count(frame: pl.LazyFrame) -> int:
    return int(_collect_lazy(frame.select(pl.len().alias("row_count"))).item())


def _summarize_quality_lazy(source: pl.LazyFrame, cleaned: pl.LazyFrame) -> pl.DataFrame:
    duplicate_trip_ids = _collect_lazy(
        source.select((pl.len() - pl.col("Trip ID").n_unique()).alias("duplicate_trip_ids"))
    ).item()
    null_required_field_rows = _row_count(
        source.filter(
            pl.any_horizontal([pl.col(column).is_null() for column in REQUIRED_COLUMNS])
        )
    )
    invalid_duration_rows = _row_count(
        source.filter(
            (pl.col("Trip Seconds") <= 0)
            | (pl.col("Trip End Timestamp") < pl.col("Trip Start Timestamp"))
        )
    )
    invalid_distance_rows = _row_count(source.filter(pl.col("Trip Miles") <= 0))
    invalid_fare_rows = _row_count(source.filter(pl.col("Fare") < 0))
    negative_total_rows = _row_count(source.filter(pl.col("Trip Total") < 0))
    null_pickup_areas = _row_count(source.filter(pl.col("Pickup Community Area").is_null()))
    null_dropoff_areas = _row_count(source.filter(pl.col("Dropoff Community Area").is_null()))
    zero_distance_trips = _row_count(source.filter(pl.col("Trip Miles") == 0))
    source_rows = _row_count(source)
    accepted_rows = _row_count(cleaned)

    return pl.DataFrame(
        {
            "source_rows": [source_rows],
            "accepted_rows": [accepted_rows],
            "rejected_rows": [source_rows - accepted_rows],
            "duplicate_trip_ids": [duplicate_trip_ids],
            "null_required_field_rows": [null_required_field_rows],
            "null_pickup_areas": [null_pickup_areas],
            "null_dropoff_areas": [null_dropoff_areas],
            "zero_distance_trips": [zero_distance_trips],
            "invalid_duration_rows": [invalid_duration_rows],
            "invalid_distance_rows": [invalid_distance_rows],
            "invalid_fare_rows": [invalid_fare_rows],
            "negative_total_rows": [negative_total_rows],
        }
    )


def _process_adls_lazy_frame(
    trips: pl.LazyFrame,
    input_path: str,
    file_system: str,
    processed_path: str,
    results_prefix: str,
    local_processed_path: Path,
    load_sql: bool = False,
) -> str:
    rows_input = _row_count(trips)
    LOGGER.info("stage=cleaning rows_input=%s", rows_input)
    cleaned = clean_trips(trips)
    transformed = add_trip_features(cleaned)
    quality = _summarize_quality_lazy(trips, cleaned)
    aggregations = {
        name: _collect_lazy(frame) for name, frame in all_aggregations(transformed).items()
    }
    rows_output = int(quality["accepted_rows"].item())
    LOGGER.info("stage=transform rows_output=%s", rows_output)

    transformed.sink_parquet(local_processed_path, engine="streaming")
    write_adls_file_from_path(
        file_system,
        processed_path,
        local_processed_path,
        "application/octet-stream",
    )
    write_adls_json(quality, file_system, f"{results_prefix}/data_quality_summary.json")
    for name, frame in aggregations.items():
        write_adls_parquet(frame, file_system, f"{results_prefix}/{name}.parquet")

    if load_sql:
        run_id = AnalyticsSqlWriter(SqlConfig.from_environment()).load(
            dataset="chicago-taxi",
            input_path=input_path,
            quality=quality,
            aggregations=aggregations,
        )
        LOGGER.info("stage=sql_load run_id=%s status=completed", run_id)

    return processed_path


def _process_frame(
    trips,
    input_path: str,
    output_dir: Path | None = None,
    file_system: str | None = None,
    processed_path: str | None = None,
    results_prefix: str | None = None,
    load_sql: bool = False,
) -> Path | str:
    LOGGER.info("stage=cleaning rows_input=%s", trips.height)
    cleaned = clean_trips(trips)
    transformed = add_trip_features(cleaned)
    quality = summarize_quality(trips, cleaned)
    aggregations = all_aggregations(transformed)
    LOGGER.info("stage=transform rows_output=%s", transformed.height)

    if file_system:
        if not processed_path or not results_prefix:
            raise RuntimeError(
                "processed_path and results_prefix are required for ADLS processing."
            )
        write_adls_parquet(transformed, file_system, processed_path)
        write_adls_json(quality, file_system, f"{results_prefix}/data_quality_summary.json")
        for name, frame in aggregations.items():
            write_adls_parquet(frame, file_system, f"{results_prefix}/{name}.parquet")
        output_path: Path | str = processed_path
    else:
        if output_dir is None:
            raise RuntimeError("output_dir is required for local processing.")
        output_path = output_dir / "processed" / "processed_trips.parquet"
        write_parquet(transformed, output_path)
        write_json(quality, output_dir / "results" / "data_quality_summary.json")
        for name, frame in aggregations.items():
            write_parquet(frame, output_dir / "results" / f"{name}.parquet")

    if load_sql:
        run_id = AnalyticsSqlWriter(SqlConfig.from_environment()).load(
            dataset="chicago-taxi",
            input_path=input_path,
            quality=quality,
            aggregations=aggregations,
        )
        LOGGER.info("stage=sql_load run_id=%s status=completed", run_id)

    return output_path


def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Process Chicago Taxi Trips CSV data.")
    parser.add_argument(
        "--mode",
        choices=["local", "adls"],
        default=os.getenv("PROCESSING_MODE", "local"),
    )
    parser.add_argument(
        "--input",
        default=os.getenv("PROCESSING_INPUT_PATH"),
        help="Local CSV path or ADLS path.",
    )
    parser.add_argument(
        "--output",
        default=os.getenv("PROCESSING_OUTPUT_DIR"),
        help="Local output directory.",
    )
    parser.add_argument(
        "--file-system",
        default=os.getenv("AZURE_STORAGE_CONTAINER_NAME"),
        help="ADLS file system/container name.",
    )
    parser.add_argument(
        "--processed-path",
        default=os.getenv("PROCESSING_PROCESSED_PATH"),
        help="ADLS processed Parquet path.",
    )
    parser.add_argument(
        "--results-prefix",
        default=os.getenv("PROCESSING_RESULTS_PREFIX"),
        help="ADLS results directory path.",
    )
    parser.add_argument(
        "--load-sql",
        action="store_true",
        default=os.getenv("PROCESSING_LOAD_SQL", "").lower() == "true",
        help="Load aggregate results to Azure SQL.",
    )
    args = parser.parse_args()

    if not args.input:
        raise SystemExit("--input or PROCESSING_INPUT_PATH is required.")

    if args.mode == "local":
        if not args.output:
            raise SystemExit("--output is required in local mode.")
        output_path = process_file(Path(args.input), Path(args.output), load_sql=args.load_sql)
    else:
        if not args.file_system or not args.processed_path or not args.results_prefix:
            raise SystemExit(
                "--file-system, --processed-path and --results-prefix are required in ADLS mode."
            )
        output_path = process_adls_file(
            file_system=args.file_system,
            input_path=args.input,
            processed_path=args.processed_path,
            results_prefix=args.results_prefix,
            load_sql=args.load_sql,
        )

    print(f"Wrote processed output to {output_path}")


if __name__ == "__main__":
    run()

