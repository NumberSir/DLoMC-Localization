import io
import json
import shutil
from contextlib import suppress
from pathlib import Path
from zipfile import ZipFile as zf, ZIP_DEFLATED

from loguru._logger import Logger

from src.config import settings, DIR_RESULT
from src.core.paratranz import Paratranz
from src.log import logger
from src.schema.enum import FileType
from src.schema.model import ParatranzProjectModel


class Project:
    def __init__(self):
        self._logger = logger.bind(project_name="Project")

    def check_structure(self):
        """check if necessary files exist"""
        if not (settings.filepath.root / settings.filepath.original).exists():
            raise

    def clean(self, *filepaths: Path):
        for filepath in filepaths:
            with suppress(FileNotFoundError):
                shutil.rmtree(filepath)
            filepath.mkdir(exist_ok=True, parents=True)
            self.logger.bind(filepath=filepath).debug("Filepath cleaned")

    def categorize(self, filepath: Path) -> FileType | None:
        purename = filepath.with_suffix("").name

        if purename == "Quests":
            self.logger.bind(filepath=filepath).debug(f"Type: {FileType.QUEST.name}")
            return FileType.QUEST
        if purename == "Recipes":
            self.logger.bind(filepath=filepath).debug(f"Type: {FileType.RECIPES.name}")
            return FileType.RECIPES

        if purename.startswith("Map"):
            if purename == "MapInfos":
                self.logger.bind(filepath=filepath).debug(f"Type: {FileType.MAPINFOS.name}")
                return FileType.MAPINFOS
            if "Copy" not in purename:
                self.logger.bind(filepath=filepath).debug(f"Type: {FileType.MAP.name}")
                return FileType.MAP
        if purename == "System":
            self.logger.bind(filepath=filepath).debug(f"Type: {FileType.SYSTEM.name}")
            return FileType.SYSTEM
        if purename == "Items":
            self.logger.bind(filepath=filepath).debug(f"Type: {FileType.ITEMS.name}")
            return FileType.ITEMS
        if purename == "Skills":
            self.logger.bind(filepath=filepath).debug(f"Type: {FileType.SKILLS.name}")
            return FileType.SKILLS
        if purename == "CommonEvents":
            self.logger.bind(filepath=filepath).debug(f"Type: {FileType.COMMON_EVENTS.name}")
            return FileType.COMMON_EVENTS

        self.logger.bind(filepath=filepath).error("Unknown filetype when categorize")
        return None

    def read(self, fp: io.TextIOWrapper, type_: FileType) -> list[str] | str | list | dict:
        match type_:
            case FileType.QUEST | FileType.RECIPES:  # txt
                self.logger.debug(f"Reading {type_}")
                return fp.read()
            case FileType.MAP | FileType.SYSTEM | FileType.MAPINFOS | FileType.ITEMS | FileType.SKILLS | FileType.COMMON_EVENTS:  # noqa: E501
                self.logger.debug(f"Reading {type_}")
                return json.load(fp)
            case _:
                self.logger.error(f"Reading unknown type failed: {type_}")
                raise TypeError

    def package(self):
        """package result to zip file # TODO: with password"""
        (settings.filepath.root / settings.filepath.dist).mkdir(parents=True, exist_ok=True)
        model: ParatranzProjectModel = Paratranz().get_project_info()
        filename = (
            f"[汉化词典] "
            f"v{settings.game.version}"
            f"-chs"
            f"-{settings.project.version}"
            f"-{model.stats.tp*10000:.0f}"
            f"-{model.stats.cp*10000:.0f}"
            f".zip"
        )
        with zf(settings.filepath.root / settings.filepath.dist / filename, "w", compresslevel=9, compression=ZIP_DEFLATED) as zfp:  # noqa: E501
            for filepath in DIR_RESULT.glob("**/*"):
                if filepath.is_dir():
                    continue
                zfp.write(
                    filename=filepath,
                    arcname=filepath.relative_to(DIR_RESULT),
                    compresslevel=9
                )
        self.logger.bind(filepath=settings.filepath.dist / filename).success("Successfully package Chinese patch.")

    @property
    def logger(self) -> Logger:
        return self._logger


__all__ = [
    "Project"
]