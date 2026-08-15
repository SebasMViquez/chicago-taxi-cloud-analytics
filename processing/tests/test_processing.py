import csv
from pathlib import Path

import polars as pl

from analytics.aggregations import all_aggregations
from cleaning.quality import clean_trips
from ingestion import csv_reader
from ingestion.csv_reader import read_local_csv
from main import process_file
from transformations.trip_features import add_trip_features

FIXTURE = Path(__file__).parent / "fixtures" / "chicago_taxi_sample.csv"
CSV_HEADER = (
    "Trip ID,Taxi ID,Trip Start Timestamp,Trip End Timestamp,Trip Seconds,Trip Miles,"
    "Pickup Community Area,Dropoff Community Area,Fare,Tips,Tolls,Extras,Trip Total,"
    "Payment Type,Company,Pickup Centroid Latitude,Pickup Centroid Longitude,"
    "Dropoff Centroid Latitude,Dropoff Centroid Longitude"
)


def write_trip_csv(
    path: Path,
    start_timestamp: str,
    end_timestamp: str,
    trip_seconds: str = "1800",
    fare: str = "14.25",
    tips: str = "2.00",
    tolls: str = "0",
    extras: str = "1.00",
    trip_total: str = "17.25",
) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADER.split(","))
        writer.writerow(
            [
                "TEST-TRIP-001",
                "TEST-TAXI-001",
                start_timestamp,
                end_timestamp,
                trip_seconds,
                "4.5",
                "32",
                "8",
                fare,
                tips,
                tolls,
                extras,
                trip_total,
                "Credit Card",
                "Test Taxi Co",
                "41.8781",
                "-87.6298",
                "41.8925",
                "-87.6262",
            ]
        )


def is_datetime_dtype(dtype: pl.DataType) -> bool:
    return dtype.base_type() == pl.Datetime


def test_read_local_csv_normalizes_trip_seconds_formats(tmp_path: Path) -> None:
    comma_path = tmp_path / "trip_seconds_comma.csv"
    plain_path = tmp_path / "trip_seconds_plain.csv"
    write_trip_csv(comma_path, "2023-01-03 08:15:00", "2023-01-03 08:35:00", "1,389")
    write_trip_csv(plain_path, "2023-01-03 08:15:00", "2023-01-03 08:35:00", "1200")

    comma_trips = read_local_csv(comma_path)
    plain_trips = read_local_csv(plain_path)

    assert comma_trips.schema["Trip Seconds"] == pl.Int64
    assert comma_trips["Trip Seconds"].item() == 1389
    assert plain_trips["Trip Seconds"].item() == 1200


def test_read_local_csv_normalizes_monetary_formats(tmp_path: Path) -> None:
    city_path = tmp_path / "city_money.csv"
    fixture_path = tmp_path / "fixture_money.csv"
    write_trip_csv(
        city_path,
        "01/31/2023 11:45:00 PM",
        "02/01/2023 12:15:00 AM",
        fare="$35.25",
        tips="$1,061.24",
        tolls="$0.00",
        extras="$4,444.44",
        trip_total="$8,902.63",
    )
    write_trip_csv(
        fixture_path,
        "2023-01-03 08:15:00",
        "2023-01-03 08:35:00",
        fare="14.25",
        tips="2.00",
        tolls="0",
        extras="1.00",
        trip_total="17.25",
    )

    city_trips = read_local_csv(city_path)
    fixture_trips = read_local_csv(fixture_path)

    for column in ["Fare", "Tips", "Tolls", "Extras", "Trip Total"]:
        assert city_trips.schema[column] == pl.Float64
    assert city_trips["Fare"].item() == 35.25
    assert city_trips["Tips"].item() == 1061.24
    assert city_trips["Tolls"].item() == 0.0
    assert city_trips["Extras"].item() == 4444.44
    assert city_trips["Trip Total"].item() == 8902.63
    assert fixture_trips["Fare"].item() == 14.25
    assert fixture_trips["Trip Total"].item() == 17.25


def test_invalid_numeric_values_become_null_and_cleaning_rejects_required_nulls(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "invalid_numeric.csv"
    write_trip_csv(
        csv_path,
        "2023-01-03 08:15:00",
        "2023-01-03 08:35:00",
        trip_seconds="not-a-number",
        fare="$not-a-number",
        tips="",
    )

    trips = read_local_csv(csv_path)
    cleaned = clean_trips(trips)

    assert trips["Trip Seconds"].null_count() == 1
    assert trips["Fare"].null_count() == 1
    assert trips["Tips"].null_count() == 1
    assert cleaned.height == 0


def test_clean_trips_rejects_invalid_rows() -> None:
    trips = read_local_csv(FIXTURE)

    cleaned = clean_trips(trips)

    assert trips.height == 3
    assert cleaned.height == 2


def test_read_local_csv_parses_fixture_timestamp_format(tmp_path: Path) -> None:
    csv_path = tmp_path / "fixture_timestamp.csv"
    write_trip_csv(csv_path, "2023-01-03 08:15:00", "2023-01-03 08:35:00")

    trips = read_local_csv(csv_path)

    assert is_datetime_dtype(trips.schema["Trip Start Timestamp"])
    assert is_datetime_dtype(trips.schema["Trip End Timestamp"])
    assert trips.select(pl.col("Trip Start Timestamp").dt.hour()).item() == 8
    assert trips.select(pl.col("Trip End Timestamp").dt.minute()).item() == 35


def test_read_local_csv_parses_city_timestamp_format(tmp_path: Path) -> None:
    csv_path = tmp_path / "city_timestamp.csv"
    write_trip_csv(csv_path, "01/31/2023 11:45:00 PM", "02/01/2023 12:15:00 AM")

    trips = read_local_csv(csv_path)

    assert is_datetime_dtype(trips.schema["Trip Start Timestamp"])
    assert is_datetime_dtype(trips.schema["Trip End Timestamp"])
    assert trips.select(pl.col("Trip Start Timestamp").dt.hour()).item() == 23
    assert trips.select(pl.col("Trip End Timestamp").dt.hour()).item() == 0


def test_read_adls_csv_parses_city_timestamp_format(
    tmp_path: Path,
    monkeypatch,
) -> None:
    csv_path = tmp_path / "city_timestamp_adls.csv"
    write_trip_csv(csv_path, "01/31/2023 11:45:00 PM", "02/01/2023 12:15:00 AM")
    content = csv_path.read_bytes()

    monkeypatch.setattr(csv_reader, "read_adls_file", lambda _file_system, _path: content)

    trips = csv_reader.read_adls_csv("chicago-taxi", "raw/sample.csv")

    assert is_datetime_dtype(trips.schema["Trip Start Timestamp"])
    assert is_datetime_dtype(trips.schema["Trip End Timestamp"])
    assert trips.select(pl.col("Trip Start Timestamp").dt.hour()).item() == 23
    assert trips.select(pl.col("Trip End Timestamp").dt.hour()).item() == 0


def test_invalid_timestamp_becomes_null_and_is_rejected_by_cleaning(tmp_path: Path) -> None:
    csv_path = tmp_path / "invalid_timestamp.csv"
    write_trip_csv(csv_path, "not-a-timestamp", "02/01/2023 12:15:00 AM")

    trips = read_local_csv(csv_path)
    cleaned = clean_trips(trips)

    assert trips["Trip Start Timestamp"].null_count() == 1
    assert cleaned.height == 0


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
