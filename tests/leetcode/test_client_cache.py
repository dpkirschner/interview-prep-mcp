"""Tests for LeetCode client caching."""
import pytest
import time
from interview_prep_mcp.leetcode.client import LeetCodeClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cache_performance():
    """Test that cache improves performance on subsequent lookups."""
    client = LeetCodeClient()

    # First lookup - should build cache (slow)
    start = time.time()
    problem1 = await client.fetch_problem_by_id(1)
    first_duration = time.time() - start

    assert problem1 is not None
    assert problem1.title == "Two Sum"
    print(f"\nFirst lookup (with cache build): {first_duration:.2f}s")

    # Second lookup - should use cache (fast)
    start = time.time()
    problem2 = await client.fetch_problem_by_id(42)
    second_duration = time.time() - start

    assert problem2 is not None
    print(f"Second lookup (cached): {second_duration:.2f}s")

    # Cache should make second lookup much faster
    assert second_duration < first_duration / 2, "Cache should significantly improve performance"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cache_content():
    """Test that cache is built correctly."""
    client = LeetCodeClient()

    # Build cache
    cache = await client._build_id_to_slug_cache()

    assert cache is not None
    assert len(cache) > 3000, "Should have thousands of problems"
    assert cache.get("1") == "two-sum"
    assert cache.get("42") == "trapping-rain-water"