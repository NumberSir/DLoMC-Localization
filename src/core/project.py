import io
import json
import shutil
from contextlib import suppress
from pathlib import Path

from loguru._logger import Logger

from src.log import logger
from src.schema import *


class Project:
    def __init__(self):
        self._logger = logger.bind(project_name="Project")

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
            case FileType.MAP | FileType.SYSTEM | FileType.MAPINFOS | FileType.ITEMS | FileType.SKILLS | FileType.COMMON_EVENTS:
                self.logger.debug(f"Reading {type_}")
                return json.load(fp)
            case _:
                self.logger.error(f"Reading unknown type failed: {type_}")
                raise TypeError

    @property
    def converter(self) -> "Converter":
        return self._converter

    @property
    def restorer(self) -> "Restorer":
        return self._restorer

    @property
    def tweaker(self) -> "Tweaker":
        return self._tweaker

    @property
    def logger(self) -> Logger:
        return self._logger


__all__ = [
    "Project"
]