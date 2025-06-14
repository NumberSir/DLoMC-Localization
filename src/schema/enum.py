from enum import Enum, auto


class Code(Enum):
    DIALOG = 401  # str
    CHOICE = 102  # list[str]
    def __eq__(self, other: int):
        return self.value == other


class FileType(Enum):
    QUEST = auto()
    RECIPES = auto()

    MAP = auto()
    SYSTEM = auto()
    MAPINFOS = auto()
    ITEMS = auto()
    SKILLS = auto()
    COMMON_EVENTS = auto()


__all__ = [
    "Code",
    "FileType",
]