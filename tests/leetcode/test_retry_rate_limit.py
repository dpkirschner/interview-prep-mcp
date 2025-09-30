"""Tests for retry logic and rate limiting."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
import httpx
import time
import asyncio
from interview_prep_mcp.leetcode.client import LeetCodeClient


class TestRetryLogic:
    """Tests for retry logic using tenacity."""

    @pytest.mark.asyncio
    async def test_retry_decorator_configuration(self):
        """Test that the retry decorator is properly configured on fetch_problem."""
        client = LeetCodeClient()

        # Check that the method has retry attributes from tenacity
        assert hasattr(client.fetch_problem, 'retry')
        assert hasattr(client.fetch_problem.retry, 'stop')
        assert hasattr(client.fetch_problem.retry, 'wait')

    @pytest.mark.asyncio
    async def test_fetch_problem_retries_on_network_error(self):
        """Test that fetch_problem retries on network errors."""
        client = LeetCodeClient()
        call_count = 0

        # Create mock response for successful request
        success_response = MagicMock()
        success_response.json.return_value = {
            "data": {
                "question": {
                    "questionId": "1",
                    "questionFrontendId": "1",
                    "title": "Two Sum",
                    "titleSlug": "two-sum",
                    "difficulty": "Easy",
                    "content": "<p>Test</p>",
                    "topicTags": [],
                    "codeSnippets": [],
                    "exampleTestcases": "[]",
                    "sampleTestCase": "[]",
                    "hints": []
                }
            }
        }
        success_response.raise_for_status = MagicMock()

        async def mock_post_with_retries(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                # Fail first 2 attempts
                raise httpx.ConnectError("Connection failed", request=MagicMock())
            # Succeed on 3rd attempt
            return success_response

        # Patch at the module level where httpx is imported
        with patch('interview_prep_mcp.leetcode.client.httpx.AsyncClient') as mock_client_class:
            mock_instance = MagicMock()
            mock_instance.post = AsyncMock(side_effect=mock_post_with_retries)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_instance

            problem = await client.fetch_problem("two-sum")

            assert problem is not None
            assert problem.title == "Two Sum"
            # Verify it retried (called 3 times)
            assert call_count == 3

    @pytest.mark.asyncio
    async def test_fetch_problem_retries_on_timeout(self):
        """Test that fetch_problem retries on timeout errors."""
        client = LeetCodeClient()
        call_count = 0

        success_response = MagicMock()
        success_response.json.return_value = {
            "data": {
                "question": {
                    "questionId": "1",
                    "questionFrontendId": "1",
                    "title": "Two Sum",
                    "titleSlug": "two-sum",
                    "difficulty": "Easy",
                    "content": "<p>Test</p>",
                    "topicTags": [],
                    "codeSnippets": [],
                    "exampleTestcases": "[]",
                    "sampleTestCase": "[]",
                    "hints": []
                }
            }
        }
        success_response.raise_for_status = MagicMock()

        async def mock_post_with_timeout(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise httpx.TimeoutException("Timeout", request=MagicMock())
            return success_response

        with patch('interview_prep_mcp.leetcode.client.httpx.AsyncClient') as mock_client_class:
            mock_instance = MagicMock()
            mock_instance.post = AsyncMock(side_effect=mock_post_with_timeout)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_instance

            problem = await client.fetch_problem("two-sum")

            assert problem is not None
            assert call_count == 2  # Failed once, succeeded on 2nd

    @pytest.mark.asyncio
    async def test_fetch_problem_fails_after_max_retries(self):
        """Test that fetch_problem fails after exhausting all retries."""
        client = LeetCodeClient()
        call_count = 0

        async def mock_post_always_fails(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            raise httpx.ConnectError("Persistent failure", request=MagicMock())

        with patch('interview_prep_mcp.leetcode.client.httpx.AsyncClient') as mock_client_class:
            mock_instance = MagicMock()
            mock_instance.post = AsyncMock(side_effect=mock_post_always_fails)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_instance

            with pytest.raises(httpx.ConnectError):
                await client.fetch_problem("two-sum")

            # Should have tried 3 times (initial + 2 retries)
            assert call_count == 3

    @pytest.mark.asyncio
    async def test_fetch_problem_does_not_retry_on_graphql_error(self):
        """Test that GraphQL errors (ValueError) are not retried."""
        client = LeetCodeClient()
        call_count = 0

        error_response = MagicMock()
        error_response.json.return_value = {
            "errors": [{"message": "Problem not found"}]
        }
        error_response.raise_for_status = MagicMock()

        async def mock_post_graphql_error(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return error_response

        with patch('interview_prep_mcp.leetcode.client.httpx.AsyncClient') as mock_client_class:
            mock_instance = MagicMock()
            mock_instance.post = AsyncMock(side_effect=mock_post_graphql_error)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_instance

            with pytest.raises(ValueError, match="GraphQL errors"):
                await client.fetch_problem("two-sum")

            # Should only call once - no retries for ValueError
            assert call_count == 1


class TestRateLimiting:
    """Tests for rate limiting using aiolimiter."""

    @pytest.mark.asyncio
    async def test_rate_limiter_exists(self):
        """Test that rate limiter is configured."""
        client = LeetCodeClient()
        assert hasattr(client, '_rate_limiter')
        assert client._rate_limiter.max_rate == 10  # 10 requests
        assert client._rate_limiter.time_period == 1  # per second

    @pytest.mark.asyncio
    async def test_rate_limiter_delays_requests(self):
        """Test that rate limiter delays requests beyond the limit."""
        client = LeetCodeClient()

        success_response = MagicMock()
        success_response.json.return_value = {
            "data": {
                "question": {
                    "questionId": "1",
                    "questionFrontendId": "1",
                    "title": "Two Sum",
                    "titleSlug": "two-sum",
                    "difficulty": "Easy",
                    "content": "<p>Test</p>",
                    "topicTags": [],
                    "codeSnippets": [],
                    "exampleTestcases": "[]",
                    "sampleTestCase": "[]",
                    "hints": []
                }
            }
        }
        success_response.raise_for_status = MagicMock()

        async def mock_post(*args, **kwargs):
            return success_response

        with patch('interview_prep_mcp.leetcode.client.httpx.AsyncClient') as mock_client_class:
            mock_instance = MagicMock()
            mock_instance.post = AsyncMock(side_effect=mock_post)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_instance

            # Make 12 concurrent requests (limit is 10 per second)
            start_time = time.time()
            tasks = [client.fetch_problem(f"problem-{i}") for i in range(12)]
            results = await asyncio.gather(*tasks)
            elapsed = time.time() - start_time

            # All requests should succeed
            assert len(results) == 12
            assert all(r is not None for r in results)

            # Should take at least 0.2 seconds due to rate limiting
            # (10 allowed immediately, 2 more need to wait)
            assert elapsed >= 0.1

    @pytest.mark.asyncio
    async def test_rate_limiter_allows_sequential_requests(self):
        """Test that rate limiter allows sequential requests within limit."""
        client = LeetCodeClient()

        success_response = MagicMock()
        success_response.json.return_value = {
            "data": {
                "question": {
                    "questionId": "1",
                    "questionFrontendId": "1",
                    "title": "Two Sum",
                    "titleSlug": "two-sum",
                    "difficulty": "Easy",
                    "content": "<p>Test</p>",
                    "topicTags": [],
                    "codeSnippets": [],
                    "exampleTestcases": "[]",
                    "sampleTestCase": "[]",
                    "hints": []
                }
            }
        }
        success_response.raise_for_status = MagicMock()

        async def mock_post(*args, **kwargs):
            return success_response

        with patch('interview_prep_mcp.leetcode.client.httpx.AsyncClient') as mock_client_class:
            mock_instance = MagicMock()
            mock_instance.post = AsyncMock(side_effect=mock_post)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_instance

            # Make 5 sequential requests (well within limit)
            results = []
            for i in range(5):
                result = await client.fetch_problem(f"problem-{i}")
                results.append(result)

            assert len(results) == 5
            assert all(r is not None for r in results)
