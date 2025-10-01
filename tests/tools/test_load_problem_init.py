"""Tests for load_problem tool initialization."""
import pytest
import time
from interview_prep_mcp.tools.load_problem import LoadProblemTool


@pytest.mark.integration
@pytest.mark.asyncio
async def test_initialize_preloads_cache() -> None:
    """Test that initialize() preloads the cache."""
    tool = LoadProblemTool()

    # Initialize should build the cache
    start = time.time()
    await tool.initialize()
    init_duration = time.time() - start

    print(f"\nInitialization time: {init_duration:.2f}s")
    assert init_duration > 5, "Initialization should take time to build cache"

    # Verify cache is populated
    assert tool.client._id_to_slug_cache is not None
    assert len(tool.client._id_to_slug_cache) > 3000

    # Now a lookup should be fast
    start = time.time()
    result = await tool.execute(problem_id=42)
    lookup_duration = time.time() - start

    print(f"Lookup time after init: {lookup_duration:.2f}s")
    assert isinstance(result, dict)
    assert result["problem_id"] == "42"
    assert lookup_duration < 1.0, "Lookup should be fast after initialization"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_without_initialize_still_works() -> None:
    """Test that the tool still works without calling initialize (lazy loading)."""
    tool = LoadProblemTool()

    # Don't call initialize - should still work but build cache on first use
    start = time.time()
    result = await tool.execute(problem_id=1)
    first_duration = time.time() - start

    print(f"\nFirst lookup without init: {first_duration:.2f}s")
    assert isinstance(result, dict)
    assert result["problem_id"] == "1"
    assert first_duration > 5, "First lookup should build cache"

    # Second lookup should be fast
    start = time.time()
    result2 = await tool.execute(problem_id=2)
    second_duration = time.time() - start

    print(f"Second lookup: {second_duration:.2f}s")
    assert isinstance(result2, dict)
    assert result2["problem_id"] == "2"
    assert second_duration < 1.0, "Second lookup should be fast"