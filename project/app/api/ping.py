from typing import Annotated

from app.config import Settings, get_settings
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/ping")
async def pong(settings: Annotated[Settings, Depends(get_settings)]):
    return {
        "ping": "pong!",
        "environment": settings.environment,
        "testing": settings.testing,
    }
