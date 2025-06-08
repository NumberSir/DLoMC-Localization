import io
import json
import os
import re
import shutil
from contextlib import suppress
from pathlib import Path
from typing import Callable

from loguru._logger import Logger

from src.config import settings
from src.enum import *
from src.log import logger
from src.model import *

GAME_ROOT = settings.filepath.root / settings.filepath.resource / f"{settings.game.name} v{settings.game.version}"
DIR_TRANSLATION = settings.filepath.root / settings.filepath.resource / "translation"

FileContent = str | list | dict


# class SubscribeStar:
#     """作者发布帖子相关"""
#     def __init__(self, client: httpx.AsyncClient):
#         self._mainpage_url = "https://subscribestar.adult/mildasento"
#         self._client = client
#
#     async def download_latest_game(self):
#         """TODO: 下载最新版本，但是因为是 MEGA 盘，有些麻烦"""
#         response = await self._client.get(self._mainpage_url)
#         html_raw = HTML(response.text)
#         latest_link = html_raw.xpath("//strong[contains(string(), 'PUBLIC')]/following-sibling::a/@href")
#         if not latest_link:
#             raise NoDownloadLinkException
#         latest_link = latest_link[0]
#
#         # 下载链接指向的是帖子
#         if not latest_link.startswith("https://subscribestar.adult/posts"):
#             return
#         headers = {
#             "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
#
#         }
#         response = await self._client.get(latest_link, follow_redirects=True, headers=headers)
#         html_raw = HTML(response.text)
#         with open(settings.filepath.root / settings.filepath.tmp / "latest.html", "wb") as fp:
#             fp.write(response.content)
#         mega_url = html_raw.xpath("//a/@data-href[contains(string(), 'mega.nz')]")
#
#         # mega = Mega()
#         # account = mega.login(email="number_sir@126.com", password="52number_sir")
#         # account.download_url(url=mega_url, dest_path=settings.filepath.tmp)


class Project:
    def __init__(self):
        self._logger = logger.bind(project_name="Project")
        self._converter = Converter()

    def clean(self, *filepaths: Path):
        for filepath in filepaths:
            with suppress(FileNotFoundError):
                shutil.rmtree(filepath)
            os.makedirs(filepath, exist_ok=True)
            self.logger.bind(filepath=filepath).debug("Filepath cleaned")

    def categorize(self, filepath: Path) -> FileType | None:
        purename = filepath.with_suffix("").name
        suffix = filepath.suffix

        match suffix:
            case ".txt":
                if purename == "Quests":
                    self.logger.bind(filepath=filepath).debug(f"Type: {FileType.QUEST.name}")
                    return FileType.QUEST
                if purename == "Recipes":
                    self.logger.bind(filepath=filepath).debug(f"Type: {FileType.RECIPES.name}")
                    return FileType.RECIPES

            case ".json":
                if purename.startswith("Map"):
                    if purename == "MapInfos":
                        self.logger.bind(filepath=filepath).debug(f"Type: {FileType.MAPINFO.name}")
                        return FileType.MAPINFO
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

            case _:
                ...

        self.logger.bind(filepath=filepath).error("Unknown filetype when categorize")
        return None

    @staticmethod
    def read(fp: io.TextIOBase, type_: FileType) -> list[str] | str | list | dict:
        match type_:
            case FileType.QUEST | FileType.RECIPES:  # txt
                return fp.read()
            case FileType.MAP | FileType.SYSTEM | FileType.MAPINFO | FileType.ITEMS | FileType.SKILLS | FileType.COMMON_EVENTS:
                return json.load(fp)
            case _:
                raise TypeError

    @property
    def converter(self) -> "Converter":
        return self._converter

    @property
    def logger(self) -> Logger:
        return self._logger


