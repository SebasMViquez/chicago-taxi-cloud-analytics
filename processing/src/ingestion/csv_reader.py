from pathlib import Path
from tempfile import TemporaryDirectory

import polars as pl

from storage.adls import download_adls_file

Frame = pl.DataFrame | pl.LazyFrame

CHICAGO_TAXI_SCHEMA = {
    "Trip ID": pl.String,
    "Taxi ID": pl.String,
    "Trip Start Timestamp": pl.String,
    "Trip End Timestamp": pl.String,
    "Trip Seconds": pl.String,
    "Trip Miles": pl.Float64,
    "Pickup Community Area": pl.Int64,
    "Dropoff Community Area": pl.Int64,
    "Fare": pl.String,
    "Tips": pl.String,
    "Tolls": pl.String,
    "Extras": pl.String,
    "Trip Total": pl.String,
    "Payment Type": pl.String,
    "Company": pl.String,
    "Pickup Centroid Latitude": pl.Float64,
    "Pickup Centroid Longitude": pl.Float64,
    "Dropoff Centroid Latitude": pl.Float64,
    "Dropoff Centroid Longitude": pl.Float64,
}

TIMESTAMP_COLUMNS = ["Trip Start Timestamp", "Trip End Timestamp"]
TIMESTAMP_FORMATS = ["%Y-%m-%d %H:%M:%S", "%m/%d/%Y %I:%M:%S %p"]
MONETARY_COLUMNS = ["Fare", "Tips", "Tolls", "Extras", "Trip Total"]


def _parse_timestamp(column: str) -> pl.Expr:
    return pl.coalesce(
        [
            pl.col(column).str.strptime(pl.Datetime, date_format, strict=False)
            for date_format in TIMESTAMP_FORMATS
        ]
    ).alias(column)


def _normalize_timestamps(trips: Frame) -> Frame:
    return trips.with_columns([_parse_timestamp(column) for column in TIMESTAMP_COLUMNS])


def _parse_trip_seconds() -> pl.Expr:
    return (
        pl.col("Trip Seconds")
        .str.strip_chars()
        .str.replace_all(",", "")
        .cast(pl.Int64, strict=False)
        .alias("Trip Seconds")
    )


def _parse_monetary(column: str) -> pl.Expr:
    return (
        pl.col(column)
        .str.strip_chars()
        .str.replace_all(r"\$", "")
        .str.replace_all(",", "")
        .cast(pl.Float64, strict=False)
        .alias(column)
    )


def _normalize_numeric_columns(trips: Frame) -> Frame:
    return trips.with_columns(
        [_parse_trip_seconds(), *[_parse_monetary(column) for column in MONETARY_COLUMNS]]
    )


def _normalize_trips(trips: Frame) -> Frame:
    return _normalize_numeric_columns(_normalize_timestamps(trips))


def scan_local_csv(path: Path) -> pl.LazyFrame:
    trips = pl.scan_csv(path, schema_overrides=CHICAGO_TAXI_SCHEMA, low_memory=True)
    return _normalize_trips(trips)


def read_local_csv(path: Path) -> pl.DataFrame:
    trips = pl.read_csv(path, schema_overrides=CHICAGO_TAXI_SCHEMA)
    return _normalize_trips(trips)


def read_adls_csv(file_system: str, path: str) -> pl.DataFrame:
    with TemporaryDirectory() as temp_dir:
        local_path = Path(temp_dir) / "input.csv"
        download_adls_file(file_system, path, local_path)
        return read_local_csv(local_path)


def scan_adls_csv(file_system: str, path: str, local_path: Path) -> pl.LazyFrame:
    download_adls_file(file_system, path, local_path)
    return scan_local_csv(local_path)

