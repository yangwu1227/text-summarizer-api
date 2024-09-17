import json
from datetime import datetime, timedelta, timezone
from sys import maxsize
from typing import Dict, List, Union

import pytest

from app.api import crud, summaries
from app.api.custom_exceptions import SummaryNotFoundException
from app.models import pydantic


class TestSummaryUnit(object):
    """
    Tests for GET /summaries, GET /summaries/:id, POST /summaries, PUT /summaries/:id, and DELETE /summaries/:id that does not invovle a database test client. This is
    accomplished via monkey patching all CRUD operations.
    """

    def test_create_summary_unit(self, test_app, monkeypatch) -> None:
        """
        Test for create_summary on the happy path.
        """

        # Monkeypatch the generate summary function
        def mock_generate_summary(summary_id, url, summarization_method, sentence_count) -> None:
            return None

        monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)

        # Monkeypatch the crud function
        async def mock_post(payload: pydantic.SummaryPayloadSchema) -> int:
            return 1

        monkeypatch.setattr(crud, "post", mock_post)

        test_request_payload = {
            "url": "https://google.com/",
            "summarization_method": "lsa",
            "sentence_count": 5,
        }
        expected_response = {"id": 1} | test_request_payload
        # This should be a SummaryResponseSchema instance
        response = test_app.post("/summaries/", data=json.dumps(test_request_payload))

        assert response.status_code == 201
        assert response.json() == expected_response

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
            # An invalid summarizer
            (
                {"url": "https://yahoo.com/", "summarization_method": "invalid_summarizer"},
                # Client-side error: Unprocessable Entity
                422,
                {
                    "detail": [
                        {
                            "type": "enum",
                            "loc": ["body", "summarization_method"],
                            "msg": "Input should be 'lsa', 'lex_rank', 'text_rank' or 'edmundson'",
                            "input": "invalid_summarizer",
                            "ctx": {"expected": "'lsa', 'lex_rank', 'text_rank' or 'edmundson'"},
                        }
                    ]
                },
            ),
            # Sentence count out of range
            (
                {"url": "https://yahoo.com/", "sentence_count": 3},
                # Client-side error: Unprocessable Entity
                422,
                {
                    "detail": [
                        {
                            "type": "greater_than_equal",
                            "loc": ["body", "sentence_count"],
                            "msg": "Input should be greater than or equal to 5",
                            "input": 3,
                            "ctx": {"ge": 5},
                        }
                    ]
                },
            ),
            (
                {"url": "https://yahoo.com/", "sentence_count": 31},
                # Client-side error: Unprocessable Entity
                422,
                {
                    "detail": [
                        {
                            "type": "less_than_equal",
                            "loc": ["body", "sentence_count"],
                            "msg": "Input should be less than or equal to 30",
                            "input": 31,
                            "ctx": {"le": 30},
                        }
                    ]
                },
            ),
        ],
        scope="function",
    )
    def test_create_summary_invalid_request_unit(
        self, test_app, payload, expected_status_code, expected_response
    ) -> None:
        """
        Test for create_summary with invalid request payloads.
        """
        response = test_app.post("/summaries/", data=json.dumps(payload))
        assert response.status_code == expected_status_code
        assert response.json() == expected_response

    def test_read_summary_unit(self, test_app, monkeypatch) -> None:
        """
        Test for read_summary on the happy path.
        """
        ios_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        # Test TextSummarySchema
        test_summary_schema = {
            "id": 1,
            "url": "https://google.com/",
            "summary": "test summary",
            "summarization_method": "lsa",
            "sentence_count": 7,
            "created_at": ios_time,
        }

        # Monkeypatch the crud function
        async def mock_get(id: int) -> Dict:
            return test_summary_schema

        monkeypatch.setattr(crud, "get", mock_get)

        # Response for a get operation
        response = test_app.get(f"/summaries/{test_summary_schema['id']}")
        assert response.status_code == 200
        assert response.json() == test_summary_schema

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
    def test_read_summary_invalid_id_unit(
        self,
        test_app,
        monkeypatch,
        id,
        expected_status_code,
        expected_response,
    ) -> None:
        """
        Test for read_summary when an invalid (non-existent) id is passed.
        """

        # Monkeypatch the crud function, which returns None given invalid ID's
        async def mock_get(id: int) -> None:
            return None

        monkeypatch.setattr(crud, "get", mock_get)
        response = test_app.get(f"/summaries/{id}/")
        assert response.status_code == expected_status_code
        assert response.json() == expected_response

    def test_read_all_summaries_unit(self, test_app, monkeypatch) -> None:
        """
        Test for read_all_summaries on the happy path.
        """
        # Monkey patch the get_all crud operation
        timestamps = [
            (datetime.now(timezone.utc) + timedelta(hours=i)).isoformat().replace("+00:00", "Z")
            for i in range(3)
        ]
        test_summaries = [
            {
                "id": 1,
                "url": "https://google.com/",
                "summary": "google",
                "summarization_method": "lsa",
                "sentence_count": 7,
                "created_at": timestamps[0],
            },
            {
                "id": 2,
                "url": "https://yahoo.com/",
                "summary": "yahoo",
                "summarization_method": "edmundson",
                "sentence_count": 12,
                "created_at": timestamps[1],
            },
            {
                "id": 3,
                "url": "https://tesla.com/",
                "summary": "tesla",
                "summarization_method": "text_rank",
                "sentence_count": 29,
                "created_at": timestamps[2],
            },
        ]

        async def mock_get_all() -> List[Dict]:
            return test_summaries

        monkeypatch.setattr(crud, "get_all", mock_get_all)

        response = test_app.get("/summaries/")
        assert response.status_code == 200
        assert response.json() == test_summaries

    def test_remove_summary_unit(self, test_app, monkeypatch) -> None:
        """
        Test for remove_summary on the happy path.
        """
        test_record = {
            "id": 7,
            "url": "https://www.python.org/",
            "summary": "python programming",
            "summarization_method": "lex_rank",
            "sentence_count": 10,
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }

        # Mock the get path operation to simulate an existing record that matches the id of the record to be deleted
        async def mock_get(id: int) -> Dict:
            return test_record

        monkeypatch.setattr(crud, "get", mock_get)

        # Then, mock the delete crud operation
        async def mock_delete(id: int) -> Union[None, Dict]:
            return None

        monkeypatch.setattr(crud, "delete", mock_delete)

        # The response should be a TextSummarySchema instance matching the results from `mock_get`
        response = test_app.delete(f"/summaries/{test_record['id']}/")
        assert response.status_code == 200
        assert response.json() == test_record

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
    def test_remove_summary_invalid_id_unit(
        self, test_app, monkeypatch, id, expected_status_code, expected_response
    ) -> None:
        """
        Test for remove_summary when an invalid (non-existent) id is passed.
        """

        async def mock_get(id) -> Union[None, Dict]:
            return None

        monkeypatch.setattr(crud, "get", mock_get)
        response = test_app.delete(f"/summaries/{id}/")
        assert response.status_code == expected_status_code
        assert response.json() == expected_response

    def test_update_summary_unit(self, test_app, monkeypatch) -> None:
        """
        Test for update_summary on the happy path.
        """
        # Test SummaryUpdatePayloadSchema
        test_update_payload = {"url": "https://yahoo.com/", "update_summary": "Updated summary"}
        test_summary_id = 12
        test_updated_response = {
            "id": test_summary_id,
            "url": test_update_payload["url"],  # New url from updated payload request body
            "summary": test_update_payload[
                "update_summary"
            ],  # New summary from update payload request body,
            "summarization_method": "lsa",
            "sentence_count": 12,
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }

        # Simulate the returned dict of the put crud operation
        async def mock_put(
            id: int, payload: pydantic.SummaryUpdatePayloadSchema
        ) -> Union[Dict, None]:
            return test_updated_response

        monkeypatch.setattr(crud, "put", mock_put)

        response = test_app.put(
            f"/summaries/{test_summary_id}/",
            data=json.dumps(test_update_payload),
        )
        # The response of the update operation should be an instance of TextSummarySchema
        assert response.status_code == 200
        assert response.json() == test_updated_response

    @pytest.mark.parametrize(
        "id, payload, expected_status_code, expected_response",
        [
            # Non-existent ID results in 404 not found status code
            (
                maxsize,
                {"url": "https://google.com/", "update_summary": "Updated summary"},
                404,
                {
                    "detail": SummaryNotFoundException.detail,
                },
            ),
            # Invalid ID (i.e. < 1) results in 422 cannot be processed by server status code
            (
                0,
                {"url": "https://google.com/", "update_summary": "Updated summary"},
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
                            "loc": ["body", "update_summary"],
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
                            "loc": ["body", "update_summary"],
                            "msg": "Field required",
                            "input": {"url": "https://google.com/"},
                        }
                    ]
                },
            ),
        ],
        scope="function",
    )
    def test_update_summary_invalid_id_or_request_unit(
        self, test_app, monkeypatch, id, payload, expected_status_code, expected_response
    ) -> None:
        """
        Test for update_summary given invalid id or request body with missing fields.
        """

        # Monkeypatch the put crud operation, which returns None when missing or invalid request is passed
        async def mock_put(
            id: int, payload: pydantic.SummaryUpdatePayloadSchema
        ) -> Union[Dict, None]:
            return None

        monkeypatch.setattr(crud, "put", mock_put)

        response = test_app.put(f"/summaries/{id}/", data=json.dumps(payload))
        assert response.status_code == expected_status_code
        assert response.json() == expected_response

    def test_update_summary_invalid_url_unit(self, test_app) -> None:
        """
        Test for update_summary given invalid url in the request body with valid ID and updated summary.
        """
        response = test_app.put(
            "/summaries/1/",
            data=json.dumps({"url": "invalid://url", "update_summary": "Updated summary"}),
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
