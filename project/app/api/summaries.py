from typing import Annotated, Dict, List

from fastapi import APIRouter, Path

from app.api import crud
from app.api.custom_exceptions import SummaryNotFoundException
from app.models.pydantic import (
    SummaryPayloadSchema,
    SummaryResponseSchema,
    SummaryUpdatePayloadSchema,
)
from app.models.tortoise import SummarySchema

router = APIRouter()


@router.post("/", response_model=SummaryResponseSchema, status_code=201)
async def create_summary(payload: SummaryPayloadSchema) -> SummaryResponseSchema:
    """
    Create a new summary based on the provided payload.

    Parameters
    ----------
    payload : SummaryPayloadSchema
        The payload containing a valid url required to create the new summary.

    Returns
    -------
    SummaryResponseSchema
        The newly created summary's response, including the summary URL and ID.
    """
    summary_id = await crud.post(payload)
    response = SummaryResponseSchema(
        url=payload.url,
        id=summary_id,
    )
    return response


@router.get("/{id}/", response_model=SummarySchema)
async def read_summary(id: Annotated[int, Path(title="The ID of the text summary to query", gt=0)]) -> SummarySchema:  # type: ignore
    """
    Retrieve a single summary based on its ID (i.e., primary key).

    Parameters
    ----------
    id : int
        The ID of the text summary to query; must be greater than 0.

    Returns
    -------
    SummarySchema
        The retrieved summary object.

    Raises
    ------
    SummaryNotFoundException
        If the summary with the given ID is not found.
    """
    summary = await crud.get(id)
    # Raise a 404 Not Found error if an id is non-existent
    if not summary:
        raise SummaryNotFoundException
    return summary


@router.get("/", response_model=List[SummarySchema])  # type: ignore
async def read_all_summaries() -> List[SummarySchema]:  # type: ignore
    """
    Retrieve all summaries.

    Returns
    -------
    List[SummarySchema]
        A list of all the summaries.
    """
    return await crud.get_all()


@router.delete("/{id}/", response_model=SummaryResponseSchema)
async def remove_summary(
    id: Annotated[int, Path(title="The ID of the text summary to delete", gt=0)]
) -> Dict:
    """
    Delete a single summary based on its ID (i.e., primary key).

    Parameters
    ----------
    id : int
        The ID of the summary to delete; must be greater than 0.

    Returns
    -------
    SummaryResponseSchema
        The retrieved summary response containing an ID and url.

    Raises
    ------
    SummaryNotFoundException
        If the summary with the given ID is not found.
    """
    summary = await crud.get(id)
    # Raise a 404 Not Found error if an id is non-existent
    if not summary:
        raise SummaryNotFoundException
    # Delete the record
    await crud.delete(id)
    return summary


@router.put("/{id}/", response_model=SummarySchema)
async def update_summary(
    id: Annotated[int, Path(title="The ID of the text summary to update", gt=0)],
    payload: SummaryUpdatePayloadSchema,
) -> SummarySchema:  # type:ignore
    """
    Update a text summary by its ID.

    Parameters
    ----------
    id : int
        The ID of the text summary to update; must be greater than 0.
    payload : SummaryUpdatePayloadSchema
        The data to update the summary with, including the new URL and summary text.

    Returns
    -------
    SummarySchema
        The updated summary object if the update is successful.

    Raises
    ------
    SummaryNotFoundException
        If no summary with the specified ID exists.
    """
    summary = await crud.put(id, payload)
    # Raise a 404 Not Found error if an id is non-existent
    if not summary:
        raise SummaryNotFoundException
    return summary
