from pydantic import AnyHttpUrl, BaseModel


class SummaryPayloadSchema(BaseModel):
    """
    The request body containing the url for which to generate a text summary.
    """

    url: AnyHttpUrl


class SummaryResponseSchema(SummaryPayloadSchema):
    """
    The response model containing the generated id of the text summary.
    """

    id: int


class SummaryUpdatePayloadSchema(SummaryPayloadSchema):
    """
    The request body containing the updated summary for updating the text summary.
    """

    summary: str
