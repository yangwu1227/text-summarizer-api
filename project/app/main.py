import os
import logging
from fastapi import FastAPI

from app.api import ping, summaries
from app.db import init_db

logger = logging.getLogger("uvicorn")

def create_app() -> FastAPI:
    application = FastAPI(title="text-summarizer")
    application.include_router(ping.router)
    application.include_router(summaries.router, prefix="/summaries", tags=["summaries"])
    return application

app = create_app()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    init_db(app)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")