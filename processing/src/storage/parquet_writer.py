from io import BytesIO
from pathlib import Path

import polars as pl

from storage.adls import write_adls_file


def write_parquet(frame: pl.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.write_parquet(path)


def write_json(frame: pl.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.write_json(path)


def write_adls_parquet(frame: pl.DataFrame, file_system: str, path: str) -> None:
    buffer = BytesIO()
    frame.write_parquet(buffer)
    write_adls_file(file_system, path, buffer.getvalue(), "application/octet-stream")


def write_adls_json(frame: pl.DataFrame, file_system: str, path: str) -> None:
    write_adls_file(file_system, path, frame.write_json(), "application/json")

