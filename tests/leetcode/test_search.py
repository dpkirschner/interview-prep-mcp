"""Tests for problem search functionality."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from interview_prep_mcp.leetcode.types import ProblemSummary, CachedProblemInfo


class TestSearchProblems:
    """Tests for search_problems method."""

    @pytest.mark.asyncio
    async def test_search_problems_single_match(self, client):
        """Test searching for problems with a single match."""
        # Mock the cache
        client._problem_cache = [
            CachedProblemInfo(
                questionFrontendId="1",
                title="Two Sum",
                titleSlug="two-sum",
                difficulty="Easy"
            ),
            CachedProblemInfo(
                questionFrontendId="15",
                title="3Sum",
                titleSlug="3sum",
                difficulty="Medium"
            )
        ]

        results = await client.search_problems("two sum")

        assert len(results) == 1
        assert results[0].title == "Two Sum"
        assert results[0].questionFrontendId == "1"
        assert results[0].titleSlug == "two-sum"

    @pytest.mark.asyncio
    async def test_search_problems_multiple_matches(self, client):
        """Test searching for problems with multiple matches."""
        client._problem_cache = [
            CachedProblemInfo(
                questionFrontendId="1",
                title="Two Sum",
                titleSlug="two-sum",
                difficulty="Easy"
            ),
            CachedProblemInfo(
                questionFrontendId="15",
                title="3Sum",
                titleSlug="3sum",
                difficulty="Medium"
            ),
            CachedProblemInfo(
                questionFrontendId="16",
                title="3Sum Closest",
                titleSlug="3sum-closest",
                difficulty="Medium"
            ),
            CachedProblemInfo(
                questionFrontendId="18",
                title="4Sum",
                titleSlug="4sum",
                difficulty="Medium"
            )
        ]

        results = await client.search_problems("sum", limit=3)

        assert len(results) == 3
        assert all("sum" in r.title.lower() or "sum" in r.titleSlug.lower() for r in results)

    @pytest.mark.asyncio
    async def test_search_problems_no_matches(self, client):
        """Test searching for problems with no matches."""
        client._problem_cache = [
            CachedProblemInfo(
                questionFrontendId="1",
                title="Two Sum",
                titleSlug="two-sum",
                difficulty="Easy"
            )
        ]

        results = await client.search_problems("binary tree")

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_problems_case_insensitive(self, client):
        """Test that search is case insensitive."""
        client._problem_cache = [
            CachedProblemInfo(
                questionFrontendId="1",
                title="Two Sum",
                titleSlug="two-sum",
                difficulty="Easy"
            )
        ]

        results = await client.search_problems("TWO SUM")

        assert len(results) == 1
        assert results[0].title == "Two Sum"

    @pytest.mark.asyncio
    async def test_search_problems_by_slug(self, client):
        """Test searching by slug."""
        client._problem_cache = [
            CachedProblemInfo(
                questionFrontendId="1",
                title="Two Sum",
                titleSlug="two-sum",
                difficulty="Easy"
            )
        ]

        results = await client.search_problems("two-sum")

        assert len(results) == 1
        assert results[0].titleSlug == "two-sum"

    @pytest.mark.asyncio
    async def test_search_problems_respects_limit(self, client):
        """Test that search respects the limit parameter."""
        client._problem_cache = [
            CachedProblemInfo(
                questionFrontendId=str(i),
                title=f"Problem {i}",
                titleSlug=f"problem-{i}",
                difficulty="Easy"
            )
            for i in range(20)
        ]

        results = await client.search_problems("problem", limit=5)

        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_search_problems_builds_cache_if_needed(self, client):
        """Test that search builds cache if not already built."""
        assert client._problem_cache is None

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "problemsetQuestionList": {
                    "total": 1,
                    "questions": [
                        {
                            "questionFrontendId": "1",
                            "title": "Two Sum",
                            "titleSlug": "two-sum",
                            "difficulty": "Easy"
                        }
                    ]
                }
            }
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            results = await client.search_problems("two sum")

            assert client._problem_cache is not None
            assert len(results) == 1
            assert results[0].title == "Two Sum"

    @pytest.mark.asyncio
    async def test_search_problems_partial_match(self, client):
        """Test searching with partial keywords."""
        client._problem_cache = [
            CachedProblemInfo(
                questionFrontendId="1",
                title="Two Sum",
                titleSlug="two-sum",
                difficulty="Easy"
            ),
            CachedProblemInfo(
                questionFrontendId="2",
                title="Add Two Numbers",
                titleSlug="add-two-numbers",
                difficulty="Medium"
            )
        ]

        results = await client.search_problems("two")

        assert len(results) == 2
        assert all("two" in r.title.lower() or "two" in r.titleSlug.lower() for r in results)