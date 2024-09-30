from typing import Dict, List, Union

from app.models.pydantic_model import SummaryPayloadSchema, SummaryUpdatePayloadSchema
from app.models.tortoise_model import TextSummary


async def post(payload: SummaryPayloadSchema) -> int:
    """
    Create a new summary record and save it to the database. The summary field is initially
    left as an empty string and is updated once the background task completes.

    Parameters
    ----------
    payload : SummaryPayloadSchema
        The payload containing a valid url, the string name of the algorithm to use, and optionally
        an integer representing the number of sentences to include in the output.

    Returns
    -------
    int
        The ID of the newly created summary.
    """
    summary = TextSummary(
        url=payload.url,
        summary="",
        summarization_method=payload.summarization_method,
        sentence_count=payload.sentence_count,
    )
    # Create/update the model object
    await summary.save()
    # Return the key
    return summary.id


async def get(id: int) -> Union[Dict, None]:
    """
    Retrieve a summary by its ID from the database.

    Parameters
    ----------
    id : int
        The ID of the summary to retrieve.

    Returns
    -------
    Union[Dict, None]
        A dictionary representation of the summary if found, otherwise None.
    """
    # Generates a QuerySet with the filter applied, limit queryset to one object, and make QuerySet return dicts instead of objects
    summary = await TextSummary.filter(id=id).first().values()
    if summary:
        return summary
    return None


async def get_all() -> List[Dict]:
    """
    Retrieve all summaries from the database.

    Returns
    -------
    List[Dict]
        A list of dictionaries, each representing a summary.
    """
    # All returns the complete QuerySet
    summaries = await TextSummary.all().values()
    return summaries


async def delete(id: int) -> None:
    """
    Delete a summary by its ID from the database.

    Parameters
    ----------
    id : int
        The ID of the summary to delete.

    Returns
    -------
    None
    """
    # First and delete are not coroutines and so awaiting will resolve a single instance of the model object and delete it
    await TextSummary.filter(id=id).first().delete()  # type: ignore
    return None


async def put(id: int, payload: SummaryUpdatePayloadSchema) -> Union[Dict, None]:
    """
    Update a summary in the database by its ID.

    Parameters
    ----------
    id : int
        The ID of the summary to update.
    payload : SummaryUpdatePayloadSchema
        The data to update the summary with, including the new URL and summary text, {"url": ..., "summary": ...}

    Returns
    -------
    Union[Dict, None]
        The updated summary as a dictionary if successful, or None if no summary was found for the given ID.
    """
    # The return object is an instance of UpdateQuery or None depending on if filter finds the given ID
    summary = await TextSummary.filter(id=id).update(
        url=payload.url, summary=payload.update_summary
    )
    if summary:
        # Update and return the updated summary schema {"id": ..., "url": ..., "summary": ...}
        updated_summary_schema = await TextSummary.filter(id=id).first().values()
        return updated_summary_schema
    return None
