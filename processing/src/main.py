from __future__ import annotations

import argparse
from pathlib import Path

from cleaning.quality import clean_trips, summarize_quality
from ingestion.csv_reader import read_local_csv
from storage.parquet_writer import write_parquet
from transformations.trip_features import add_trip_features


def process_file(input_path: Path, output_dir: Path) -> Path:
    trips = read_local_csv(input_path)
    cleaned = clean_trips(trips)
    transformed = add_trip_features(cleaned)
    output_path = output_dir / "processed_trips.parquet"
    write_parquet(transformed, output_path)
    summarize_quality(trips, cleaned).write_json(output_dir / "data_quality_summary.json")
    return output_path


def run() -> None:
    parser = argparse.ArgumentParser(description="Process a local Chicago Taxi Trips CSV sample.")
    parser.add_argument("--input", required=True, type=Path, help="Path to a local CSV file.")
    parser.add_argument("--output", required=True, type=Path, help="Directory for local outputs.")
    args = parser.parse_args()

    output_path = process_file(args.input, args.output)
    print(f"Wrote local development Parquet output to {output_path}")


if __name__ == "__main__":
    run()

