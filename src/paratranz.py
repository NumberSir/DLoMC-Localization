import contextlib
import os
import shutil
from pathlib import Path
from zipfile import ZipFile

import httpx
from loguru._logger import Logger

from src.config import settings
from src.log import logger


class Paratranz:
    def __init__(self, client: httpx.Client = httpx.Client()):
        self._logger = logger.bind(project_name="Paratranz")
        self._client = client
        self._base_url = "https://paratranz.cn/api"
        self._headers = {"Authorization": settings.paratranz.token}
        self._project_id = settings.paratranz.project_id
        self.logger.info("")
        self.logger.info("======= PARATRANZ START =======")

    def _update_file(self, file: str, fileid: int):
        url = f"{self.base_url}/projects/{self.project_id}/files/{fileid}"
        headers = {**self.headers, 'Content-Type': 'multipart/form-data'}
        data = {"file": bytearray(file, "utf-8")}
        response = self.client.post(url, headers=headers, data=data)
        self.logger.bind(filepath=response.json()).success("Updated file successfully")

    def _create_file(self, file: str, path: Path):
        url = f"{self.base_url}/projects/{self.project_id}/files"
        headers = {**self.headers, 'Content-Type': 'multipart/form-data'}
        data = {"file": bytearray(file, "utf-8"), "path": path.__str__()}
        response = self.client.post(url, headers=headers, data=data)
        self.logger.bind(filepath=response.json()).success("Created file successfully")

    def download(self):
        self.logger.info("Starting to download translated files...")
        os.makedirs(settings.filepath.root / settings.filepath.tmp, exist_ok=True)
        os.makedirs(settings.filepath.root / settings.filepath.download, exist_ok=True)
        with contextlib.suppress(httpx.TimeoutException):
            self._trigger_export()
        self._download_artifacts()
        self._extract_artifacts()
        self.logger.success("Download completes.")

    def _trigger_export(self):
        url = f"{self.base_url}/projects/{self.project_id}/artifacts"
        self.client.post(url, headers=self.headers)

    def _download_artifacts(self):
        url = f"{self.base_url}/projects/{self.project_id}/artifacts/download"
        try:
            content = (self.client.get(url, headers=self.headers, follow_redirects=True)).content
        except httpx.ConnectError as e:
            self.logger.error(f"Error downloading artifacts: {e}")
            raise
        with open(settings.filepath.root / settings.filepath.tmp / "paratranz_export.zip", "wb") as fp:
            fp.write(content)

    def _extract_artifacts(self):
        with ZipFile(settings.filepath.root / settings.filepath.tmp / "paratranz_export.zip") as zfp:
            zfp.extractall(settings.filepath.root / settings.filepath.tmp)

        def _ignore(src: str, names: list[str]):
            return ["旧"]
        shutil.copytree(
            settings.filepath.root / settings.filepath.tmp / "utf8",
            settings.filepath.root / settings.filepath.download,
            dirs_exist_ok=True,
            ignore=_ignore
        )

    @property
    def client(self) -> httpx.Client:
        return self._client

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def headers(self) -> dict:
        return self._headers

    @property
    def project_id(self) -> int:
        return self._project_id

    @property
    def logger(self) -> Logger:
        return self._logger


__all__ = [
    'Paratranz'
]
