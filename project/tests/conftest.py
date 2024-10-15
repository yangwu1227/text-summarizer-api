import os
from typing import Generator

import pytest
from starlette.testclient import TestClient
from tortoise.contrib.fastapi import register_tortoise

from app.config import Settings, get_settings
from app.custom_rate_limiter import CustomRateLimiter
from app.main import create_app

TestClientGenerator = Generator[TestClient, None, None]


def override_get_settings() -> Settings:
    """
    Override the get_settings dependency to use the test database URL.
    """
    return Settings(testing=True, database_url=os.environ.get("DATABASE_TEST_URL", None))  # type: ignore


@pytest.fixture(scope="module")
def test_app() -> TestClientGenerator:
    """
    Pytest fixture to set up the test application client.

    Yields
    ------
    TestClientGenerator
        A TestClient instance for testing.
    """
    # Use the app.dependency_overrides attribute to override the dependency
    app = create_app()
    app.dependency_overrides[get_settings] = override_get_settings
    # Override all CustomRateLimiter dependencies with no-op for testing
    app.dependency_overrides[CustomRateLimiter(times=5, seconds=60)] = lambda: True
    app.dependency_overrides[CustomRateLimiter(times=3, seconds=60)] = lambda: True
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def test_app_with_db() -> TestClientGenerator:
    """
    Pytest fixture to set up the test application client with an automatically generated database.

    Yields
    ------
    TestClientGenerator
        A TestClient instance for testing.
    """
    # Use the app.dependency_overrides attribute to override the dependency
    app = create_app()
    app.dependency_overrides[get_settings] = override_get_settings
    # Override all CustomRateLimiter dependencies with no-op for testing
    app.dependency_overrides[CustomRateLimiter(times=5, seconds=60)] = lambda: True
    app.dependency_overrides[CustomRateLimiter(times=3, seconds=60)] = lambda: True
    register_tortoise(
        app,
        db_url=os.environ.get("DATABASE_TEST_URL"),
        modules={"models": ["app.models.tortoise_model"]},
        # True to generate schema immediately
        generate_schemas=True,
        add_exception_handlers=True,
    )
    with TestClient(app) as test_client:
        yield test_client
