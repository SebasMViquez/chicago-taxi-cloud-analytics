from io import BytesIO
from pathlib import Path

import polars as pl

from storage.adls import read_adls_file

CHICAGO_TAXI_SCHEMA = {
    "Trip ID": pl.String,
    "Taxi ID": pl.String,
    "Trip Start Timestamp": pl.Datetime,
    "Trip End Timestamp": pl.Datetime,
    "Trip Seconds": pl.Int64,
    "Trip Miles": pl.Float64,
    "Pickup Community Area": pl.Int64,
    "Dropoff Community Area": pl.Int64,
    "Fare": pl.Float64,
    "Tips": pl.Float64,
    "Tolls": pl.Float64,
    "Extras": pl.Float64,
    "Trip Total": pl.Float64,
    "Payment Type": pl.String,
    "Company": pl.String,
    "Pickup Centroid Latitude": pl.Float64,
    "Pickup Centroid Longitude": pl.Float64,
    "Dropoff Centroid Latitude": pl.Float64,
    "Dropoff Centroid Longitude": pl.Float64,
}


def read_local_csv(path: Path) -> pl.DataFrame:
    return pl.read_csv(
        path,
        try_parse_dates=True,
        schema_overrides=CHICAGO_TAXI_SCHEMA,
    )


def read_adls_csv(file_system: str, path: str) -> pl.DataFrame:
    content = read_adls_file(file_system, path)
    return pl.read_csv(BytesIO(content), try_parse_dates=True, schema_overrides=CHICAGO_TAXI_SCHEMA)

