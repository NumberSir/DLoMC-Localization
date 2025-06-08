from typing import Optional

from pydantic import BaseModel, Field


class ParatranzModel(BaseModel):
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
    stage: Optional[int] = Field(default=None)


""" MAP """
class GameMapUnitModel(BaseModel):
    code: int
    indent: int
    parameters: list


class GameMapPageModel(BaseModel):
    list: list[GameMapUnitModel]


class GameMapEventModel(BaseModel):
    id: int
    name: str
    pages: list[GameMapPageModel]


class GameMapModel(BaseModel):
    events: list[GameMapEventModel | None]


""" SYSTEM """
class GameSystemTermsModel(BaseModel):
    basic: list[str]
    commands: list[str | None]
    params: list[str]
    messages: dict[str, str]


class GameSystemModel(BaseModel):
    gameTitle: str
    locale: str
    skillTypes: list[str]
    terms: GameSystemTermsModel


""" ITEMS """
class GameItemModel(BaseModel):
    id: int
    description: str
    name: str


""" SKILLS """
class GameSkillModel(BaseModel):
    id: int
    description: str
    name: str


""" COMMONEVENTS """
class GameCommonEventUnitModel(BaseModel):
    code: int
    parameters: list


class GameCommonEventModel(BaseModel):
    id: int
    name: str
    list: list[GameCommonEventUnitModel]



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
]