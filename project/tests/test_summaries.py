import json
from sys import maxsize

import pytest
from app.api.custom_exceptions import SummaryNotFoundException


class TestSummary(object):
    """
    Tests for GET /summaries, GET /summaries/:id, POST /summaries, PUT /summaries/:id, and DELETE /summaries/:id.
    """

    def test_create_summary(self, test_app_with_db) -> None:
        """
        Test for create_summary on the happy path.
        """
        test_url = "https://yahoo.com/"
        response = test_app_with_db.post("/summaries/", data=json.dumps({"url": test_url}))
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
            # A realistic invalid url
            (
                {"url": "www.article.exmaple.com"},
                # Client-side error: Unprocessable Entity
                422,
                {
                    "detail": [
                        {
                            "type": "url_parsing",
                            "loc": ["body", "url"],
                            "msg": "Input should be a valid URL, relative URL without a base",
                            "input": "www.article.exmaple.com",
                            "ctx": {"error": "relative URL without a base"},
                        }
                    ]
                },
            ),
            # A completely invalid url
            (
                {"url": "invalid://url"},
                # Client-side error: Unprocessable Entity
                422,
                {
                    "detail": [
                        {
                            "type": "url_scheme",
                            "loc": ["body", "url"],
                            "msg": "URL scheme should be 'http' or 'https'",
                            "input": "invalid://url",
                            "ctx": {"expected_schemes": "'http' or 'https'"},
                        }
                    ]
                },
            ),
        ],
        scope="function",
    )
    def test_create_summary_invalid_request(
        self, test_app_with_db, payload, expected_status_code, expected_response
    ) -> None:
        """
        Test for create_summary with invalid request payloads.
        """
        response = test_app_with_db.post("/summaries/", data=json.dumps(payload))
        assert response.status_code == expected_status_code
        print(response.json())
        assert response.json() == expected_response

    def test_read_summary(self, test_app_with_db) -> None:
        """
        Test for read_summary on the happy path.
        """
        test_url = "https://google.com/"
        # Create summary and get the generated ID
        response = test_app_with_db.post("/summaries/", data=json.dumps({"url": test_url}))
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

    @pytest.mark.parametrize(
        "id, expected_status_code, expected_response",
        [
            # Non-existent ID results in 404 not found status code
            (
                maxsize,
                SummaryNotFoundException.status_code,
                {"detail": SummaryNotFoundException.detail},
            ),
            # Invalid ID (i.e. < 1) results in 422 cannot be processed by server status code
            (
                0,
                422,
                {
                    "detail": [
                        {
                            "type": "greater_than",
                            "loc": ["path", "id"],
                            "msg": "Input should be greater than 0",
                            "input": "0",
                            "ctx": {"gt": 0},
                        }
                    ]
                },
            ),
        ],
        scope="function",
    )
    def test_read_summary_invalid_id(
        self, test_app_with_db, id, expected_status_code, expected_response
    ) -> None:
        """
        Test for read_summary when an invalid (non-existent) id is passed.
        """
        response = test_app_with_db.get(f"/summaries/{id}/")
        assert response.status_code == expected_status_code
        assert response.json() == expected_response

    def test_read_all_summaries(self, test_app_with_db) -> None:
        """
        Test for read_all_summaries on the happy path.
        """
        # Post a new url so a record is created in the database
        test_url = "https://fastapi.tiangolo.com/"
        response = test_app_with_db.post("/summaries/", data=json.dumps({"url": test_url}))
        summary_id = response.json()["id"]

        # Get all summaries
        response = test_app_with_db.get("/summaries/")
        assert response.status_code == 200

        # Response is a list of SummarySchema's
        response_list = response.json()
        # Ensure that the newly created text summary is among the list of text summaries
        assert (len(list(filter(lambda summary_schema: summary_schema["id"] == summary_id, response_list))) == 1)  # fmt: skip

    def test_remove_summary(self, test_app_with_db) -> None:
        """
        Test for remove_summary on the happy path.
        """
        test_url = "https://www.python.org/"
        response = test_app_with_db.post("/summaries/", data=json.dumps({"url": test_url}))
        summary_id = response.json()["id"]

        # The response should be a SummaryResponseSchema instance
        response = test_app_with_db.delete(f"/summaries/{summary_id}/")
        assert response.status_code == 200
        assert response.json() == {"id": summary_id, "url": test_url}

    @pytest.mark.parametrize(
        "id, expected_status_code, expected_response",
        [
            # ID is non-existent
            (
                maxsize,
                404,
                {
                    "detail": SummaryNotFoundException.detail,
                },
            ),
            # Id is < 0
            (
                0,
                422,
                {
                    "detail": [
                        {
                            "type": "greater_than",
                            "loc": ["path", "id"],
                            "msg": "Input should be greater than 0",
                            "input": "0",
                            "ctx": {"gt": 0},
                        }
                    ]
                },
            ),
        ],
        scope="function",
    )
    def test_remove_summary_invalid_id(
        self, test_app_with_db, id, expected_status_code, expected_response
    ) -> None:
        """
        Test for remove_summary when an invalid (non-existent) id is passed.
        """
        response = test_app_with_db.delete(f"/summaries/{id}/")
        assert response.status_code == expected_status_code
        assert response.json() == expected_response

    def test_update_summary(self, test_app_with_db) -> None:
        """
        Test for update_summary on the happy path.
        """
        test_url = "https://yahoo.com/"
        response = test_app_with_db.post("/summaries/", data=json.dumps({"url": test_url}))
        summary_id = response.json()["id"]

        response = test_app_with_db.put(
            f"/summaries/{summary_id}/",
            data=json.dumps({"url": test_url, "summary": "Updated summary"}),
        )
        assert response.status_code == 200

        response_data = response.json()
        # Ensure that the id and url match those from the post path operation
        assert response_data["id"] == summary_id
        assert response_data["url"] == test_url
        # The summary and created_at fields should exist, and summary should match the user friendly feedback
        assert response_data["summary"] == "Updated summary"
        assert response_data["created_at"]

    @pytest.mark.parametrize(
        "id, payload, expected_status_code, expected_response",
        [
            # Non-existent ID results in 404 not found status code
            (
                maxsize,
                {"url": "https://google.com/", "summary": "Updated summary"},
                404,
                {
                    "detail": SummaryNotFoundException.detail,
                },
            ),
            # Invalid ID (i.e. < 1) results in 422 cannot be processed by server status code
            (
                0,
                {"url": "https://google.com/", "summary": "Updated summary"},
                422,
                {
                    "detail": [
                        {
                            "type": "greater_than",
                            "loc": ["path", "id"],
                            "msg": "Input should be greater than 0",
                            "input": "0",
                            "ctx": {"gt": 0},
                        }
                    ]
                },
            ),
            # Missing both the url and the update summary in the request body results in 422 status code
            (
                1,
                {},
                422,
                {
                    "detail": [
                        {
                            "type": "missing",
                            "loc": ["body", "url"],
                            "msg": "Field required",
                            "input": {},
                        },
                        {
                            "type": "missing",
                            "loc": ["body", "summary"],
                            "msg": "Field required",
                            "input": {},
                        },
                    ]
                },
            ),
            # Missing just the update summary in the request body results in 422 status code
            (
                1,
                {"url": "https://google.com/"},
                422,
                {
                    "detail": [
                        {
                            "type": "missing",
                            "loc": ["body", "summary"],
                            "msg": "Field required",
                            "input": {"url": "https://google.com/"},
                        }
                    ]
                },
            ),
        ],
        scope="function",
    )
    def test_update_summary_invalid_id_or_request(
        self, test_app_with_db, id, payload, expected_status_code, expected_response
    ) -> None:
        """
        Test for update_summary given invalid id or request body with missing fields.
        """
        response = test_app_with_db.put(f"/summaries/{id}/", data=json.dumps(payload))
        assert response.status_code == expected_status_code
        assert response.json() == expected_response


def test_update_summary_invalid_url(test_app_with_db) -> None:
    """
    Test for update_summary given invalid url in the request body with valid ID and updated summary.
    """
    response = test_app_with_db.put(
        "/summaries/1/",
        data=json.dumps({"url": "invalid://url", "summary": "Updated summary"}),
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "url_scheme",
                "loc": ["body", "url"],
                "msg": "URL scheme should be 'http' or 'https'",
                "input": "invalid://url",
                "ctx": {"expected_schemes": "'http' or 'https'"},
            }
        ]
    }
