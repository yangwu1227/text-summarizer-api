from enum import Enum

from pydantic import AnyHttpUrl, BaseModel, Field


class SummarizationMethod(str, Enum):
    """
    Enum representing available summarizer options.

    This enum maps to the available summarizer implementations, ensuring that
    only valid summarizer names are used in the request.
    """

    lsa = "lsa"
    lex_rank = "lex_rank"
    text_rank = "text_rank"
    edmundson = "edmundson"


class SummaryPayloadSchema(BaseModel):
    """
    Schema representing the request body to generate a text summary.

    This schema is used to validate incoming requests where the client provides
    a URL, the summarizer name, and optionally the desired number of sentences
    in the summary. The URL must be a valid HTTP or HTTPS URL.

    Attributes
    ----------
    url : AnyHttpUrl
        The URL of the text for which a summary will be generated. This must be a
        valid HTTP or HTTPS URL.
    summarization_method : str
        The name of the summarizer to be used for generating the summary.
    sentence_count : Optional[int]
        The number of sentences to include in the summary. This field is optional.
    """

    url: AnyHttpUrl
    summarization_method: SummarizationMethod = SummarizationMethod.lsa
    sentence_count: int = Field(default=10, ge=5, le=30)


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
    url : AnyHttpUrl
        The URL of the text for which a summary will be generated. This must be a
        valid HTTP or HTTPS URL.
    summarization_method : str
        The name of the summarizer to be used for generating the summary.
    sentence_count : Optional[int]
        The number of sentences to include in the summary. This field is optional.
    """

    id: int


class SummaryUpdatePayloadSchema(BaseModel):
    """
    Schema representing the request body for updating an existing text summary in the database.

    This schema includes a `url` and a `update_summary` field, which contains the updated summary content.
    It is used when clients want to modify the previously generated summary for a specific URL given
    a summary ID.

    Attributes
    ----------
    update_summary : str
        The updated text summary for the provided URL. This field contains the new
        summary content that will replace the previous one.
    url : AnyHttpUrl
        The URL of the text for which a summary will be generated. This must be a
        valid HTTP or HTTPS URL.
    """

    url: AnyHttpUrl
    update_summary: str
