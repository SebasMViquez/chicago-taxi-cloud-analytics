from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

from analytics.aggregations import all_aggregations
from cleaning.quality import clean_trips, summarize_quality
from ingestion.csv_reader import read_adls_csv, read_local_csv
from storage.parquet_writer import write_adls_json, write_adls_parquet, write_json, write_parquet
from storage.sql_writer import AnalyticsSqlWriter, SqlConfig
from transformations.trip_features import add_trip_features

LOGGER = logging.getLogger("chicago_taxi_processing")


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
    trips = read_adls_csv(file_system, input_path)
    _process_frame(
        trips,
        input_path,
        file_system=file_system,
        processed_path=processed_path,
        results_prefix=results_prefix,
        load_sql=load_sql,
    )
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

