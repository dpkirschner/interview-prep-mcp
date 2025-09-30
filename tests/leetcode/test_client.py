"""Tests for leetcode client."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from interview_prep_mcp.leetcode.client import LeetCodeClient
from interview_prep_mcp.leetcode.types import Problem
import httpx


@pytest.fixture
def mock_response_data():
    """Sample response data from LeetCode API."""
    return {
        "data": {
            "question": {
                "questionId": "1",
                "questionFrontendId": "1",
                "title": "Two Sum",
                "titleSlug": "two-sum",
                "difficulty": "Easy",
                "content": "<p>Given an array of integers...</p>",
                "topicTags": [
                    {"name": "Array", "slug": "array"},
                    {"name": "Hash Table", "slug": "hash-table"}
                ],
                "codeSnippets": [
                    {
                        "lang": "Python3",
                        "langSlug": "python3",
                        "code": "class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:"
                    }
                ],
                "exampleTestcases": "[2,7,11,15]\n9",
                "sampleTestCase": "[2,7,11,15]\n9",
                "hints": []
            }
        }
    }


@pytest.fixture
def client():
    """Create a LeetCodeClient instance."""
    return LeetCodeClient()


class TestLeetCodeClient:
    """Tests for LeetCodeClient."""

    def test_client_initialization(self, client):
        """Test client initializes with correct URL."""
        assert client.url == "https://leetcode.com/graphql/"

    @pytest.mark.asyncio
    async def test_fetch_problem_success(self, client, mock_response_data):
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
    async def test_fetch_problem_not_found(self, client):
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
    async def test_fetch_problem_graphql_error(self, client):
        """Test handling GraphQL errors."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "errors": [
                {"message": "Problem not found"}
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_async_client = AsyncMock()
            mock_async_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_async_client

            with pytest.raises(ValueError, match="GraphQL errors"):
                await client.fetch_problem("two-sum")

    @pytest.mark.asyncio
    async def test_fetch_problem_http_error(self, client):
        """Test handling HTTP errors."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_async_client = AsyncMock()
            mock_async_client.post = AsyncMock(side_effect=httpx.HTTPError("Connection failed"))
            mock_client_class.return_value.__aenter__.return_value = mock_async_client

            with pytest.raises(httpx.HTTPError):
                await client.fetch_problem("two-sum")

    @pytest.mark.asyncio
    async def test_fetch_problem_request_format(self, client, mock_response_data):
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
    async def test_fetch_problem_timeout(self, client):
        """Test handling timeout errors."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_async_client = AsyncMock()
            mock_async_client.post = AsyncMock(side_effect=httpx.TimeoutException("Request timed out"))
            mock_client_class.return_value.__aenter__.return_value = mock_async_client

            with pytest.raises(httpx.TimeoutException):
                await client.fetch_problem("two-sum")

    @pytest.mark.asyncio
    async def test_fetch_problem_network_error(self, client):
        """Test handling network errors."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_async_client = AsyncMock()
            mock_async_client.post = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
            mock_client_class.return_value.__aenter__.return_value = mock_async_client

            with pytest.raises(httpx.ConnectError):
                await client.fetch_problem("two-sum")

    @pytest.mark.asyncio
    async def test_fetch_problem_malformed_json(self, client):
        """Test handling malformed JSON response."""
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_async_client = AsyncMock()
            mock_async_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_async_client

            with pytest.raises(ValueError, match="Invalid JSON"):
                await client.fetch_problem("two-sum")

    @pytest.mark.asyncio
    async def test_fetch_problem_empty_response(self, client):
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
    async def test_fetch_problem_null_question(self, client):
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
    async def test_fetch_problem_partial_data(self, client):
        """Test handling response with missing optional fields."""
        mock_response_data = {
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
    async def test_fetch_problem_with_special_characters_in_slug(self, client, mock_response_data):
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
    async def test_fetch_problem_multiple_graphql_errors(self, client):
        """Test handling multiple GraphQL errors."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "errors": [
                {"message": "Error 1"},
                {"message": "Error 2"},
                {"message": "Error 3"}
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_async_client = AsyncMock()
            mock_async_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_async_client

            with pytest.raises(ValueError, match="GraphQL errors: Error 1, Error 2, Error 3"):
                await client.fetch_problem("two-sum")

    @pytest.mark.asyncio
    async def test_fetch_problem_http_status_error(self, client):
        """Test handling HTTP status errors (4xx, 5xx)."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_async_client = AsyncMock()

            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "500 Server Error", request=MagicMock(), response=MagicMock()
            )
            mock_async_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_async_client

            with pytest.raises(httpx.HTTPStatusError):
                await client.fetch_problem("two-sum")

    @pytest.mark.asyncio
    async def test_fetch_problem_pydantic_validation_error(self, client):
        """Test handling Pydantic validation errors from malformed data."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "question": {
                    "questionId": "1",
                    # Missing required fields for Problem model
                    "title": "Incomplete"
                }
            }
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_async_client = AsyncMock()
            mock_async_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_async_client

            with pytest.raises(Exception):  # Pydantic ValidationError
                await client.fetch_problem("two-sum")

    @pytest.mark.asyncio
    async def test_fetch_problem_empty_title_slug(self, client, mock_response_data):
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
    async def test_fetch_problem_ensures_timeout_set(self, client, mock_response_data):
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