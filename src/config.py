from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class ProjectSettings(BaseSettings):
    """About this project"""
    model_config = SettingsConfigDict(env_prefix="PROJECT_")

    name: str = Field(default="ModrinthApi")
    version: str = Field(default="0.0.1")
    username: str = Field(default="Anonymous")
    email: str = Field(default="anonymous@email.com")
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="<g>{time:HH:mm:ss}</g> | [<lvl>{level:^7}</lvl>] | {extra[project_name]}{message:<35}")


class FilepathSettings(BaseSettings):
    """About files / directories"""
    model_config = SettingsConfigDict(env_prefix="PATH_")

    root: Path = Field(default=Path(__file__).parent.parent)
    data: Path = Field(default=Path("data"))
    tmp: Path = Field(default=Path("data/tmp"))
    log: Path = Field(default=Path("data/log"))
    resource: Path = Field(default=Path("resource"))
    convert: Path = Field(default=Path("resource/paratranz/convert"))
    download: Path = Field(default=Path("resource/paratranz/download"))
    result: Path = Field(default=Path("resource/result"))


class GameSettings(BaseSettings):
    """About the game"""
    model_config = SettingsConfigDict(env_prefix="GAME_")

    name: str = Field(default="Daily Lives of My Countryside")
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


class Settings(BaseSettings):
    """Main settings"""
    paratranz: ParatranzSettings = ParatranzSettings()
    github: GitHubSettings = GitHubSettings()
    project: ProjectSettings = ProjectSettings()
    filepath: FilepathSettings = FilepathSettings()
    game: GameSettings = GameSettings()


settings = Settings()

__all__ = [
    "Settings",
    "settings",
]

if __name__ == '__main__':
    print(Settings().model_dump())
