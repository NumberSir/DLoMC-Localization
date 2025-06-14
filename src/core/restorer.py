import json
import re
import shutil
from pathlib import Path
from typing import Callable

from loguru._logger import Logger
from pydantic import BaseModel

from src.config import *
from src.core.project import Project
from src.log import logger
from src.schema import *


class Restorer:
    """restore local files from paratranz result"""
    def __init__(self):
        self._logger = logger.bind(project_name="Restore")

    def restore(self):
        self.logger.info("")
        self.logger.info("======= RESTORE START =======")
        DIR_DOWNLOAD.mkdir(exist_ok=True, parents=True)
        for filepath in DIR_DOWNLOAD.glob("**/*"):
            if filepath.is_dir():
                continue

            relative_filepath = filepath.relative_to(DIR_DOWNLOAD)
            result_filepath = DIR_RESULT / relative_filepath.with_suffix("")
            file_type = Project().categorize(result_filepath)
            if not file_type:
                continue

            self.logger.bind(filepath=relative_filepath).debug("Restoring file")
            match file_type:
                # JSON
                case FileType.MAP:
                    model = self._restore_map(filepath, file_type)
                case FileType.SYSTEM:
                    model = self._restore_system(filepath, file_type)
                case FileType.ITEMS:
                    model = self._restore_items(filepath, file_type)
                case FileType.SKILLS:
                    model = self._restore_skills(filepath, file_type)
                case FileType.COMMON_EVENTS:
                    model = self._restore_common_events(filepath, file_type)
                case FileType.MAPINFOS:
                    model = self._restore_map_infos(filepath, file_type)
                # TXT
                case FileType.QUEST:
                    model = self._restore_quest(filepath, file_type)
                case _:
                    self.logger.bind(filepath=relative_filepath).error("Unknown file type when restore")
                    continue

            if model is None:
                self.logger.bind(filepath=relative_filepath).warning("Restoring file failed")
                continue

            (DIR_RESULT / relative_filepath).parent.mkdir(exist_ok=True, parents=True)
            if isinstance(model, str):
                with (DIR_RESULT / result_filepath).open("w", encoding="utf-8") as fp:
                    fp.write(model)
                self.logger.bind(filepath=relative_filepath).debug("Restoring file successfully.")
                continue

            elif isinstance(model, list):
                datas = [m.model_dump() if m is not None else None for m in model]

            else:
                datas = model.model_dump()

            with (DIR_RESULT / result_filepath).open("w", encoding="utf-8") as fp:
                json.dump(datas, fp, ensure_ascii=False)
            self.logger.bind(filepath=relative_filepath).debug("Restoring file successfully.")

        self.restore_special()

    def restore_special(self):
        shutil.copytree(DIR_SPECIAL, DIR_RESULT, dirs_exist_ok=True)
        self.logger.debug("Restoring special files successfully.")

    def _restore_general(self, filepath: Path, type_: FileType, process_function: Callable[..., list[BaseModel]|BaseModel|str], **kwargs) -> list[BaseModel] | BaseModel | str:
        relative_filepath = filepath.relative_to(DIR_DOWNLOAD)
        with filepath.open("r", encoding="utf-8") as fp:
            download = json.load(fp)

        filepath_original = GAME_ROOT / relative_filepath.with_suffix("")
        with filepath_original.open("r", encoding="utf-8") as fp:
            original = Project().read(fp, type_)

        return process_function(
            filepath=filepath,
            original=original,
            download=download,
            **kwargs
        )

    def _restore_quest(self, filepath: Path, type_: FileType) -> str:
        def _process(**kwargs):
            original: str = kwargs["original"]
            downloads: list[ParatranzModel] = [ParatranzModel.model_validate(_) for _ in kwargs["download"]]

            pattern = re.compile(r"(<quest (\d+?):[\s\S]+?\|\d+?\|\d+?>[\s\S]+?</quest>)")
            quests = re.findall(pattern, original)  # [(quest, idx)]
            quests_map = {
                idx: quest
                for quest, idx in quests
            }

            for model in downloads:
                if model.untranslated():
                    continue

                quests_map[model.key] = model.translation

            return "\n\n".join(quests_map.values())

        return self._restore_general(
            filepath=filepath,
            type_=type_,
            process_function=_process,
        )

    def _restore_map(self, filepath: Path, type_: FileType) -> BaseModel:
        def _process(**kwargs):
            original: GameMapModel = GameMapModel.model_validate(kwargs["original"])
            downloads: list[ParatranzModel] = [ParatranzModel.model_validate(_) for _ in kwargs["download"]]

            for model in downloads:
                if model.untranslated():
                    continue

                if model.key == "displayName":
                    original.displayName = model.translation
                event_id, event_name, idx_page, idx_unit, unit_code = (_.strip() for _ in model.key.split("|"))
                event_id, idx_page, idx_unit, unit_code = int(event_id), int(idx_page), int(idx_unit), int(unit_code)
                event_name = event_name.strip()

                for idx_event, event in enumerate(original.events):
                    if event is None:
                        continue
                    if any((event_id != event.id, event_name != event.name)):
                        continue

                    for idx_page_, page in enumerate(event.pages):
                        for idx_unit_, unit in enumerate(page.list):
                            if Code.DIALOG == unit.code == unit_code:
                                if model.original != unit.parameters[0]:
                                    continue
                                original.events[idx_event].pages[idx_page_].list[idx_unit_].parameters[0] = model.translation
                            elif Code.CHOICE == unit.code == unit_code:
                                if model.original != "\n".join(unit.parameters[0]):
                                    continue
                                original.events[idx_event].pages[idx_page_].list[idx_unit_].parameters[0] = model.translation.split("\n")

            return original

        return self._restore_general(
            filepath=filepath,
            type_=type_,
            process_function=_process,
        )

    def _restore_system(self, filepath: Path, type_: FileType) -> BaseModel:
        def _process(**kwargs):
            original: GameSystemModel = GameSystemModel.model_validate(kwargs["original"])
            downloads: list[ParatranzModel] = [ParatranzModel.model_validate(_) for _ in kwargs["download"]]

            for model in downloads:
                if model.untranslated():
                    continue

                if model.key == "gameTitle":
                    original.gameTitle = model.translation
                elif model.key == "locale":
                    original.locale = model.translation
                elif model.key.startswith("skillTypes"):
                    for idx, skill_type in enumerate(original.skillTypes):
                        if skill_type != model.original:
                            continue
                        original.skillTypes[idx] = model.translation
                elif model.key.startswith("terms"):
                    if "basic" in model.key:
                        for idx, basic in enumerate(original.terms.basic):
                            if basic != model.original:
                                continue
                            original.terms.basic[idx] = model.translation
                    elif "commands" in model.key:
                        for idx, command in enumerate(original.terms.commands):
                            if command != model.original:
                                continue
                            original.terms.commands[idx] = model.translation
                    elif "params" in model.key:
                        for idx, param in enumerate(original.terms.params):
                            if param != model.original:
                                continue
                            original.terms.params[idx] = model.translation
                    elif "messages" in model.key:
                        for key, value in original.terms.messages.items():
                            if value != model.original:
                                continue
                            original.terms.messages[key] = model.translation
                    else:
                        raise
            return original

        return self._restore_general(
            filepath=filepath,
            type_=type_,
            process_function=_process,
        )

    def _restore_items(self, filepath: Path, type_: FileType) -> list[BaseModel]:
        def _process(**kwargs):
            original: list[GameItemModel] = [GameItemModel.model_validate(_) if _ is not None else _ for _ in kwargs["original"]]
            downloads: list[ParatranzModel] = [ParatranzModel.model_validate(_) for _ in kwargs["download"]]

            for model in downloads:
                if model.untranslated():
                    continue

                item_id, item_type = model.key.split("|")
                item_id = int(item_id)

                for idx, item in enumerate(original):
                    if item is None:
                        continue

                    if item.id != item_id:
                        continue

                    if "name" in item_type:
                        original[idx].name = model.translation
                    elif "description" in item_type:
                        original[idx].description = model.translation
                    else:
                        raise

            return original

        return self._restore_general(
            filepath=filepath,
            type_=type_,
            process_function=_process,
        )

    def _restore_skills(self, filepath: Path, type_: FileType) -> list[BaseModel]:
        def _process(**kwargs):
            original: list[GameSkillModel] = [GameSkillModel.model_validate(_) if _ is not None else _ for _ in kwargs["original"]]
            downloads: list[ParatranzModel] = [ParatranzModel.model_validate(_) for _ in kwargs["download"]]

            for model in downloads:
                if model.untranslated():
                    continue

                skill_id, skill_type = model.key.split("|")
                skill_id = int(skill_id)

                for idx, skill in enumerate(original):
                    if skill is None:
                        continue

                    if skill.id != skill_id:
                        continue

                    if "name" in skill_type:
                        original[idx].name = model.translation
                    elif "description" in skill_type:
                        original[idx].description = model.translation
                    else:
                        raise

            return original

        return self._restore_general(
            filepath=filepath,
            type_=type_,
            process_function=_process,
        )

    def _restore_common_events(self, filepath: Path, type_: FileType) -> list[BaseModel]:
        def _process(**kwargs):
            original: list[GameCommonEventModel] = [GameCommonEventModel.model_validate(_) if _ is not None else _ for _ in kwargs["original"]]
            downloads: list[ParatranzModel] = [ParatranzModel.model_validate(_) for _ in kwargs["download"]]

            for model in downloads:
                if model.untranslated():
                    continue

                event_id, event_name, idx_unit, unit_code = (_.strip() for _ in model.key.split("|"))
                event_id, idx_unit, unit_code = int(event_id), int(idx_unit), int(unit_code)
                event_name = event_name.strip()

                for idx_event, event in enumerate(original):
                    if event is None:
                        continue

                    if any((event_id != event.id, event_name != event.name)):
                        continue

                    for idx_unit_, unit in enumerate(event.list):
                        if Code.DIALOG == unit.code == unit_code:
                            if model.original != unit.parameters[0]:
                                continue
                            original[idx_event].list[idx_unit_].parameters[0] = model.translation
                        elif Code.CHOICE == unit.code == unit_code:
                            if model.original != "\n".join(unit.parameters[0]):
                                continue
                            original[idx_event].list[idx_unit_].parameters[0] = model.translation.split("\n")

            return original

        return self._restore_general(
            filepath=filepath,
            type_=type_,
            process_function=_process,
        )

    def _restore_map_infos(self, filepath: Path, type_: FileType) -> BaseModel:
        def _process(**kwargs):
            original: list[GameMapInfoModel] = [GameMapInfoModel.model_validate(_) if _ is not None else _ for _ in kwargs["original"]]
            downloads: list[ParatranzModel] = [ParatranzModel.model_validate(_) for _ in kwargs["download"]]

            for model in downloads:
                if model.untranslated():
                    continue

                for idx, info in enumerate(original):
                    if info is None:
                        continue
                    if info.id != int(model.key):
                        continue
                    original[idx].name = model.translation
            return original

        return self._restore_general(
            filepath=filepath,
            type_=type_,
            process_function=_process,
        )

    @property
    def logger(self) -> Logger:
        return self._logger


__all__ = [
    "Restorer"
]