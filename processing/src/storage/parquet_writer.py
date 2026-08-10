from pathlib import Path

import polars as pl


def write_parquet(frame: pl.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.write_parquet(path)


def write_azure_blob() -> None:
    raise NotImplementedError("Azure Blob writes will be added when storage is provisioned.")


def load_azure_sql() -> None:
    raise NotImplementedError("Azure SQL loading will be added after the analytical schema is approved.")

