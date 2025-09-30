"""Tests for load_problem tool."""
import pytest
from unittest.mock import AsyncMock, patch
from interview_prep_mcp.tools.load_problem import LoadProblemTool
from interview_prep_mcp.leetcode.types import Problem, CodeSnippet, TopicTag


@pytest.fixture
def sample_problem():
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
async def test_load_problem_success(sample_problem):
    """Test successfully loading a problem."""
    tool = LoadProblemTool()

    with patch.object(tool.client, "fetch_problem", new=AsyncMock(return_value=sample_problem)):
        result = await tool.execute("two-sum")

    assert result["problem_id"] == "1"
    assert result["title"] == "Two Sum"
    assert result["title_slug"] == "two-sum"
    assert result["difficulty"] == "Easy"
    assert "Given an array of integers" in result["description"]
    assert result["topics"] == ["Array", "Hash Table"]
    assert result["python_code"] is not None
    assert "class Solution:" in result["python_code"]
    assert result["hints"] == ["A hint for solving the problem"]
    assert result["example_test_cases"] == "[2,7,11,15]\n9"


@pytest.mark.asyncio
async def test_load_problem_not_found():
    """Test loading a problem that doesn't exist."""
    tool = LoadProblemTool()

    with patch.object(tool.client, "fetch_problem", new=AsyncMock(return_value=None)):
        with pytest.raises(ValueError, match="Problem not found: invalid-slug"):
            await tool.execute("invalid-slug")


@pytest.mark.asyncio
async def test_load_problem_no_python_code(sample_problem):
    """Test loading a problem without Python code snippet."""
    # Remove Python code snippet
    sample_problem.codeSnippets = [
        CodeSnippet(lang="Java", langSlug="java", code="class Solution { }")
    ]

    tool = LoadProblemTool()

    with patch.object(tool.client, "fetch_problem", new=AsyncMock(return_value=sample_problem)):
        result = await tool.execute("two-sum")

    assert result["python_code"] is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_load_problem_real_api():
    """Integration test with real LeetCode API."""
    tool = LoadProblemTool()
    result = await tool.execute("two-sum")

    assert result["problem_id"] == "1"
    assert result["title"] == "Two Sum"
    assert result["difficulty"] == "Easy"
    assert result["python_code"] is not None
    assert len(result["topics"]) > 0