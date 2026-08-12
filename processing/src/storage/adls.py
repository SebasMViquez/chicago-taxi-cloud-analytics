from __future__ import annotations

import os
from pathlib import PurePosixPath

from azure.core.exceptions import ResourceExistsError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContentSettings
from azure.storage.filedatalake import DataLakeServiceClient, FileSystemClient


def _service_client() -> DataLakeServiceClient:
    account_url = os.getenv("AZURE_STORAGE_ACCOUNT_URL")
    account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")

    if not account_url:
        if not account_name:
            raise RuntimeError(
                "AZURE_STORAGE_ACCOUNT_URL or AZURE_STORAGE_ACCOUNT_NAME is required."
            )
        account_url = f"https://{account_name}.dfs.core.windows.net"

    return DataLakeServiceClient(account_url=account_url, credential=DefaultAzureCredential())


def read_adls_file(file_system: str, path: str) -> bytes:
    file_client = _service_client().get_file_client(file_system=file_system, file_path=path)
    return file_client.download_file().readall()


def write_adls_file(file_system: str, path: str, content: bytes | str, content_type: str) -> None:
    data = content.encode("utf-8") if isinstance(content, str) else content
    file_system_client = _service_client().get_file_system_client(file_system)
    _ensure_parent_directories(file_system_client, path)
    file_client = file_system_client.get_file_client(path)
    file_client.upload_data(
        data,
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type),
    )


def _ensure_parent_directories(file_system_client: FileSystemClient, path: str) -> None:
    parts = PurePosixPath(path).parts[:-1]
    current = ""
    for part in parts:
        current = part if not current else f"{current}/{part}"
        try:
            file_system_client.get_directory_client(current).create_directory()
        except ResourceExistsError:
            continue
