from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class ProjectSettings(BaseSettings):
    """About this project"""
    model_config = SettingsConfigDict(env_prefix="PROJECT_")

    name: str = Field(default="DLoMC-Localization")
    version: str = Field(default="0.0.1")
    username: str = Field(default="Anonymous")
    email: str = Field(default="anonymous@email.com")
    log_level: str = Field(default="INFO")
    log_format: str = Field(
        default="<g>{time:HH:mm:ss}</g> | [<lvl>{level:^7}</lvl>] | {extra[project_name]}{message:<35}"
    )

    @property
    def user_agent(self) -> str:
        return (
            f"{self.username}/"
            f"{self.name}/"
            f"{self.version} "
            f"({self.email})"
        )


class FilepathSettings(BaseSettings):
    """About files / directories"""
    model_config = SettingsConfigDict(env_prefix="PATH_")

    root: Path = Field(default=Path(__file__).parent.parent)
    data: Path = Field(default=Path("data"))
    tmp: Path = Field(default=Path("data/tmp"))
    log: Path = Field(default=Path("data/log"))
    dist: Path = Field(default=Path("dist"))
    resource: Path = Field(default=Path("resource"))
    original: Path = Field(default=Path("resource/01-original"))
    convert: Path = Field(default=Path("resource/02-paratranz/convert"))
    download: Path = Field(default=Path("resource/02-paratranz/download"))
    result: Path = Field(default=Path("resource/03-result"))
    special: Path = Field(default=Path("resource/04-special-file"))


class GameSettings(BaseSettings):
    """About the game"""
    model_config = SettingsConfigDict(env_prefix="GAME_")

    name: str = Field(default="Daily Lives of My Countryside")
    name_translation: str = Field(default="我的乡村日常生活")
    version: str = Field(default="")


class GitHubSettings(BaseSettings):
    """About GitHub"""
    model_config = SettingsConfigDict(env_prefix='GITHUB_')

    access_token: str = Field(default="")


class ParatranzSettings(BaseSettings):
    """About Paratranz"""
    model_config = SettingsConfigDict(env_prefix='PARATRANZ_')

    project_id: str = Field(default="")
    token: str = Field(default="")


# TODO: Download the latest game automatically
# class SubscribeStarSettings(BaseSettings):
#     """About SubscribeStar"""
#     model_config = SettingsConfigDict(env_prefix='SUBSCRIBE_STAR_')
#     email: str = Field(default="")
#     password: str = Field(default="")


class Settings(BaseSettings):
    """Main settings"""
    # subscribestar: SubscribeStarSettings = SubscribeStarSettings()
    paratranz: ParatranzSettings = ParatranzSettings()
    github: GitHubSettings = GitHubSettings()
    project: ProjectSettings = ProjectSettings()
    filepath: FilepathSettings = FilepathSettings()
    game: GameSettings = GameSettings()


settings = Settings()
GAME_ROOT = settings.filepath.root / settings.filepath.original / f"{settings.game.name} v{settings.game.version}"
DIR_CONVERT = settings.filepath.root / settings.filepath.convert
DIR_DOWNLOAD = settings.filepath.root / settings.filepath.download
DIR_RESULT = settings.filepath.root / settings.filepath.result
DIR_SPECIAL = settings.filepath.root / settings.filepath.special

__all__ = [
    "Settings",
    "settings",

    "GAME_ROOT",
    "DIR_CONVERT",
    "DIR_DOWNLOAD",
    "DIR_RESULT",
    "DIR_SPECIAL",
]

if __name__ == '__main__':
    from pprint import pprint
    pprint(Settings().model_dump())
    pprint(settings.project.user_agent)
