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
    return trips.filter(
        pl.all_horizontal([pl.col(column).is_not_null() for column in REQUIRED_COLUMNS])
        & (pl.col("Trip Seconds") > 0)
        & (pl.col("Trip Miles") > 0)
        & (pl.col("Fare") >= 0)
        & (pl.col("Trip Total") >= 0)
        & (pl.col("Trip End Timestamp") >= pl.col("Trip Start Timestamp"))
    )


def summarize_quality(source: pl.DataFrame, cleaned: pl.DataFrame) -> pl.DataFrame:
    rejected_rows = source.height - cleaned.height
    return pl.DataFrame(
        {
            "source_rows": [source.height],
            "accepted_rows": [cleaned.height],
            "rejected_rows": [rejected_rows],
        }
    )

