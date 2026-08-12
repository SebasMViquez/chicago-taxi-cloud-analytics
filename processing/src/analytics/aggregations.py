import polars as pl


def dashboard_summary(trips: pl.DataFrame) -> pl.DataFrame:
    return trips.select(
        pl.len().alias("total_trips"),
        pl.col("Fare").mean().alias("average_fare"),
        pl.col("Trip Miles").mean().alias("average_miles"),
        pl.col("duration_minutes").mean().alias("average_duration_minutes"),
    )


def demand_by_hour(trips: pl.DataFrame) -> pl.DataFrame:
    return trips.group_by(["day_of_week", "hour"]).agg(pl.len().alias("trip_count")).sort(
        ["day_of_week", "hour"]
    )


def demand_by_area(trips: pl.DataFrame) -> pl.DataFrame:
    return (
        trips.group_by("Pickup Community Area")
        .agg(
            pl.len().alias("trip_count"),
            pl.col("Fare").mean().alias("average_fare"),
            pl.col("Trip Miles").mean().alias("average_trip_miles"),
        )
        .sort("trip_count", descending=True)
    )


def payment_summary(trips: pl.DataFrame) -> pl.DataFrame:
    return trips.group_by("Payment Type").agg(
        pl.len().alias("trip_count"),
        pl.col("Trip Total").sum().alias("total_amount"),
        pl.col("tip_percentage").mean().alias("average_tip_percentage"),
    ).sort("trip_count", descending=True)


def monthly_trends(trips: pl.DataFrame) -> pl.DataFrame:
    return trips.group_by(["year", "month"]).agg(
        pl.len().alias("trip_count"),
        pl.col("Fare").mean().alias("average_fare"),
        pl.col("Trip Miles").mean().alias("average_trip_miles"),
    ).sort(["year", "month"])


def cost_by_distance(trips: pl.DataFrame) -> pl.DataFrame:
    return trips.group_by("distance_range").agg(
        pl.len().alias("trip_count"),
        pl.col("Fare").mean().alias("average_fare"),
        pl.col("Trip Total").mean().alias("average_trip_total"),
        pl.col("duration_minutes").mean().alias("average_duration_minutes"),
    ).rename({"distance_range": "distance_range_miles"})


def demand_by_day(trips: pl.DataFrame) -> pl.DataFrame:
    return trips.with_columns(pl.col("Trip Start Timestamp").dt.date().alias("trip_date")).group_by(
        "trip_date"
    ).agg(pl.len().alias("trip_count")).sort("trip_date")


def all_aggregations(trips: pl.DataFrame) -> dict[str, pl.DataFrame]:
    return {
        "dashboard_summary": dashboard_summary(trips),
        "demand_by_hour": demand_by_hour(trips),
        "demand_by_day": demand_by_day(trips),
        "demand_by_area": demand_by_area(trips),
        "cost_by_distance": cost_by_distance(trips),
        "payment_summary": payment_summary(trips),
        "monthly_trends": monthly_trends(trips),
    }

