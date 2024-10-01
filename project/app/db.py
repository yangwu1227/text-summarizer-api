import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from tortoise import Tortoise, run_async
from tortoise.contrib.fastapi import RegisterTortoise

logger = logging.getLogger("uvicorn")

# Configuration for Tortoise ORM and Aerich migrations: docker compose exec <service-name> aerich init -t app.db.TORTOISE_ORM
TORTOISE_ORM = {
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
    Registers Tortoise ORM within a FastAPI application's lifespan context.

    This method ensures proper setup and teardown of the database connection
    when the application starts and stops. The database schema is not
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
        the database connection and will run teardown tasks on shutdown.
    """
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
