from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class TextSummary(Model):
    """
    A data model representing a summarized version of text content from a given URL.

    This model stores the original URL and the generated summary, along with the
    timestamp of when the summary was created. It is built using Tortoise ORM, which
    allows for easy database integration with the FastAPI framework.

    Attributes
    ----------
    id : int
        The primary key, uniquely identifying each summary entry.
    url : str
        The original URL of the text that is being summarized.
    summary : str
        The summarized content extracted from the given URL.
    created_at : datetime
        A timestamp that records when the summary was created. It is automatically
        set to the current date and time upon object creation.
    """

    id = fields.IntField(primary_key=True)
    url = fields.TextField()
    summary = fields.TextField()
    # Allow null to handle existing records before these were added to the schema
    summarization_method = fields.TextField(null=True)
    sentence_count = fields.IntField(null=True)
    # Automatically set the field to now when the object is first created
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self) -> str:
        """
        Returns the URL as a string representation of the object.

        Returns
        -------
        str
            The URL of the text summary.
        """
        return self.url


"""
This is a Pydantic model created from the `TextSummary` Tortoise model.

This schema can be used to validate data for both incoming requests and outgoing responses 
in a FastAPI application. It ensures that the fields from the Tortoise ORM model are properly 
validated when used within API endpoints.
"""
TextSummarySchema = pydantic_model_creator(TextSummary)
