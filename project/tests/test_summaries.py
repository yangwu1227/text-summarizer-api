import json
from sys import maxsize

import pytest

from app.api.custom_exceptions import SummaryNotFoundException


class TestSummary(object):
    """
    Tests for GET /summaries, GET /summaries/:id, and POST /summaries.
    """

    def test_create_summary(self, test_app_with_db) -> None:
        """
        Test for create_summary on the happy path.
        """
        test_url = "https://yahoo.com"
        response = test_app_with_db.post(
            "/summaries/", data=json.dumps({"url": test_url})
        )
        assert response.status_code == 201
        assert response.json()["url"] == test_url

    @pytest.mark.parametrize(
        "payload, expected_status_code, expected_response",
        [
            (
                {},
                # Client-side error: Unprocessable Entity
                422,
                {
                    "detail": [
                        {
                            "type": "missing",
                            "loc": ["body", "url"],
                            "msg": "Field required",
                            "input": {},
                        }
                    ]
                },
            ),
            (
                {"url": 12},
                # Client-side error: Unprocessable Entity
                422,
                {
                    "detail": [
                        {
                            "type": "string_type",
                            "loc": ["body", "url"],
                            "msg": "Input should be a valid string",
                            "input": 12,
                        }
                    ]
                },
            ),
        ],
    )
    def test_create_summary_invalid_request(
        self, test_app, payload, expected_status_code, expected_response
    ) -> None:
        """
        Test for create_summary with invalid request payloads.
        """
        response = test_app.post("/summaries/", data=json.dumps(payload))
        assert response.status_code == expected_status_code
        print(response.json())
        assert response.json() == expected_response

    def test_read_summary(self, test_app_with_db) -> None:
        """
        Test for read_summary on the happy path.
        """
        test_url = "https://google.com"
        # Create summary and get the generated ID
        response = test_app_with_db.post(
            "/summaries/", data=json.dumps({"url": test_url})
        )
        summary_id = response.json()["id"]

        # Response for a get operation
        response = test_app_with_db.get(f"/summaries/{summary_id}")
        assert response.status_code == 200

        response_data = response.json()
        # The id field should match that from the SummaryResponseSchema
        assert response_data["id"] == summary_id
        # The url field should match
        assert response_data["url"] == test_url
        # The summary and created_at fields should exist
        assert response_data["summary"]
        assert response_data["created_at"]

    def test_read_summary_invalid_id(self, test_app_with_db) -> None:
        """
        Test for read_summary when an invalid (non-existent) id is passed.
        """
        response = test_app_with_db.get(f"/summaries/{maxsize}/")
        assert response.status_code == SummaryNotFoundException.status_code
        assert response.json()["detail"] == SummaryNotFoundException.detail

    def test_read_all_summaries(self, test_app_with_db) -> None:
        """
        Test for read_all_summaries on the happy path.
        """
        # Post a new url so a record is created in the database
        test_url = "https://fastapi.tiangolo.com/"
        response = test_app_with_db.post(
            "/summaries/", data=json.dumps({"url": test_url})
        )
        summary_id = response.json()["id"]

        # Get all summaries
        response = test_app_with_db.get("/summaries/")
        assert response.status_code == 200

        # Response is a list of SummarySchema's
        response_list = response.json()
        # Ensure that the newly created text summary is among the list of text summaries
        assert (
            len(
                list(
                    filter(
                        lambda summary_schema: summary_schema["id"] == summary_id,
                        response_list,
                    )
                )
            )
            == 1
        )
