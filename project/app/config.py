import logging
from functools import lru_cache
from typing import Optional

from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    """
    Configuration settings for the application.

    Attributes
    ----------
    model_config : SettingsConfigDict
        Specifies the environment file (.env) and its encoding.
    environment : str
        The environment the application is running in (default is 'dev').
    testing : bool
        A flag to indicate if the application is in testing mode (default is False).
    database_url : Optional[AnyUrl]
        The URL for connecting to the database.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    environment: str = "dev"
    testing: bool = False
    database_url: Optional[AnyUrl] = None


@lru_cache()
def get_settings() -> Settings:
    logger.info("Loading config settings from the environment...")
    return Settings()
