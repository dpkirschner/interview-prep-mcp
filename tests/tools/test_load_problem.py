"""Tests for load_problem tool."""
import pytest
from unittest.mock import AsyncMock, patch
from interview_prep_mcp.tools.load_problem import LoadProblemTool
from interview_prep_mcp.leetcode.types import Problem, CodeSnippet, TopicTag


@pytest.fixture
def sample_problem():  # type: ignore[no-untyped-def]
    """Create a sample problem for testing."""
    return Problem(
        questionId="1",
        questionFrontendId="1",
        title="Two Sum",
        titleSlug="two-sum",
        difficulty="Easy",
        content="<p>Given an array of integers <code>nums</code> and an integer <code>target</code>, return <em>indices of the two numbers such that they add up to <code>target</code></em>.</p>",
        topicTags=[
            TopicTag(name="Array", slug="array"),
            TopicTag(name="Hash Table", slug="hash-table"),
        ],
        codeSnippets=[
            CodeSnippet(
                lang="Python3",
                langSlug="python3",
                code="class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        pass",
            ),
        ],
        exampleTestcases="[2,7,11,15]\n9",
        sampleTestCase="[2,7,11,15]\n9",
        hints=["A hint for solving the problem"],
    )


@pytest.mark.asyncio
async def test_load_problem_success(sample_problem) -> None:  # type: ignore[no-untyped-def,misc]
    """Test successfully loading a problem."""
    tool = LoadProblemTool()

    with patch.object(tool.client, "fetch_problem", new=AsyncMock(return_value=sample_problem)):
        result = await tool.execute("two-sum")

    assert isinstance(result, dict)
    assert result["problem_id"] == "1"
    assert result["title"] == "Two Sum"
    assert result["title_slug"] == "two-sum"
    assert result["difficulty"] == "Easy"
    assert "Given an array of integers" in result["description"]
    assert result["topics"] == ["Array", "Hash Table"]
    # Without language specified, should return all code snippets
    assert "code_snippets" in result
    assert "python3" in result["code_snippets"]
    assert "class Solution:" in result["code_snippets"]["python3"]
    assert result["hints"] == ["A hint for solving the problem"]
    assert result["example_test_cases"] == "[2,7,11,15]\n9"


@pytest.mark.asyncio
async def test_load_problem_not_found() -> None:
    """Test loading a problem that doesn't exist."""
    tool = LoadProblemTool()

    with patch.object(tool.client, "fetch_problem", new=AsyncMock(return_value=None)):
        with pytest.raises(ValueError, match="Problem not found: invalid-slug"):
            await tool.execute("invalid-slug")


@pytest.mark.asyncio
async def test_load_problem_no_python_code(sample_problem) -> None:  # type: ignore[no-untyped-def,misc]
    """Test loading a problem without Python code snippet."""
    # Remove Python code snippet
    sample_problem.codeSnippets = [
        CodeSnippet(lang="Java", langSlug="java", code="class Solution { }")
    ]

    tool = LoadProblemTool()

    with patch.object(tool.client, "fetch_problem", new=AsyncMock(return_value=sample_problem)):
        result = await tool.execute("two-sum")

    # Without language specified, should return all available code snippets
    assert isinstance(result, dict)
    assert "code_snippets" in result
    assert "java" in result["code_snippets"]
    assert "python3" not in result["code_snippets"]


@pytest.mark.asyncio
async def test_load_problem_by_id_success(sample_problem) -> None:  # type: ignore[no-untyped-def,misc]
    """Test successfully loading a problem by ID."""
    tool = LoadProblemTool()

    with patch.object(tool.client, "fetch_problem_by_id", new=AsyncMock(return_value=sample_problem)):
        result = await tool.execute(problem_id=1)

    assert isinstance(result, dict)
    assert result["problem_id"] == "1"
    assert result["title"] == "Two Sum"
    assert result["title_slug"] == "two-sum"
    assert result["difficulty"] == "Easy"


@pytest.mark.asyncio
async def test_load_problem_no_parameters() -> None:
    """Test that error is raised when no parameters provided."""
    tool = LoadProblemTool()

    with pytest.raises(ValueError, match="Either title_slug, problem_id, or problem_name must be provided"):
        await tool.execute()


@pytest.mark.asyncio
async def test_load_problem_id_not_found() -> None:
    """Test loading a problem ID that doesn't exist."""
    tool = LoadProblemTool()

    with patch.object(tool.client, "fetch_problem_by_id", new=AsyncMock(return_value=None)):
        with pytest.raises(ValueError, match="Problem not found: ID 99999"):
            await tool.execute(problem_id=99999)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_load_problem_real_api() -> None:
    """Integration test with real LeetCode API using title slug."""
    tool = LoadProblemTool()
    result = await tool.execute(title_slug="two-sum")

    assert isinstance(result, dict)
    assert result["problem_id"] == "1"
    assert result["title"] == "Two Sum"
    assert result["difficulty"] == "Easy"
    # Without language specified, should return all code snippets
    assert "code_snippets" in result
    assert "python3" in result["code_snippets"]
    assert len(result["topics"]) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_load_problem_by_id_real_api() -> None:
    """Integration test with real LeetCode API using problem ID."""
    tool = LoadProblemTool()
    result = await tool.execute(problem_id=1)

    assert isinstance(result, dict)
    assert result["problem_id"] == "1"
    assert result["title"] == "Two Sum"
    assert result["difficulty"] == "Easy"
    # Without language specified, should return all code snippets
    assert "code_snippets" in result
    assert "python3" in result["code_snippets"]
    assert len(result["topics"]) > 0