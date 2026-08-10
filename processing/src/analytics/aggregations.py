import polars as pl


def demand_by_hour(trips: pl.DataFrame) -> pl.DataFrame:
    return trips.group_by(["day_of_week", "hour"]).agg(pl.len().alias("trip_count"))


def demand_by_area(trips: pl.DataFrame) -> pl.DataFrame:
    return trips.group_by("Pickup Community Area").agg(pl.len().alias("trip_count"))


def payment_summary(trips: pl.DataFrame) -> pl.DataFrame:
    return trips.group_by("Payment Type").agg(
        pl.len().alias("trip_count"),
        pl.col("Trip Total").sum().alias("total_amount"),
    )


def monthly_trends(trips: pl.DataFrame) -> pl.DataFrame:
    return trips.group_by(["year", "month"]).agg(pl.len().alias("trip_count"))


def cost_by_distance(trips: pl.DataFrame) -> pl.DataFrame:
    return trips.with_columns(
        pl.when(pl.col("Trip Miles") < 2)
        .then(pl.lit("0-2"))
        .when(pl.col("Trip Miles") < 5)
        .then(pl.lit("2-5"))
        .when(pl.col("Trip Miles") < 10)
        .then(pl.lit("5-10"))
        .otherwise(pl.lit("10+"))
        .alias("distance_range_miles")
    ).group_by("distance_range_miles").agg(
        pl.len().alias("trip_count"),
        pl.col("Trip Total").mean().alias("average_trip_total"),
    )

