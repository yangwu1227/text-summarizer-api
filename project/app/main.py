import logging

from fastapi import FastAPI

from app.api import ping, summaries
from app.db import lifespan

logger = logging.getLogger("uvicorn")


def create_app() -> FastAPI:
    application = FastAPI(title="text-summarizer", lifespan=lifespan)
    application.include_router(ping.router)
    application.include_router(summaries.router, prefix="/summaries", tags=["summaries"])
    return application


app = create_app()
