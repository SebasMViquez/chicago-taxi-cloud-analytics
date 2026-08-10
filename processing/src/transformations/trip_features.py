import polars as pl


def add_trip_features(trips: pl.DataFrame) -> pl.DataFrame:
    return trips.with_columns(
        pl.col("Trip Start Timestamp").dt.year().alias("year"),
        pl.col("Trip Start Timestamp").dt.month().alias("month"),
        pl.col("Trip Start Timestamp").dt.weekday().alias("day_of_week"),
        pl.col("Trip Start Timestamp").dt.hour().alias("hour"),
        (pl.col("Trip Seconds") / 60).alias("duration_minutes"),
        (pl.col("Trip Total") / pl.col("Trip Miles")).alias("cost_per_mile"),
        (pl.col("Trip Miles") / (pl.col("Trip Seconds") / 3600)).alias("average_speed_mph"),
        (pl.col("Tips") / pl.col("Trip Total") * 100).alias("tip_percentage"),
    )

