from typing import Annotated, Dict, Union

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings

router = APIRouter()


@router.get("/ping")
async def pong(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Dict[str, Union[str, bool]]:
    """
    A health check endpoint that returns a simple "ping" response.
    """
    return {
        "ping": "pong!",
        "environment": settings.environment,
        "testing": settings.testing,
    }
