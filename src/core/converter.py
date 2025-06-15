import json
import re
from pathlib import Path
from typing import Callable

from loguru._logger import Logger

from src.config import *
from src.core.project import Project
from src.log import logger
from src.schema import *


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
            for filepath in dir_.iterdir():
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
                    case FileType.MAPINFOS:
                        models = self._convert_map_infos(filepath, file_type)
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
                (DIR_CONVERT / relative_filepath).parent.mkdir(parents=True, exist_ok=True)
                converted_filepath = relative_filepath.parent / f"{relative_filepath.name}.json"
                with (DIR_CONVERT / converted_filepath).open("w", encoding="utf-8") as fp:
                    json.dump(datas, fp, ensure_ascii=False, indent=2)
                self.logger.bind(filepath=relative_filepath).debug("Converting file successfully.")

    def _convert_general(self, filepath: Path, type_: FileType, process_function: Callable[..., list[ParatranzModel]], **kwargs) -> list[ParatranzModel]:
        relative_filepath = filepath.relative_to(GAME_ROOT)
        with filepath.open("r", encoding="utf-8") as fp:
            original = Project().read(fp, type_)

        translation, translation_mapping = None, None
        filepath_translation = DIR_DOWNLOAD / relative_filepath.parent / f"{relative_filepath.name}.json"
        if translation_flag := filepath_translation.exists():
            self.logger.bind(filepath=relative_filepath).debug("Translation exists.")
            with filepath_translation.open("r", encoding="utf-8") as fp:
                translation: list[ParatranzModel] | None = [ParatranzModel.model_validate(_) for _ in json.load(fp)]
                translation_mapping: dict[str, ParatranzModel] | None = {model.key: model for model in translation}

        return process_function(
            filepath=filepath,
            original=original,
            translation=translation,
            translation_mapping=translation_mapping,
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
            translation_flag = kwargs["translation_flag"]
            translation_mapping: dict[str, ParatranzModel] | None = kwargs["translation_mapping"]

            pattern = re.compile(r"(<quest (\d+?):[\s\S]+?\|\d+?\|\d+?>[\s\S]+?</quest>)")
            quests = re.findall(pattern, original)  # [(quest, idx)]

            return [
                ParatranzModel(
                    key=id_,
                    original=quest,
                    translation=(translation_mapping.get(id_, "") if translation_flag else "").translation if translation_mapping.get(id_) else ""
                )
                for quest, id_ in quests
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
            translation: list[ParatranzModel] | None = kwargs["translation"]
            translation_mapping: dict[str, ParatranzModel] | None = kwargs["translation_mapping"]

            def _build_context(idx_unit_: int, code_: Code, flag_: bool, page_: GameMapPageModel):
                context = ""
                if flag_:
                    return flag_, context

                flag_ = True
                idx_ = idx_unit_
                while code_ == page_.list[idx_:][0].code:
                    context += f"\n{page_.list[idx_:][0].parameters[0]}"
                    idx_ += 1
                return flag_, context

            display_name_translation = translation_mapping.get("displayName", "") if translation_flag else ""
            display_name_translation = display_name_translation.translation if display_name_translation else ""
            models = [ParatranzModel(key="displayName", original=original.displayName, translation=display_name_translation)]
            for idx_event, event in enumerate(original.events):
                if event is None:
                    continue
                event_id = event.id
                event_name = event.name

                for idx_page, page in enumerate(event.pages):
                    flag_conversation, flag_choice = False, False
                    for idx_unit, unit in enumerate(page.list):
                        unit_code = unit.code
                        key = f"{event_id} | {event_name} | {idx_page} | {idx_unit} | {unit_code}"
                        if Code.DIALOG == unit_code:
                            original_value = unit.parameters[0]  # str
                            translation_value = [model.translation for model in translation if model.original == original_value] if translation_flag else ""
                            translation_value = translation_value[0] if translation_value else ""
                            flag_conversation, context_conversation = _build_context(idx_unit, Code.DIALOG, flag_conversation, page)
                        elif Code.CHOICE == unit_code:
                            original_value = "\n".join(unit.parameters[0])  # list[str]
                            translation_value = [model.translation for model in translation if model.original == original_value] if translation_flag else ""
                            translation_value = translation_value[0] if translation_value else ""
                            flag_choice, context_choice = _build_context(idx_unit, Code.CHOICE, flag_choice, page)
                        else:
                            flag_conversation, flag_choice = False, False
                            continue

                        model = ParatranzModel(
                            key=key,
                            original=original_value,
                            translation=translation_value,
                            context=context_conversation.strip() if Code.DIALOG == unit_code else context_choice.strip(),
                        )
                        model.context = f'{display_name_translation or original.displayName}\n{model.context}'
                        models.append(model)

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
            translation: list[ParatranzModel] | None = kwargs["translation"]
            translation_mapping: dict[str, ParatranzModel] | None = kwargs["translation_mapping"]

            models = []
            game_title_original = original.gameTitle
            game_title_translation = translation_mapping["gameTitle"].translation if translation_flag else ""
            models.append(ParatranzModel(key="gameTitle", original=game_title_original, translation=game_title_translation))

            locale_original = original.locale
            locale_translation = translation_mapping["locale"].translation if translation_flag else ""
            models.append(ParatranzModel(key="locale", original=locale_original, translation=locale_translation))

            def _convert_lists(list_: list, key_prefix: str, models_: list):
                for idx_, item in enumerate(list_):
                    if not item:
                        continue

                    key_ = f"{key_prefix} | {idx_}"
                    original_ = item
                    translation_ = [model.translation for model in translation if model.original == original_] if translation_flag else ""
                    translation_ = translation_[0] if translation_ else ""
                    models_.append(ParatranzModel(key=key_, original=original_, translation=translation_))
                return models_

            models = _convert_lists(original.skillTypes, "skillTypes", models)
            models = _convert_lists(original.terms.basic, "terms | basic", models)
            models = _convert_lists(original.terms.commands, "terms | commands", models)
            models = _convert_lists(original.terms.params, "terms | params", models)

            for key, value in original.terms.messages.items():
                key = f"terms | messages | {key}"
                message_original = value
                message_translation = translation_mapping.get(key, "") if translation_flag else ""
                message_translation = message_translation.translation if message_translation else ""
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
            translation_mapping: dict[str, ParatranzModel] | None = kwargs["translation_mapping"]

            models = []
            for idx, item in enumerate(original):
                if not any((item.name, item.description)):
                    continue

                if item.name:
                    key = f"{item.id} | name"
                    translation_value = translation_mapping.get(key, "") if translation_flag else ""
                    translation_value = translation_value.translation if translation_value else ""
                    models.append(ParatranzModel(key=key, original=item.name, translation=translation_value, context=f"{item.id} | {item.name}\n{item.description}"))
                if item.description:
                    key = f"{item.id} | description"
                    translation_value = translation_mapping.get(key, "") if translation_flag else ""
                    translation_value = translation_value.translation if translation_value else ""
                    models.append(ParatranzModel(key=key, original=item.description, translation=translation_value, context=f"{item.id} | {item.name}\n{item.description}"))
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
            translation_mapping: dict[str, ParatranzModel] | None = kwargs["translation_mapping"]

            models = []
            for idx, skill in enumerate(original):
                if not any((skill.name, skill.description)):
                    continue

                if skill.name:
                    key = f"{skill.id} | name"
                    translation_value = translation_mapping.get(key, "") if translation_flag else ""
                    translation_value = translation_value.translation if translation_value else ""
                    models.append(ParatranzModel(key=f"{skill.id} | name", original=skill.name, translation=translation_value, context=f"{skill.id} | {skill.name}\n{skill.description}"))
                if skill.description:
                    key = f"{skill.id} | description"
                    translation_value = translation_mapping.get(key, "") if translation_flag else ""
                    translation_value = translation_value.translation if translation_value else ""
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
            translation: list[ParatranzModel] | None = kwargs["translation"]

            def _build_context(idx_unit_: int, code_: Code, flag_: bool, event_: GameCommonEventModel):
                context = ""
                if flag_:
                    return flag_, context

                flag_ = True
                idx_ = idx_unit_
                while code_ == event_.list[idx_:][0].code:
                    context += f"\n{event_.list[idx_:][0].parameters[0]}"
                    idx_ += 1
                return flag_, context

            models = []
            for idx, event in enumerate(original):
                event_id = event.id
                event_name = event.name
                flag_conversation, flag_choice = False, False
                for idx_unit, unit in enumerate(event.list):
                    if Code.DIALOG == unit.code:
                        original_value = unit.parameters[0]  # str
                        translation_value = [model.translation for model in translation if model.original == original_value] if translation_flag else ""
                        translation_value = translation_value[0] if translation_value else ""
                        flag_conversation, context_conversation = _build_context(idx_unit, Code.DIALOG, flag_conversation, event)
                    elif Code.CHOICE == unit.code:
                        original_value = "\n".join(unit.parameters[0])  # list[str]
                        translation_value = [model.translation for model in translation if model.original == original_value] if translation_flag else ""
                        translation_value = translation_value[0] if translation_value else ""
                        flag_choice, context_choice = _build_context(idx_unit, Code.CHOICE, flag_choice, event)
                    else:
                        flag_conversation, flag_choice = False, False
                        continue

                    models.append(
                        ParatranzModel(
                            key=f"{event_id} | {event_name} | {idx_unit} | {unit.code}",
                            original=original_value,
                            translation=translation_value,
                            context=context_conversation.strip() if Code.DIALOG == unit.code else context_choice.strip(),
                        )
                    )
            return models

        return self._convert_general(
            filepath=filepath,
            type_=type_,
            process_function=_process,
        )

    def _convert_map_infos(self, filepath: Path, type_: FileType) -> list[ParatranzModel]:
        """
        special json
        :param filepath: map infos filepath
        :param type_: file type
        :return: array of ParatranzModel
        """
        def _process(**kwargs):
            original: list[GameMapInfoModel | None] = [GameMapInfoModel.model_validate(_) if _ is not None else None for _ in kwargs["original"]]
            translation_flag = kwargs["translation_flag"]
            translation_mapping: dict[str, ParatranzModel] | None = kwargs["translation_mapping"]

            models = []
            for idx, info in enumerate(original):
                if info is None:
                    continue

                translation_value = translation_mapping.get(info.id.__str__(), "") if translation_flag else ""
                translation_value = translation_value.translation if translation_flag else ""
                models.append(ParatranzModel(key=info.id.__str__(), original=info.name, translation=translation_value))

            return models

        return self._convert_general(
            filepath=filepath,
            type_=type_,
            process_function=_process,
        )

    @property
    def logger(self) -> Logger:
        return self._logger


__all__ = [
    "Converter",
]