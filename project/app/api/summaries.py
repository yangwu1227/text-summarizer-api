from typing import Annotated, List

from fastapi import APIRouter, BackgroundTasks, Depends, Path

from app.api import crud
from app.api.custom_exceptions import SummaryNotFoundException
from app.custom_rate_limiter import CustomRateLimiter
from app.models.pydantic_model import (
    SummaryPayloadSchema,
    SummaryResponseSchema,
    SummaryUpdatePayloadSchema,
)
from app.models.tortoise_model import TextSummarySchema
from app.summarizer import generate_summary

router = APIRouter()


@router.post(
    "/",
    response_model=SummaryResponseSchema,
    status_code=201,
    dependencies=[Depends(CustomRateLimiter(times=5, seconds=60))],
)
async def create_summary(
    payload: SummaryPayloadSchema, background_tasks: BackgroundTasks
) -> SummaryResponseSchema:
    """
    Create a new summary based on the provided payload.

    Parameters
    ----------
    payload : SummaryPayloadSchema
        The payload containing a valid url required to create the new summary.
    background_tasks : BackgroundTasks
        A collection of background tasks that will be called after a response has been sent to the client.

    Returns
    -------
    SummaryResponseSchema
        The newly created summary's response, including the `url`, `id`, `summarization_method`, and `sentence_count`.
    """
    summary_id = await crud.post(payload)
    # Generate summary as a background task
    background_tasks.add_task(
        generate_summary,
        summary_id,
        str(payload.url),
        payload.summarization_method,
        int(payload.sentence_count),
    )
    response = SummaryResponseSchema(
        url=payload.url,
        id=summary_id,
        summarization_method=payload.summarization_method,
        sentence_count=payload.sentence_count,
    )
    return response


@router.get(
    "/{id}/",
    response_model=TextSummarySchema,
    dependencies=[Depends(CustomRateLimiter(times=3, seconds=60))],
)
async def read_summary(id: Annotated[int, Path(title="The ID of the text summary to query", gt=0)]) -> TextSummarySchema:  # type: ignore
    """
    Retrieve a single summary based on its ID (i.e., primary key).

    Parameters
    ----------
    id : int
        The ID of the text summary to query; must be greater than 0.

    Returns
    -------
    TextSummarySchema
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


@router.get(
    "/",
    response_model=List[TextSummarySchema],  # type: ignore
    dependencies=[Depends(CustomRateLimiter(times=3, seconds=60))],
)
async def read_all_summaries() -> List[TextSummarySchema]:  # type: ignore
    """
    Retrieve all summaries.

    Returns
    -------
    List[TextSummarySchema]
        A list of all the summaries.
    """
    return await crud.get_all()


@router.delete(
    "/{id}/",
    response_model=TextSummarySchema,
)
async def remove_summary(
    id: Annotated[int, Path(title="The ID of the text summary to delete", gt=0)]
) -> TextSummarySchema:  # type: ignore
    """
    Delete a single summary based on its ID (i.e., primary key).

    Parameters
    ----------
    id : int
        The ID of the summary to delete; must be greater than 0.

    Returns
    -------
    TextSummarySchema
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
    # Return the summary record that was deleted
    return summary


@router.put(
    "/{id}/",
    response_model=TextSummarySchema,
)
async def update_summary(
    id: Annotated[int, Path(title="The ID of the text summary to update", gt=0)],
    payload: SummaryUpdatePayloadSchema,
) -> TextSummarySchema:  # type:ignore
    """
    Update a text summary by its ID. Both the URL and the summary text are updated based on the provided payload.

    Parameters
    ----------
    id : int
        The ID of the text summary to update; must be greater than 0.
    payload : SummaryUpdatePayloadSchema
        The data to update the summary with, including the new URL and summary text.

    Returns
    -------
    TextSummarySchema
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
