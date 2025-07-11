import contextlib
import shutil
from pathlib import Path
from zipfile import ZipFile, BadZipFile

import httpx
from loguru._logger import Logger

from src.config import settings
from src.log import logger
from src.schema.model import ParatranzProjectModel


class Paratranz:
    def __init__(self, client: httpx.Client = httpx.Client()):
        self._logger = logger.bind(project_name="Paratranz")
        self._client = client
        self._base_url = "https://paratranz.cn/api"
        self._headers = {
            "Authorization": settings.paratranz.token,
            "user-agent": settings.project.user_agent,
        }
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

    def get_project_info(self) -> ParatranzProjectModel:
        url = f"{self.base_url}/projects/{self.project_id}"
        response = self.client.get(url, headers=self.headers)
        self.logger.success("Get project info successfully")
        return ParatranzProjectModel.model_validate(response.json())

    def download(self):
        self.logger.info("Starting to download translated files...")
        (settings.filepath.root / settings.filepath.tmp).mkdir(parents=True, exist_ok=True)
        (settings.filepath.root / settings.filepath.download).mkdir(parents=True, exist_ok=True)
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

        self.logger.info(f"Artifact size: {len(content)}")
        if len(content) <= 52:
            self.logger.bind(filepath=content).warning("Artifact size too small")
        with open(settings.filepath.root / settings.filepath.tmp / "paratranz_export.zip", "wb") as fp:
            fp.write(content)

    def _extract_artifacts(self):
        try:
            with ZipFile(settings.filepath.root / settings.filepath.tmp / "paratranz_export.zip") as zfp:
                zfp.extractall(settings.filepath.root / settings.filepath.tmp)
        except BadZipFile as e:
            self.logger.error(f"Download artifact might failed due to some reason, try again: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error opening artifacts: {e}")
            raise

        shutil.copytree(
            settings.filepath.root / settings.filepath.tmp / "utf8",
            settings.filepath.root / settings.filepath.download,
            dirs_exist_ok=True
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


if __name__ == '__main__':
    result = Paratranz().get_project_info()
    print(result)
