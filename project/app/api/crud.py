from typing import Union, Dict, List 
from app.models.pydantic import SummaryPayloadSchema
from app.models.tortoise import TextSummary

async def post(payload: SummaryPayloadSchema) -> int:
    """
    Create a new summary record and save it to the database.

    Parameters
    ----------
    payload : SummaryPayloadSchema
        The payload containing a valid url required to create the new summary.

    Returns
    -------
    int
        The ID of the newly created summary.
    """
    summary = TextSummary(
        url=payload.url,
        summary='summary',
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
