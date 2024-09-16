import logging
from functools import lru_cache
from typing import Optional

from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    """
    Configuration settings for the application.

    This class handles configuration settings using Pydantic's BaseSettings. It reads from
    environment variables, including an optional `.env` file, which overrides the default
    values.

    Attributes
    ----------
    model_config : SettingsConfigDict
        Specifies the environment file (.env) and its encoding.
    environment : str
        The environment the application is running in, defaulting to 'dev'.
    testing : bool
        A flag to indicate if the application is in testing mode. Default is False.
    database_url : Optional[AnyUrl]
        The URL for connecting to the database, parsed as an optional AnyUrl.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    environment: str = "dev"
    testing: bool = False
    database_url: Optional[AnyUrl] = None


@lru_cache()
def get_settings() -> Settings:
    """
    Retrieves the application settings.

    This function uses an LRU cache to ensure settings are loaded only once per application
    lifecycle, improving performance. The settings are loaded from environment variables
    and are based on the `Settings` class.

    Returns
    -------
    Settings
        The application settings, loaded from environment variables and optionally an `.env` file.
    """
    logger.info("Loading config settings from the environment...")
    return Settings()
