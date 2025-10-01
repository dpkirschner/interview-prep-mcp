"""Shared fixtures for LeetCode tests."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from contextlib import contextmanager
from interview_prep_mcp.leetcode.client import LeetCodeClient


@pytest.fixture
def client():  # type: ignore[no-untyped-def]
    """Create a LeetCodeClient instance."""
    return LeetCodeClient()


@pytest.fixture
def mock_response_data():  # type: ignore[no-untyped-def]
    """Sample response data from LeetCode API for Two Sum problem."""
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
def mock_httpx_response():  # type: ignore[no-untyped-def]
    """Create a mock httpx response with common setup."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    return mock_response


@contextmanager
def mock_async_client(mock_response=None, side_effect=None):  # type: ignore[no-untyped-def,misc]
    """
    Context manager to mock httpx.AsyncClient for testing.

    Args:
        mock_response: The response object to return from post()
        side_effect: Exception or callable to use as side_effect for post()

    Usage:
        with mock_async_client(mock_response):
            result = await client.fetch_problem("two-sum")
    """
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_async_client = AsyncMock()

        if side_effect:
            mock_async_client.post = AsyncMock(side_effect=side_effect)
        elif mock_response:
            mock_async_client.post = AsyncMock(return_value=mock_response)
        else:
            # Default to returning a mock
            mock_async_client.post = AsyncMock()

        mock_client_class.return_value.__aenter__.return_value = mock_async_client

        yield mock_async_client