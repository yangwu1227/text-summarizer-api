from typing import Annotated
from fastapi import Depends, APIRouter
from app.config import get_settings, Settings

router = APIRouter()

@router.get("/ping")
async def pong(settings: Annotated[Settings, Depends(get_settings)]):
    return {
        "ping": "pong!",
        "environment": settings.environment,
        "testing": settings.testing
    }
