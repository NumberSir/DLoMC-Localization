import io
import json
import os
import re
import shutil
from contextlib import suppress
from pathlib import Path
from typing import Callable
from xml.etree.ElementTree import Element, ElementTree

from loguru._logger import Logger
from lxml import etree
from pydantic import BaseModel

from src.config import settings
from src.enum import *
from src.log import logger
from src.model import *

GAME_ROOT = settings.filepath.root / settings.filepath.original / f"{settings.game.name} v{settings.game.version}"
DIR_TRANSLATION = settings.filepath.root / settings.filepath.translation
DIR_CONVERT = settings.filepath.root / settings.filepath.convert
DIR_DOWNLOAD = settings.filepath.root / settings.filepath.download
DIR_RESULT = settings.filepath.root / settings.filepath.result
DIR_SPECIAL = settings.filepath.root / settings.filepath.special

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
        self._restorer = Restorer()

    def clean(self, *filepaths: Path):
        for filepath in filepaths:
            with suppress(FileNotFoundError):
                shutil.rmtree(filepath)
            os.makedirs(filepath, exist_ok=True)
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
    def restorer(self) -> "Restorer":
        return self._restorer

    @property
    def logger(self) -> Logger:
        return self._logger


class Converter:
    """convert local files to paratranz format"""
    def __init__(self):
        self._logger = logger.bind(project_name="Convert")

    def convert(self):
        self.logger.info("")
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
                os.makedirs((DIR_CONVERT / relative_filepath).parent, exist_ok=True)
                converted_filepath = relative_filepath.parent / f"{relative_filepath.name}.json"
                with open(DIR_CONVERT / converted_filepath, "w", encoding="utf-8") as fp:
                    json.dump(datas, fp, ensure_ascii=False, indent=2)
                self.logger.bind(filepath=relative_filepath).debug("Converting file successfully.")

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
        json, similar to common events
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
                event_id = event.id
                event_name = event.name

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
                                key=f"{event_id} | {event_name} | {idx_page} | {idx_unit} | {unit.code}",
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
            game_title_original = original.gameTitle
            game_title_translation = translation.gameTitle if translation_flag else ""
            game_title_translation = game_title_translation if game_title_translation != game_title_original else ""
            models.append(ParatranzModel(key="gameTitle", original=game_title_original, translation=game_title_translation))

            locale_original = original.locale
            locale_translation = translation.locale if translation_flag else ""
            locale_translation = locale_translation if locale_translation != locale_original else ""
            models.append(ParatranzModel(key="locale", original=locale_original, translation=locale_translation))

            for idx, skill_type in enumerate(original.skillTypes):
                if not skill_type:
                    continue
                skill_type_original = skill_type
                skill_type_translation = translation.skillTypes[idx] if translation_flag else ""
                skill_type_translation = skill_type_translation if skill_type_translation != skill_type_original else ""
                models.append(ParatranzModel(key=f"skillTypes | {idx}", original=skill_type_original, translation=skill_type_translation))

            for idx, basic in enumerate(original.terms.basic):
                if not basic:
                    continue
                basic_original = basic
                basic_translation = translation.terms.basic[idx] if translation_flag else ""
                basic_translation = basic_translation if basic_translation != basic_original else ""
                models.append(ParatranzModel(key=f"terms | basic | {idx}", original=basic_original, translation=basic_translation))

            for idx, command in enumerate(original.terms.commands):
                if not command:
                    continue
                command_original = command
                command_translation = translation.terms.commands[idx] if translation_flag else ""
                command_translation = command_translation if command_translation != command_original else ""
                models.append(ParatranzModel(key=f"terms | commands | {idx}", original=command_original, translation=command_translation))

            for idx, param in enumerate(original.terms.params):
                if not param:
                    continue
                param_original = param
                param_translation = translation.terms.params[idx] if translation_flag else ""
                param_translation = param_translation if param_translation != param_original else ""
                models.append(ParatranzModel(key=f"terms | params | {idx}", original=param_original, translation=param_translation))

            for key, value in original.terms.messages.items():
                message_original = value
                message_translation = translation.terms.messages[key] if translation_flag else ""
                message_translation = message_translation if message_translation != message_original else ""
                models.append(ParatranzModel(key=f"terms | messages | {key}", original=message_original, translation=message_translation))

            return models

        return self._convert_general(
            filepath=filepath,
            type_=type_,
            process_function=_process,
        )

    def _convert_items(self, filepath: Path, type_: FileType) -> list[ParatranzModel]:
        """
        json, similar to skills
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
                event_id = event.id
                event_name = event.name
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
                            key=f"{event_id} | {event_name} | {idx_unit} | {unit.code}",
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


class Restorer:
    """restore local files from paratranz result"""
    def __init__(self):
        self._logger = logger.bind(project_name="Restore")

    def restore(self):
        self.logger.info("")
        self.logger.info("======= RESTORE START =======")
        os.makedirs(DIR_DOWNLOAD, exist_ok=True)
        for root, dirs, files in os.walk(DIR_DOWNLOAD):
            for file in files:
                filepath = Path(root) / file
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
                    # TXT
                    case FileType.QUEST:
                        model = self._restore_quest(filepath, file_type)
                    case _:
                        self.logger.bind(filepath=relative_filepath).error("Unknown file type when restore")
                        continue

                if model is None:
                    self.logger.bind(filepath=relative_filepath).warning("Restoring file failed")
                    continue

                os.makedirs((DIR_RESULT / relative_filepath).parent, exist_ok=True)
                if isinstance(model, str):
                    with open(DIR_RESULT / result_filepath, "w", encoding="utf-8") as fp:
                        fp.write(model)
                    self.logger.bind(filepath=relative_filepath).debug("Restoring file successfully.")
                    continue

                elif isinstance(model, list):
                    datas = [m.model_dump() if m is not None else None for m in model]

                else:
                    datas = model.model_dump()

                with open(DIR_RESULT / result_filepath, "w", encoding="utf-8") as fp:
                    json.dump(datas, fp, ensure_ascii=False)
                self.logger.bind(filepath=relative_filepath).debug("Restoring file successfully.")

        self.restore_special()

    def restore_special(self):
        shutil.copytree(DIR_SPECIAL, DIR_RESULT, dirs_exist_ok=True)
        self.logger.debug("Restoring special files successfully.")

    def _restore_general(self, filepath: Path, type_: FileType, process_function: Callable[..., list[BaseModel]|BaseModel|str], **kwargs) -> list[BaseModel] | BaseModel | str:
        relative_filepath = filepath.relative_to(DIR_DOWNLOAD)
        with open(filepath, "r", encoding="utf-8") as fp:
            download = json.load(fp)

        filepath_original = GAME_ROOT / relative_filepath.with_suffix("")
        with open(filepath_original, "r", encoding="utf-8") as fp:
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


    @property
    def logger(self) -> Logger:
        return self._logger


class Special:
    """tiny tweaks"""
    def __init__(self):
        ...

    def tweak_game_title(self):
        with open(GAME_ROOT / "www" / "index.html", encoding="utf-8") as fp:
            root: Element = etree.HTML(fp.read())

        newtitle = etree.Element("title")
        newtitle.text = settings.game.name_translation

        head = root.find("head").__copy__()
        head.remove(head.find("title"))
        head.append(newtitle)

        root.remove(root.find("head"))
        root.insert(0, head,)

        tree: ElementTree = etree.ElementTree(root)
        tree.write(DIR_RESULT / "www" / "index.html", encoding="utf-8", method="html", pretty_print=True)



if __name__ == '__main__':
    special = Special()
    special.tweak_game_title()

