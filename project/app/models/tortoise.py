from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class TextSummary(Model):
    """
    A data model representing a summarized text of a given URL. 
    """
    id = fields.IntField(primary_key=True)
    url = fields.TextField()
    summary = fields.TextField()
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

# Build a Pydantic Model off Tortoise Model
SummarySchema = pydantic_model_creator(TextSummary)
