"""Tests for leetcode client."""
import pytest
from typing import Any
from unittest.mock import AsyncMock, patch, MagicMock
from interview_prep_mcp.leetcode.types import Problem
from .conftest import mock_async_client
import httpx


class TestLeetCodeClient:
    """Tests for LeetCodeClient."""

    def test_client_initialization(self, client) -> None:  # type: ignore[no-untyped-def]
        """Test client initializes with correct URL."""
        assert client.url == "https://leetcode.com/graphql/"

    @pytest.mark.asyncio
    async def test_fetch_problem_success(self, client, mock_response_data) -> None:  # type: ignore[no-untyped-def,misc]
        """Test successfully fetching a problem."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            problem = await client.fetch_problem("two-sum")

            assert problem is not None
            assert isinstance(problem, Problem)
            assert problem.title == "Two Sum"
            assert problem.questionFrontendId == "1"
            assert problem.difficulty == "Easy"
            assert len(problem.topicTags) == 2
            assert len(problem.codeSnippets) == 1

    @pytest.mark.asyncio
    async def test_fetch_problem_not_found(self, client) -> None:  # type: ignore[no-untyped-def,misc]
        """Test fetching a non-existent problem."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"question": None}}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            problem = await client.fetch_problem("non-existent-problem")

            assert problem is None

    @pytest.mark.asyncio
    async def test_fetch_problem_graphql_error(self, client, mock_httpx_response) -> None:  # type: ignore[no-untyped-def,misc]
        """Test handling GraphQL errors."""
        mock_httpx_response.json.return_value = {
            "errors": [
                {"message": "Problem not found"}
            ]
        }

        with mock_async_client(mock_httpx_response):
            with pytest.raises(ValueError, match="GraphQL errors"):
                await client.fetch_problem("two-sum")

    @pytest.mark.asyncio
    async def test_fetch_problem_http_error(self, client) -> None:  # type: ignore[no-untyped-def,misc]
        """Test handling HTTP errors."""
        with mock_async_client(side_effect=httpx.HTTPError("Connection failed")):
            with pytest.raises(httpx.HTTPError):
                await client.fetch_problem("two-sum")

    @pytest.mark.asyncio
    async def test_fetch_problem_request_format(self, client, mock_response_data) -> None:  # type: ignore[no-untyped-def,misc]
        """Test that the request is formatted correctly."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = AsyncMock()
            mock_post = AsyncMock(return_value=mock_response)
            mock_client.post = mock_post
            mock_client_class.return_value = mock_client

            await client.fetch_problem("two-sum")

            # Verify the request was made with correct parameters
            mock_post.assert_called_once()
            call_args = mock_post.call_args

            assert call_args[0][0] == "https://leetcode.com/graphql/"
            assert "json" in call_args[1]
            assert "query" in call_args[1]["json"]
            assert "variables" in call_args[1]["json"]
            assert call_args[1]["json"]["variables"]["titleSlug"] == "two-sum"
            assert "headers" in call_args[1]
            assert call_args[1]["headers"]["Content-Type"] == "application/json"
            assert call_args[1]["headers"]["Referer"] == "https://leetcode.com"

    @pytest.mark.asyncio
    async def test_fetch_problem_timeout(self, client) -> None:  # type: ignore[no-untyped-def,misc]
        """Test handling timeout errors."""
        with mock_async_client(side_effect=httpx.TimeoutException("Request timed out")):
            with pytest.raises(httpx.TimeoutException):
                await client.fetch_problem("two-sum")

    @pytest.mark.asyncio
    async def test_fetch_problem_network_error(self, client) -> None:  # type: ignore[no-untyped-def,misc]
        """Test handling network errors."""
        with mock_async_client(side_effect=httpx.ConnectError("Connection refused")):
            with pytest.raises(httpx.ConnectError):
                await client.fetch_problem("two-sum")

    @pytest.mark.asyncio
    async def test_fetch_problem_malformed_json(self, client, mock_httpx_response) -> None:  # type: ignore[no-untyped-def,misc]
        """Test handling malformed JSON response."""
        mock_httpx_response.json.side_effect = ValueError("Invalid JSON")

        with mock_async_client(mock_httpx_response):
            with pytest.raises(ValueError, match="Invalid JSON"):
                await client.fetch_problem("two-sum")

    @pytest.mark.asyncio
    async def test_fetch_problem_empty_response(self, client) -> None:  # type: ignore[no-untyped-def,misc]
        """Test handling empty response data."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            result = await client.fetch_problem("two-sum")
            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_problem_null_question(self, client) -> None:  # type: ignore[no-untyped-def,misc]
        """Test handling null question in response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"question": None}}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            result = await client.fetch_problem("non-existent")
            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_problem_partial_data(self, client) -> None:  # type: ignore[no-untyped-def,misc]
        """Test handling response with missing optional fields."""
        mock_response_data: dict[str, dict[str, dict[str, object]]] = {
            "data": {
                "question": {
                    "questionId": "100",
                    "questionFrontendId": "100",
                    "title": "Minimal Problem",
                    "titleSlug": "minimal-problem",
                    "difficulty": "Easy",
                    "content": "<p>Minimal</p>",
                    "topicTags": [],
                    "codeSnippets": [],
                    "exampleTestcases": None,
                    "sampleTestCase": None,
                    "hints": []
                }
            }
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            problem = await client.fetch_problem("minimal-problem")
            assert problem is not None
            assert problem.exampleTestcases is None
            assert problem.sampleTestCase is None
            assert problem.hints == []

    @pytest.mark.asyncio
    async def test_fetch_problem_with_special_characters_in_slug(self, client, mock_response_data) -> None:  # type: ignore[no-untyped-def,misc]
        """Test fetching problem with special characters in slug."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = AsyncMock()
            mock_post = AsyncMock(return_value=mock_response)
            mock_client.post = mock_post
            mock_client_class.return_value = mock_client

            await client.fetch_problem("binary-tree-level-order-traversal-ii")

            call_args = mock_post.call_args
            assert call_args[1]["json"]["variables"]["titleSlug"] == "binary-tree-level-order-traversal-ii"

    @pytest.mark.asyncio
    async def test_fetch_problem_multiple_graphql_errors(self, client, mock_httpx_response) -> None:  # type: ignore[no-untyped-def,misc]
        """Test handling multiple GraphQL errors."""
        mock_httpx_response.json.return_value = {
            "errors": [
                {"message": "Error 1"},
                {"message": "Error 2"},
                {"message": "Error 3"}
            ]
        }

        with mock_async_client(mock_httpx_response):
            with pytest.raises(ValueError, match="GraphQL errors: Error 1, Error 2, Error 3"):
                await client.fetch_problem("two-sum")

    @pytest.mark.asyncio
    async def test_fetch_problem_http_status_error(self, client, mock_httpx_response) -> None:  # type: ignore[no-untyped-def,misc]
        """Test handling HTTP status errors (4xx, 5xx)."""
        mock_httpx_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Server Error", request=MagicMock(), response=MagicMock()
        )

        with mock_async_client(mock_httpx_response):
            with pytest.raises(httpx.HTTPStatusError):
                await client.fetch_problem("two-sum")

    @pytest.mark.asyncio
    async def test_fetch_problem_pydantic_validation_error(self, client, mock_httpx_response) -> None:  # type: ignore[no-untyped-def,misc]
        """Test handling Pydantic validation errors from malformed data."""
        mock_httpx_response.json.return_value = {
            "data": {
                "question": {
                    "questionId": "1",
                    # Missing required fields for Problem model
                    "title": "Incomplete"
                }
            }
        }

        with mock_async_client(mock_httpx_response):
            with pytest.raises(Exception):  # Pydantic ValidationError
                await client.fetch_problem("two-sum")

    @pytest.mark.asyncio
    async def test_fetch_problem_empty_title_slug(self, client, mock_response_data) -> None:  # type: ignore[no-untyped-def,misc]
        """Test fetching with empty title slug."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = AsyncMock()
            mock_post = AsyncMock(return_value=mock_response)
            mock_client.post = mock_post
            mock_client_class.return_value = mock_client

            await client.fetch_problem("")

            call_args = mock_post.call_args
            assert call_args[1]["json"]["variables"]["titleSlug"] == ""

    @pytest.mark.asyncio
    async def test_fetch_problem_ensures_timeout_set(self, client, mock_response_data) -> None:  # type: ignore[no-untyped-def,misc]
        """Test that timeout is properly configured."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = AsyncMock()
            mock_post = AsyncMock(return_value=mock_response)
            mock_client.post = mock_post
            mock_client_class.return_value = mock_client

            await client.fetch_problem("two-sum")

            call_args = mock_post.call_args
            assert "timeout" in call_args[1]
            assert call_args[1]["timeout"] == 30.0