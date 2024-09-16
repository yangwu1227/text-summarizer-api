from pydantic import AnyHttpUrl, BaseModel


class SummaryPayloadSchema(BaseModel):
    """
    Schema representing the request body to generate a text summary.

    This schema is used to validate incoming requests where the client provides
    a URL. The URL must be a valid HTTP or HTTPS URL. This schema serves as
    the base model for other request and response schemas.

    Attributes
    ----------
    url : AnyHttpUrl
        The URL of the text for which a summary will be generated. This must be a
        valid HTTP or HTTPS URL.
    """

    url: AnyHttpUrl


class SummaryResponseSchema(SummaryPayloadSchema):
    """
    Schema representing the response containing the generated summary ID.

    This schema extends the `SummaryPayloadSchema` by including an additional `id`
    field, representing the unique identifier of the text summary that has been
    generated. This is used when responding to the client with the summary
    creation result.

    Attributes
    ----------
    id : int
        The unique identifier of the generated text summary. This is returned in
        response to a successful summary generation request with 201 status code.
    """

    id: int


class SummaryUpdatePayloadSchema(SummaryPayloadSchema):
    """
    Schema representing the request body for updating an existing text summary in the database.

    This schema extends the `SummaryPayloadSchema` by including an additional `summary`
    field, which contains the updated summary content. It is used when clients want to
    modify the previously generated summary for a specific URL given a summary ID.

    Attributes
    ----------
    summary : str
        The updated text summary for the provided URL. This field contains the new
        summary content that will replace the previous one.
    """

    summary: str
