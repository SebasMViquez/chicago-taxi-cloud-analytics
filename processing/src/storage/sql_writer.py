from __future__ import annotations

import os
import struct
from dataclasses import dataclass
from datetime import UTC, datetime

import polars as pl
import pyodbc
from azure.identity import DefaultAzureCredential


@dataclass(frozen=True)
class SqlConfig:
    server: str
    database: str
    auth_mode: str = "ManagedIdentity"

    @classmethod
    def from_environment(cls) -> SqlConfig:
        server = os.getenv("SQL_SERVER_NAME") or os.getenv("SQL_SERVER")
        database = os.getenv("SQL_DATABASE_NAME") or os.getenv("SQL_DATABASE")
        if not server or not database:
            raise RuntimeError(
                "SQL_SERVER_NAME and SQL_DATABASE_NAME are required for SQL loading."
            )

        return cls(
            server=server,
            database=database,
            auth_mode=os.getenv("SQL_AUTH_MODE", "ManagedIdentity"),
        )


class AnalyticsSqlWriter:
    def __init__(self, config: SqlConfig) -> None:
        self._config = config

    def load(
        self,
        dataset: str,
        input_path: str,
        quality: pl.DataFrame,
        aggregations: dict[str, pl.DataFrame],
    ) -> int:
        with self._connect() as connection:
            cursor = connection.cursor()
            run_id = self._create_run(cursor, dataset, input_path, quality)
            self._insert_aggregations(cursor, run_id, aggregations)
            self._insert_quality(cursor, run_id, quality)
            cursor.execute(
                """
                UPDATE dbo.AnalyticsRuns
                SET Status = ?, CompletedAtUtc = ?
                WHERE AnalyticsRunId = ?
                """,
                "Completed",
                datetime.now(UTC).replace(tzinfo=None),
                run_id,
            )
            connection.commit()
            return run_id

    def _connect(self) -> pyodbc.Connection:
        host = (
            self._config.server
            if "." in self._config.server
            else f"{self._config.server}.database.windows.net"
        )

        connection_string = (
            "Driver={ODBC Driver 18 for SQL Server};"
            f"Server=tcp:{host},1433;"
            f"Database={self._config.database};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )

        if self._config.auth_mode == "SqlPassword":
            sql_user = os.getenv("SQL_USER") or os.getenv("SQL_USERNAME")
            sql_password = os.getenv("SQL_PASSWORD")

            if not sql_user or not sql_password:
                raise RuntimeError(
                    "SQL_USER and SQL_PASSWORD are required when SQL_AUTH_MODE=SqlPassword."
                )

            connection_string += f"UID={sql_user};PWD={sql_password};"
            return pyodbc.connect(connection_string)

        if self._config.auth_mode == "ManagedIdentity":
            token = DefaultAzureCredential().get_token(
                "https://database.windows.net/.default"
            ).token
            token_bytes = token.encode("utf-16-le")
            token_struct = struct.pack(
                f"<I{len(token_bytes)}s",
                len(token_bytes),
                token_bytes,
            )
            sql_copt_ss_access_token = 1256
            return pyodbc.connect(
                connection_string,
                attrs_before={sql_copt_ss_access_token: token_struct},
            )

        connection_string += "Authentication=ActiveDirectoryDefault;"
        return pyodbc.connect(connection_string)

    def _create_run(
        self,
        cursor: pyodbc.Cursor,
        dataset: str,
        input_path: str,
        quality: pl.DataFrame,
    ) -> int:
        row = quality.row(0, named=True)
        cursor.execute(
            """
            INSERT INTO dbo.AnalyticsRuns
                (SourceDatasetName, SourceInputPath, Status, TotalRows,
                 ValidRows, InvalidRows, Notes)
            OUTPUT INSERTED.AnalyticsRunId
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            dataset,
            input_path,
            "Running",
            row["source_rows"],
            row["accepted_rows"],
            row["rejected_rows"],
            (
                f"Input: {input_path}; source_rows={row['source_rows']}; "
                f"accepted_rows={row['accepted_rows']}"
            ),
        )
        return int(cursor.fetchone()[0])

    def _insert_quality(self, cursor: pyodbc.Cursor, run_id: int, quality: pl.DataFrame) -> None:
        row = quality.row(0, named=True)
        cursor.execute(
            """
            INSERT INTO dbo.DataQualityMetrics
                (AnalyticsRunId, SourceRows, AcceptedRows, RejectedRows,
                 DuplicateTripIds, NullRequiredFieldRows, NullPickupAreas, NullDropoffAreas,
                 ZeroDistanceTrips, InvalidDurationRows, InvalidDistanceRows, InvalidFareRows,
                 NegativeTotalRows)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            run_id,
            row["source_rows"],
            row["accepted_rows"],
            row["rejected_rows"],
            row["duplicate_trip_ids"],
            row["null_required_field_rows"],
            row["null_pickup_areas"],
            row["null_dropoff_areas"],
            row["zero_distance_trips"],
            row["invalid_duration_rows"],
            row["invalid_distance_rows"],
            row["invalid_fare_rows"],
            row["negative_total_rows"],
        )

    def _insert_aggregations(
        self,
        cursor: pyodbc.Cursor,
        run_id: int,
        aggregations: dict[str, pl.DataFrame],
    ) -> None:
        self._insert_demand_by_hour(cursor, run_id, aggregations["demand_by_hour"])
        self._insert_demand_by_day(cursor, run_id, aggregations["demand_by_day"])
        self._insert_demand_by_area(cursor, run_id, aggregations["demand_by_area"])
        self._insert_cost_by_distance(cursor, run_id, aggregations["cost_by_distance"])
        self._insert_payment_summary(cursor, run_id, aggregations["payment_summary"])
        self._insert_monthly_trends(cursor, run_id, aggregations["monthly_trends"])

    def _insert_demand_by_hour(
        self,
        cursor: pyodbc.Cursor,
        run_id: int,
        frame: pl.DataFrame,
    ) -> None:
        cursor.executemany(
            """
            INSERT INTO dbo.TripDemandByHour
                (AnalyticsRunId, DayOfWeek, HourOfDay, TripCount)
            VALUES (?, ?, ?, ?)
            """,
            [
                (run_id, row["day_of_week"], row["hour"], row["trip_count"])
                for row in frame.iter_rows(named=True)
            ],
        )

    def _insert_demand_by_day(
        self,
        cursor: pyodbc.Cursor,
        run_id: int,
        frame: pl.DataFrame,
    ) -> None:
        cursor.executemany(
            """
            INSERT INTO dbo.TripDemandByDay
                (AnalyticsRunId, TripDate, TripCount)
            VALUES (?, ?, ?)
            """,
            [(run_id, row["trip_date"], row["trip_count"]) for row in frame.iter_rows(named=True)],
        )

    def _insert_demand_by_area(
        self,
        cursor: pyodbc.Cursor,
        run_id: int,
        frame: pl.DataFrame,
    ) -> None:
        cursor.executemany(
            """
            INSERT INTO dbo.TripDemandByPickupArea
                (AnalyticsRunId, PickupCommunityArea, TripCount, AverageFare, AverageTripMiles)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    run_id,
                    row["Pickup Community Area"],
                    row["trip_count"],
                    row["average_fare"],
                    row["average_trip_miles"],
                )
                for row in frame.iter_rows(named=True)
            ],
        )

    def _insert_cost_by_distance(
        self,
        cursor: pyodbc.Cursor,
        run_id: int,
        frame: pl.DataFrame,
    ) -> None:
        cursor.executemany(
            """
            INSERT INTO dbo.TripCostByDistanceRange
                (AnalyticsRunId, DistanceRangeMiles, TripCount,
                 AverageFare, AverageTripTotal, AverageDurationMinutes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    run_id,
                    row["distance_range_miles"],
                    row["trip_count"],
                    row["average_fare"],
                    row["average_trip_total"],
                    row["average_duration_minutes"],
                )
                for row in frame.iter_rows(named=True)
            ],
        )

    def _insert_payment_summary(
        self,
        cursor: pyodbc.Cursor,
        run_id: int,
        frame: pl.DataFrame,
    ) -> None:
        cursor.executemany(
            """
            INSERT INTO dbo.PaymentTypeSummary
                (AnalyticsRunId, PaymentType, TripCount, TotalAmount, AverageTipPercentage)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    run_id,
                    row["Payment Type"],
                    row["trip_count"],
                    row["total_amount"],
                    row["average_tip_percentage"],
                )
                for row in frame.iter_rows(named=True)
            ],
        )

    def _insert_monthly_trends(
        self,
        cursor: pyodbc.Cursor,
        run_id: int,
        frame: pl.DataFrame,
    ) -> None:
        cursor.executemany(
            """
            INSERT INTO dbo.MonthlyTripTrend
                (AnalyticsRunId, TripYear, TripMonth, TripCount, AverageFare, AverageTripMiles)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    run_id,
                    row["year"],
                    row["month"],
                    row["trip_count"],
                    row["average_fare"],
                    row["average_trip_miles"],
                )
                for row in frame.iter_rows(named=True)
            ],
        )
