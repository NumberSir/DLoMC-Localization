from typing import Optional

from pydantic import BaseModel, Field


class _BaseModelAllowExtra(BaseModel, extra='allow'):
    ...


class ParatranzModel(_BaseModelAllowExtra):
    """json schema for files uploaded to Paratranz"""
    """primary key"""
    key: str
    """eg: english"""
    original: str
    """eg: chinese"""
    translation: str = Field(default='')
    """as reference"""
    context: str = Field(default='')
    """untranslated, translated, checked, ..."""
    stage: Optional[int] = Field(default=0)

    def untranslated(self) -> bool:
        return not self.translation or self.translation == self.original


""" MAP """
class GameMapUnitModel(_BaseModelAllowExtra):
    code: int
    indent: int
    parameters: list


class GameMapPageModel(_BaseModelAllowExtra):
    list: list[GameMapUnitModel]


class GameMapEventModel(_BaseModelAllowExtra):
    id: int
    name: str
    pages: list[GameMapPageModel]


class GameMapModel(_BaseModelAllowExtra):
    events: list[GameMapEventModel | None]


""" SYSTEM """
class GameSystemTermsModel(_BaseModelAllowExtra):
    basic: list[str]
    commands: list[str | None]
    params: list[str]
    messages: dict[str, str]


class GameSystemModel(_BaseModelAllowExtra):
    gameTitle: str
    locale: str
    skillTypes: list[str]
    terms: GameSystemTermsModel


""" ITEMS """
class GameItemModel(_BaseModelAllowExtra):
    id: int
    description: str
    name: str


""" SKILLS """
class GameSkillModel(_BaseModelAllowExtra):
    id: int
    description: str
    name: str


""" COMMONEVENTS """
class GameCommonEventUnitModel(_BaseModelAllowExtra):
    code: int
    parameters: list


class GameCommonEventModel(_BaseModelAllowExtra):
    id: int
    name: str
    list: list[GameCommonEventUnitModel]


""" PLUGINS """
class GamePluginModel(_BaseModelAllowExtra):
    name: str
    status: bool
    description: str
    parameters: dict



__all__ = [
    'ParatranzModel',

    'GameMapUnitModel',
    'GameMapPageModel',
    'GameMapModel',

    'GameSystemTermsModel',
    'GameSystemModel',

    'GameItemModel',

    'GameSkillModel',

    "GameCommonEventUnitModel",
    "GameCommonEventModel",

    "GamePluginModel",
]