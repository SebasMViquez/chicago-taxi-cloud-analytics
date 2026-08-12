import polars as pl


def add_trip_features(trips: pl.DataFrame) -> pl.DataFrame:
    return trips.with_columns(
        pl.col("Trip Start Timestamp").dt.year().alias("year"),
        pl.col("Trip Start Timestamp").dt.month().alias("month"),
        pl.col("Trip Start Timestamp").dt.day().alias("day"),
        pl.col("Trip Start Timestamp").dt.weekday().alias("day_of_week"),
        pl.col("Trip Start Timestamp").dt.hour().alias("hour"),
        (pl.col("Trip Start Timestamp").dt.weekday() >= 6).alias("is_weekend"),
        (pl.col("Trip Seconds") / 60).alias("duration_minutes"),
        (pl.col("Trip Total") / pl.col("Trip Miles")).alias("cost_per_mile"),
        (pl.col("Trip Miles") / (pl.col("Trip Seconds") / 3600)).alias("average_speed_mph"),
        (pl.col("Tips") / pl.col("Trip Total") * 100).alias("tip_percentage"),
        pl.when(pl.col("Trip Miles") < 2)
        .then(pl.lit("0-2"))
        .when(pl.col("Trip Miles") < 5)
        .then(pl.lit("2-5"))
        .when(pl.col("Trip Miles") < 10)
        .then(pl.lit("5-10"))
        .otherwise(pl.lit("10+"))
        .alias("distance_range"),
    )

