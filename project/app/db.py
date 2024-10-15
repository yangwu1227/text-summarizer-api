import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from urllib.parse import quote

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from tortoise import Tortoise, run_async
from tortoise.contrib.fastapi import RegisterTortoise

logger = logging.getLogger("uvicorn")

# Configuration for Tortoise ORM and Aerich migrations: docker compose exec <service-name> aerich init -t app.db.TORTOISE_ORM
TORTOISE_ORM = {
    # During production, the DATABASE_URL environment variable is automatically set by Heroku
    "connections": {"default": os.getenv("DATABASE_URL")},
    "apps": {
        "models": {
            "models": ["app.models.tortoise_model", "aerich.models"],
            "default_connection": "default",
        },
    },
}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Registers Tortoise ORM and Redis for rate limiting within a FastAPI application's
    lifespan context.

    This method ensures proper setup and teardown of both the database connection
    and Redis when the application starts and stops. The database schema is not
    generated immediately (suitable for production), and exception handlers
    for `DoesNotExist` and `IntegrityError` are optionally added.

    Parameters
    ----------
    app : FastAPI
        The FastAPI application instance.

    Yields
    ------
    None
        This generator yields control to the application after setting up
        the database connection and Redis for rate limiting. The database
        connection is closed and Redis is disconnected when the application
        stops.
    """
    # Initialize Redis for rate limiting
    redis_endpoint = os.getenv("REDIS_ENDPOINT")
    redis_encoded_password = quote(os.getenv("REDIS_PASSWORD"), safe="")  # type: ignore[arg-type]
    redis_url = f"redis://:{redis_encoded_password}@{redis_endpoint}"
    # The usename, password, hostname, etc. are all passed through urllib.parse.unquote internally
    redis_connection = redis.from_url(redis_url, encoding="utf8")  # type: ignore[no-untyped-call]
    await FastAPILimiter.init(redis_connection)

    # Registers Tortoise-ORM with set-up and tear-down inside a FastAPI application’s lifespan
    async with RegisterTortoise(
        app=app,
        db_url=os.environ.get("DATABASE_URL"),
        modules={"models": ["app.models.tortoise_model"]},
        # Do not generate schema immediately for production
        generate_schemas=False,
        # True to add some automatic exception handlers for DoesNotExist & IntegrityError, not recommended for production
        add_exception_handlers=True,
    ):
        # DB connected
        yield
        # App teardown
    # Closed connection

    # Teardown: Close Redis connection (warning is issued since fastapi_limiter calls the close method, which is deprecated in favor of aclose)
    await FastAPILimiter.close()


async def generate_schema() -> None:
    """
    Initializes Tortoise ORM and generates database schema.

    This function connects to the database using the Tortoise ORM,
    initializes models, and generates the database schema based on
    the models defined. It is intended to be run manually to apply
    schema changes.
    """
    logger.info("Initializing Tortoise...")

    await Tortoise.init(
        db_url=os.environ.get("DATABASE_URL"),
        modules={"models": ["models.tortoise"]},
    )
    logger.info("Generating database schema via Tortoise...")
    await Tortoise.generate_schemas()
    # This is not strictly needed as `run_async` will ensure that connections are closed
    await Tortoise.close_connections()


if __name__ == "__main__":

    run_async(generate_schema())
