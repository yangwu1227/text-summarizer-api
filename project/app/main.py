import logging
import os

from fastapi import FastAPI

from app.api import ping, summaries
from app.db import lifespan

logger = logging.getLogger("uvicorn")


def create_app() -> FastAPI:
    application = FastAPI(
        title="text-summarizer",
        lifespan=lifespan,
        docs_url=os.getenv("ENABLE_DOCS", None),
        redoc_url=None,
    )
    application.include_router(ping.router)
    application.include_router(summaries.router, prefix="/summaries", tags=["summaries"])
    return application


app = create_app()
