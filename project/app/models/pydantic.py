from pydantic import BaseModel


class SummaryPayloadSchema(BaseModel):
    """
    The request body containing the url for which to generate a text summary.
    """
    url: str

class SummaryResponseSchema(SummaryPayloadSchema):
    """
    The response model containing the generated id of the text summary.
    """
    id: int
