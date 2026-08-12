import polars as pl

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


def clean_trips(trips: pl.DataFrame) -> pl.DataFrame:
    cleaned = trips.filter(
        pl.all_horizontal([pl.col(column).is_not_null() for column in REQUIRED_COLUMNS])
        & (pl.col("Trip Seconds") > 0)
        & (pl.col("Trip Miles") > 0)
        & (pl.col("Fare") >= 0)
        & (pl.col("Tips") >= 0)
        & (pl.col("Trip Total") >= 0)
        & (pl.col("Trip End Timestamp") >= pl.col("Trip Start Timestamp"))
    )
    return cleaned.unique(subset=["Trip ID"], keep="first")


def summarize_quality(source: pl.DataFrame, cleaned: pl.DataFrame) -> pl.DataFrame:
    duplicate_trip_ids = source.height - source.unique(subset=["Trip ID"], keep="first").height
    null_required_field_rows = source.filter(
        pl.any_horizontal([pl.col(column).is_null() for column in REQUIRED_COLUMNS])
    ).height
    invalid_duration_rows = source.filter(
        (pl.col("Trip Seconds") <= 0)
        | (pl.col("Trip End Timestamp") < pl.col("Trip Start Timestamp"))
    ).height
    invalid_distance_rows = source.filter(pl.col("Trip Miles") <= 0).height
    invalid_fare_rows = source.filter(pl.col("Fare") < 0).height
    negative_total_rows = source.filter(pl.col("Trip Total") < 0).height
    null_pickup_areas = source.filter(pl.col("Pickup Community Area").is_null()).height
    null_dropoff_areas = source.filter(pl.col("Dropoff Community Area").is_null()).height
    zero_distance_trips = source.filter(pl.col("Trip Miles") == 0).height
    rejected_rows = source.height - cleaned.height

    return pl.DataFrame(
        {
            "source_rows": [source.height],
            "accepted_rows": [cleaned.height],
            "rejected_rows": [rejected_rows],
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

