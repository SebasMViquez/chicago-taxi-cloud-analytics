from pathlib import Path

import polars as pl

from analytics.aggregations import all_aggregations
from cleaning.quality import clean_trips
from ingestion.csv_reader import read_local_csv
from main import process_file
from transformations.trip_features import add_trip_features

FIXTURE = Path(__file__).parent / "fixtures" / "chicago_taxi_sample.csv"


def test_clean_trips_rejects_invalid_rows() -> None:
    trips = read_local_csv(FIXTURE)

    cleaned = clean_trips(trips)

    assert trips.height == 3
    assert cleaned.height == 2


def test_add_trip_features_adds_expected_columns() -> None:
    trips = clean_trips(read_local_csv(FIXTURE))

    transformed = add_trip_features(trips)

    assert "duration_minutes" in transformed.columns
    assert "cost_per_mile" in transformed.columns
    assert "average_speed_mph" in transformed.columns
    assert "tip_percentage" in transformed.columns
    assert "day" in transformed.columns
    assert "is_weekend" in transformed.columns
    assert "distance_range" in transformed.columns


def test_process_file_writes_parquet(tmp_path: Path) -> None:
    output_path = process_file(FIXTURE, tmp_path)

    assert output_path.exists()
    assert (tmp_path / "results" / "data_quality_summary.json").exists()
    assert (tmp_path / "results" / "demand_by_hour.parquet").exists()
    assert (tmp_path / "results" / "payment_summary.parquet").exists()


def test_all_aggregations_returns_dashboard_ready_outputs() -> None:
    trips = add_trip_features(clean_trips(read_local_csv(FIXTURE)))

    aggregations = all_aggregations(trips)

    assert set(aggregations) == {
        "dashboard_summary",
        "demand_by_hour",
        "demand_by_day",
        "demand_by_area",
        "cost_by_distance",
        "payment_summary",
        "monthly_trends",
    }
    assert isinstance(aggregations["dashboard_summary"], pl.DataFrame)
