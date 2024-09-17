import json
from sys import maxsize

import pytest

from app.api import summaries
from app.api.custom_exceptions import SummaryNotFoundException


class TestSummary(object):
    """
    Tests for GET /summaries, GET /summaries/:id, POST /summaries, PUT /summaries/:id, and DELETE /summaries/:id.
    """

    @pytest.mark.parametrize(
        "payload, expected_response_sans_id",
        [
            # Non-default summarizer and sentence count
            (
                {
                    "url": "https://yahoo.com/",
                    "summarizer_specifier": "lex_rank",
                    "sentence_count": 5,
                },
                {
                    "url": "https://yahoo.com/",
                    "summarizer_specifier": "lex_rank",
                    "sentence_count": 5,
                },
            ),
            # Default values
            (
                {"url": "https://yahoo.com/"},
                {"url": "https://yahoo.com/", "summarizer_specifier": "lsa", "sentence_count": 10},
            ),
        ],
        scope="function",
    )
    def test_create_summary(
        self, test_app_with_db, monkeypatch, payload, expected_response_sans_id
    ) -> None:
        """
        Test for create_summary on the happy path.
        """

        # Monkeypatch the generate summary function
        def mock_generate_summary(summary_id, url, summarizer_specifier, sentence_count) -> None:
            return None

        monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)

        response = test_app_with_db.post("/summaries/", data=json.dumps(payload))
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["url"] == expected_response_sans_id["url"]
        assert (
            response_data["summarizer_specifier"]
            == expected_response_sans_id["summarizer_specifier"]
        )
        assert response_data["sentence_count"] == expected_response_sans_id["sentence_count"]

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
                {"url": "https://yahoo.com/", "summarizer_specifier": "invalid_summarizer"},
                # Client-side error: Unprocessable Entity
                422,
                {
                    "detail": [
                        {
                            "type": "enum",
                            "loc": ["body", "summarizer_specifier"],
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
    def test_create_summary_invalid_request(
        self, test_app_with_db, payload, expected_status_code, expected_response
    ) -> None:
        """
        Test for create_summary with invalid request payloads.
        """
        response = test_app_with_db.post("/summaries/", data=json.dumps(payload))
        assert response.status_code == expected_status_code
        assert response.json() == expected_response

    def test_read_summary(self, test_app_with_db, monkeypatch) -> None:
        """
        Test for read_summary on the happy path.
        """

        # Monkeypatch the generate summary function
        def mock_generate_summary(summary_id, url, summarizer_specifier, sentence_count) -> None:
            return None

        monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)

        payload = {
            "url": "https://google.com/",
            "summarizer_specifier": "lex_rank",
            "sentence_count": 5,
        }
        # Create summary and get the generated ID
        response = test_app_with_db.post("/summaries/", data=json.dumps(payload))
        summary_id = response.json()["id"]

        # Response for a get operation
        response = test_app_with_db.get(f"/summaries/{summary_id}")
        assert response.status_code == 200

        response_data = response.json()
        # The id field should match that from the SummaryResponseSchema
        assert response_data["id"] == summary_id
        # The url field should match
        assert response_data["url"] == payload["url"]
        # The created_at fields should exist (and summary is an empty string initially)
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

    def test_read_all_summaries(self, test_app_with_db, monkeypatch) -> None:
        """
        Test for read_all_summaries on the happy path.
        """

        # Monkeypatch the generate summary function
        def mock_generate_summary(summary_id, url, summarizer_specifier, sentence_count) -> None:
            return None

        monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)

        payload = {
            "url": "https://fastapi.tiangolo.com/",
            "summarizer_specifier": "lsa",
            "sentence_count": 17,
        }
        # Create summary and get the generated ID
        response = test_app_with_db.post("/summaries/", data=json.dumps(payload))
        summary_id = response.json()["id"]

        # Get all summaries
        response = test_app_with_db.get("/summaries/")
        assert response.status_code == 200

        # Response is a list of SummarySchema's
        response_list = response.json()
        # Ensure that the newly created text summary is among the list of text summaries
        assert (len(list(filter(lambda summary_schema: summary_schema["id"] == summary_id, response_list))) == 1)  # fmt: skip

    def test_remove_summary(self, test_app_with_db, monkeypatch) -> None:
        """
        Test for remove_summary on the happy path.
        """

        # Monkeypatch the generate summary function
        def mock_generate_summary(summary_id, url, summarizer_specifier, sentence_count) -> None:
            return None

        monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)

        payload = {
            "url": "https://www.python.org/",
            "summarizer_specifier": "edmundson",
            "sentence_count": 7,
        }
        # Create summary and get the generated ID
        response_post = test_app_with_db.post("/summaries/", data=json.dumps(payload))
        summary_id = response_post.json()["id"]

        # The response should be a SummarySchema instance
        response_delete = test_app_with_db.delete(f"/summaries/{summary_id}/")
        response_delete_data = response_delete.json()
        assert response_delete.status_code == 200
        assert response_delete_data["url"] == payload["url"]
        # The created_at must exist
        assert response_delete_data["created_at"]

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

    def test_update_summary(self, test_app_with_db, monkeypatch) -> None:
        """
        Test for update_summary on the happy path.
        """

        # Monkeypatch the generate summary function
        def mock_generate_summary(summary_id, url, summarizer_specifier, sentence_count) -> None:
            return None

        monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)

        # Create summary and get the generated ID
        payload = {
            "url": "https://isocpp.org/",
            "summarizer_specifier": "text_rank",
            "sentence_count": 6,
        }
        response = test_app_with_db.post("/summaries/", data=json.dumps(payload))
        summary_id = response.json()["id"]

        # Update the summary for the summary generated above
        response = test_app_with_db.put(
            f"/summaries/{summary_id}/",
            data=json.dumps({"url": payload["url"], "update_summary": "Updated summary"}),
        )
        assert response.status_code == 200

        response_data = response.json()
        # Ensure that the id and url match those from the post path operation
        assert response_data["id"] == summary_id
        assert response_data["url"] == payload["url"]
        # The summary and created_at fields should exist, and summary should have been updateds
        assert response_data["summary"] == "Updated summary"
        assert response_data["created_at"]

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
    def test_update_summary_invalid_id_or_request(
        self, test_app_with_db, id, payload, expected_status_code, expected_response
    ) -> None:
        """
        Test for update_summary given invalid id or request body with missing fields.
        """
        response = test_app_with_db.put(f"/summaries/{id}/", data=json.dumps(payload))
        assert response.status_code == expected_status_code
        assert response.json() == expected_response

    def test_update_summary_invalid_url(self, test_app_with_db) -> None:
        """
        Test for update_summary given invalid url in the request body with valid ID and updated summary.
        """
        response = test_app_with_db.put(
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