class Converter:
    """convert local json to paratranz format"""
    def __init__(self):
        self._logger = logger.bind(project_name="Convert")

    def convert(self):
        logger.info("")
        self.logger.info("======= CONVERT START =======")
        for dir_ in {
            GAME_ROOT / "www" / "data",
            GAME_ROOT / "www" / "quest"
        }:
            for file in os.listdir(dir_):
                filepath = dir_ / file
                relative_filepath = filepath.relative_to(GAME_ROOT)
                file_type = Project().categorize(relative_filepath)
                if not file_type:
                    continue

                self.logger.bind(filepath=relative_filepath).debug("Converting file")
                match file_type:
                    # JSON
                    case FileType.MAP:
                        models = self._convert_map(filepath, file_type)
                    case FileType.SYSTEM:
                        models = self._convert_system(filepath, file_type)
                    case FileType.ITEMS:
                        models = self._convert_items(filepath, file_type)
                    case FileType.SKILLS:
                        models = self._convert_skills(filepath, file_type)
                    case FileType.COMMON_EVENTS:
                        models = self._convert_common_events(filepath, file_type)
                    # TXT
                    case FileType.QUEST:
                        models = self._convert_quest(filepath, file_type)
                    case _:
                        self.logger.bind(filepath=relative_filepath).error("Unknown file type when convert")
                        continue

                if not models:
                    if models is None:
                        self.logger.bind(filepath=relative_filepath).warning("Converting file failed")
                    else:  # blank
                        self.logger.bind(filepath=relative_filepath).warning("Converting result is blank")
                    continue

                datas = [_.model_dump() for _ in models]
                os.makedirs((settings.filepath.root / settings.filepath.convert / relative_filepath).parent, exist_ok=True)
                with open(settings.filepath.root / settings.filepath.convert / relative_filepath.with_suffix(".json"), "w", encoding="utf-8") as fp:
                    json.dump(datas, fp, ensure_ascii=False, indent=2)
                self.logger.bind(filepath=relative_filepath).success("Converting file successfully.")

    def _convert_general(self, filepath: Path, type_: FileType, process_function: Callable[..., list[ParatranzModel]], **kwargs) -> list[ParatranzModel]:
        relative_filepath = filepath.relative_to(GAME_ROOT)
        with open(filepath, "r", encoding="utf-8") as fp:
            original = Project().read(fp, type_)

        translation = None
        filepath_translation = DIR_TRANSLATION / relative_filepath
        if translation_flag := filepath_translation.exists():
            with open(filepath_translation, "r", encoding="utf-8") as fp:
                translation = Project().read(fp, type_)

        return process_function(
            filepath=filepath,
            original=original,
            translation=translation,
            translation_flag=translation_flag,
            **kwargs
        )

    def _convert_quest(self, filepath: Path, type_: FileType) -> list[ParatranzModel]:
        """
        txt, <game_root>/www/js/plugins/Galv_QuestLog.js
        title, line1 and line2 do not translate
        :param filepath: quest filepath
        :param type_: file type
        :return: array of ParatranzModel
        """
        def _process(**kwargs):
            original: str = kwargs["original"]
            translation: str = kwargs["translation"]
            translation_flag = kwargs["translation_flag"]

            pattern = re.compile(r"(<quest (\d+?):[\s\S]+?\|\d+?\|\d+?>[\s\S]+?</quest>)")
            quests = re.findall(pattern, original)  # [(quest, idx)]
            if translation_flag:
                quests_translation = re.findall(pattern, translation)
                translations = {
                    idx_: quest_translation
                    for quest_translation, idx_ in quests_translation
                }

            return [
                ParatranzModel(
                    key=idx,
                    original=quest,
                    translation=translations[idx] if translation_flag and translations[idx] != quest else ""
                )
                for quest, idx in quests
            ]

        return self._convert_general(
            filepath=filepath,
            type_=type_,
            process_function=_process,
        )

    def _convert_map(self, filepath: Path, type_: FileType) -> list[ParatranzModel]:
        """
        json
        :param filepath: map filepath
        :param type_: file type
        :return: array of ParatranzModel
        """
        def _process(**kwargs):
            original: GameMapModel = GameMapModel.model_validate(kwargs["original"])
            translation_flag = kwargs["translation_flag"]
            translation: GameMapModel = GameMapModel.model_validate(kwargs["translation"]) if translation_flag else None

            models = []
            for idx_event, event in enumerate(original.events):
                if event is None:
                    continue
                id_ = event.id
                name = event.name

                for idx_page, page in enumerate(event.pages):
                    flag_conversation, flag_choice = False, False
                    for idx_unit, unit in enumerate(page.list):
                        if Code.DIALOG == unit.code:
                            original_value = unit.parameters[0]  # str
                            translation_value = translation.events[idx_event].pages[idx_page].list[idx_unit].parameters[0] if translation_flag else ""
                            if not flag_conversation:
                                flag_conversation = True
                                idx_ = idx_unit
                                context_conversation = ""
                                while Code.DIALOG == page.list[idx_:][0].code:
                                    context_conversation += f"\n{page.list[idx_:][0].parameters[0]}"
                                    idx_ += 1
                        elif Code.CHOICE == unit.code:
                            original_value = "\n".join(unit.parameters[0])  # list[str]
                            translation_value = "\n".join(translation.events[idx_event].pages[idx_page].list[idx_unit].parameters[0]) if translation_flag else ""
                            if not flag_choice:
                                flag_choice = True
                                idx_ = idx_unit
                                context_choice = ""
                                while Code.CHOICE == page.list[idx_:][0].code:
                                    context_choice += f"\n{' | '.join(page.list[idx_:][0].parameters[0])}"
                                    idx_ += 1
                        else:
                            flag_conversation, flag_choice = False, False
                            continue

                        models.append(
                            ParatranzModel(
                                key=f"{id_} | {name} | {idx_page} | {idx_unit} | {unit.code}",
                                original=original_value,
                                translation=translation_value if translation_value != original_value else "",
                                context=context_conversation.strip() if Code.DIALOG == unit.code else context_choice.strip(),
                            )
                        )

            return models

        return self._convert_general(
            filepath=filepath,
            type_=type_,
            process_function=_process,
        )

    def _convert_system(self, filepath: Path, type_: FileType) -> list[ParatranzModel]:
        """
        special json
        :param filepath: system filepath
        :param type_: file type
        :return: array of ParatranzModel
        """
        def _process(**kwargs):
            original: GameSystemModel = GameSystemModel.model_validate(kwargs["original"])
            translation_flag = kwargs["translation_flag"]
            translation: GameSystemModel = GameSystemModel.model_validate(kwargs["translation"]) if translation_flag else None

            models = []
            for key, value in original.model_dump().items():
                if isinstance(value, str):
                    translation_value = translation.model_dump()[key] if translation_flag else ""
                    translation_value = translation_value if translation_value != value else ""
                    models.append(ParatranzModel(key=key, original=value, translation=translation_value))
                elif isinstance(value, list):
                    for idx, item in enumerate(value):
                        if not item:
                            continue
                        translation_value = translation.model_dump()[key][idx] if translation_flag else ""
                        translation_value = translation_value if translation_value != item else ""
                        models.append(ParatranzModel(key=f"{key} | {idx}", original=item, translation=translation_value))
                elif isinstance(value, dict):
                    for key_, value_ in original.model_dump()[key].items():
                        if isinstance(value_, list):
                            for idx, item in enumerate(value_):
                                if not item:
                                    continue
                                translation_value = translation.model_dump()[key][key_][idx] if translation_flag else ""
                                translation_value = translation_value if translation_value != item else ""
                                models.append(ParatranzModel(key=f"{key} | {key_} | {idx}", original=item, translation=translation_value))
                        elif isinstance(value_, dict):
                            for key__, value__ in value_.items():
                                translation_value = translation.model_dump()[key][key_][key__] if translation_flag else ""
                                translation_value = translation_value if translation_value != value__ else ""
                                models.append(ParatranzModel(key=f"{key} | {key_} | {key__}", original=value__, translation=translation_value))
                else:
                    raise TypeError

            return models

        return self._convert_general(
            filepath=filepath,
            type_=type_,
            process_function=_process,
        )

    def _convert_items(self, filepath: Path, type_: FileType) -> list[ParatranzModel]:
        """
        json
        :param filepath: items filepath
        :param type_: file type
        :return: array of ParatranzModel
        """
        def _process(**kwargs):
            original: list[GameItemModel] = [GameItemModel.model_validate(_) for _ in kwargs["original"] if _]
            translation_flag = kwargs["translation_flag"]
            translation: list[GameItemModel] = [GameItemModel.model_validate(_) for _ in kwargs["translation"] if _] if translation_flag else None

            models = []
            for idx, item in enumerate(original):
                if not any((item.name, item.description)):
                    continue

                if item.name:
                    translation_value = translation[idx].name if translation_flag else ""
                    translation_value = translation_value if translation_value != item.name else ""
                    models.append(ParatranzModel(key=f"{item.id} | name", original=item.name, translation=translation_value, context=f"{item.id} | {item.name}\n{item.description}"))
                if item.description:
                    translation_value = translation[idx].description if translation_flag else ""
                    translation_value = translation_value if translation_value != item.description else ""
                    models.append(ParatranzModel(key=f"{item.id} | description", original=item.description, translation=translation_value, context=f"{item.id} | {item.name}\n{item.description}"))
            return models

        return self._convert_general(
            filepath=filepath,
            type_=type_,
            process_function=_process,
        )

    def _convert_skills(self, filepath: Path, type_: FileType) -> list[ParatranzModel]:
        """
        json, similar to items
        :param filepath: skills filepath
        :param type_: file type
        :return: array of ParatranzModel
        """
        def _process(**kwargs):
            original: list[GameSkillModel] = [GameSkillModel.model_validate(_) for _ in kwargs["original"] if _]
            translation_flag = kwargs["translation_flag"]
            translation: list[GameSkillModel] = [GameSkillModel.model_validate(_) for _ in kwargs["translation"] if _] if translation_flag else None

            models = []
            for idx, skill in enumerate(original):
                if not any((skill.name, skill.description)):
                    continue

                if skill.name:
                    translation_value = translation[idx].name if translation_flag else ""
                    translation_value = translation_value if translation_value != skill.name else ""
                    models.append(ParatranzModel(key=f"{skill.id} | name", original=skill.name, translation=translation_value, context=f"{skill.id} | {skill.name}\n{skill.description}"))
                if skill.description:
                    translation_value = translation[idx].description if translation_flag else ""
                    translation_value = translation_value if translation_value != skill.description else ""
                    models.append(ParatranzModel(key=f"{skill.id} | description", original=skill.description, translation=translation_value, context=f"{skill.id} | {skill.name}\n{skill.description}"))

            return models

        return self._convert_general(
            filepath=filepath,
            type_=type_,
            process_function=_process,
        )

    def _convert_common_events(self, filepath: Path, type_: FileType) -> list[ParatranzModel]:
        """
        json, similar to maps
        :param filepath: common_events filepath
        :param type_: file type
        :return: array of ParatranzModel
        """
        def _process(**kwargs):
            original: list[GameCommonEventModel] = [GameCommonEventModel.model_validate(_) for _ in kwargs["original"] if _]
            translation_flag = kwargs["translation_flag"]
            translation: list[GameCommonEventModel] = [GameCommonEventModel.model_validate(_) for _ in kwargs["translation"] if _] if translation_flag else None

            models = []
            for idx, event in enumerate(original):
                id_ = event.id
                name = event.name
                flag_conversation, flag_choice = False, False
                for idx_unit, unit in enumerate(event.list):
                    if Code.DIALOG == unit.code:
                        original_value = unit.parameters[0]  # str
                        translation_value = translation[idx].list[idx_unit].parameters[0] if translation_flag else ""
                        if not flag_conversation:
                            flag_conversation = True
                            idx_ = idx_unit
                            context_conversation = ""
                            while Code.DIALOG == event.list[idx_:][0].code:
                                context_conversation += f"\n{event.list[idx_:][0].parameters[0]}"
                                idx_ += 1
                    elif Code.CHOICE == unit.code:
                        original_value = "\n".join(unit.parameters[0])  # list[str]
                        translation_value = "\n".join(translation[idx].list[idx_unit].parameters[0]) if translation_flag else ""
                        if not flag_choice:
                            flag_choice = True
                            idx_ = idx_unit
                            context_choice = ""
                            while Code.CHOICE == event.list[idx_:][0].code:
                                context_choice += f"\n{' | '.join(event.list[idx_:][0].parameters[0])}"
                                idx_ += 1
                    else:
                        flag_conversation, flag_choice = False, False
                        continue

                    models.append(
                        ParatranzModel(
                            key=f"{id_} | {name} | {idx_unit} | {unit.code}",
                            original=original_value,
                            translation=translation_value if translation_value != original_value else "",
                            context=context_conversation.strip() if Code.DIALOG == unit.code else context_choice.strip(),
                        )
                    )
            return models

        return self._convert_general(
            filepath=filepath,
            type_=type_,
            process_function=_process,
        )

    @property
    def logger(self) -> Logger:
        return self._logger


if __name__ == '__main__':
    project = Project()
    project.clean(settings.filepath.root / settings.filepath.tmp)
    project.converter.convert()
