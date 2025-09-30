"""Tests for load_problem tool search functionality."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from interview_prep_mcp.tools.load_problem import LoadProblemTool
from interview_prep_mcp.leetcode.types import Problem, ProblemSummary, TopicTag, CodeSnippet


@pytest.fixture
def tool():
    """Create a LoadProblemTool instance."""
    return LoadProblemTool()


@pytest.fixture
def sample_problem():
    """Create a sample Problem object."""
    return Problem(
        questionId="1",
        questionFrontendId="1",
        title="Two Sum",
        titleSlug="two-sum",
        difficulty="Easy",
        content="<p>Given an array...</p>",
        topicTags=[
            TopicTag(name="Array", slug="array"),
            TopicTag(name="Hash Table", slug="hash-table")
        ],
        codeSnippets=[
            CodeSnippet(
                lang="Python3",
                langSlug="python3",
                code="class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:"
            )
        ],
        exampleTestcases="[2,7,11,15]\n9",
        hints=[]
    )


class TestLoadProblemSearch:
    """Tests for load_problem with search functionality."""

    @pytest.mark.asyncio
    async def test_execute_with_problem_name_single_match(self, tool, sample_problem):
        """Test loading problem by name with single match."""
        # Mock search returning single match
        tool.client.search_problems = AsyncMock(return_value=[
            ProblemSummary(
                questionFrontendId="1",
                title="Two Sum",
                titleSlug="two-sum",
                difficulty="Easy"
            )
        ])
        tool.client.fetch_problem = AsyncMock(return_value=sample_problem)

        result = await tool.execute(problem_name="two sum")

        assert isinstance(result, dict)
        assert result["title"] == "Two Sum"
        assert result["problem_id"] == "1"
        tool.client.search_problems.assert_called_once_with("two sum", limit=10)
        tool.client.fetch_problem.assert_called_once_with("two-sum")

    @pytest.mark.asyncio
    async def test_execute_with_problem_name_multiple_matches(self, tool):
        """Test loading problem by name with multiple matches."""
        # Mock search returning multiple matches
        matches = [
            ProblemSummary(
                questionFrontendId="1",
                title="Two Sum",
                titleSlug="two-sum",
                difficulty="Easy"
            ),
            ProblemSummary(
                questionFrontendId="2",
                title="Add Two Numbers",
                titleSlug="add-two-numbers",
                difficulty="Medium"
            ),
            ProblemSummary(
                questionFrontendId="15",
                title="3Sum",
                titleSlug="3sum",
                difficulty="Medium"
            )
        ]
        tool.client.search_problems = AsyncMock(return_value=matches)

        result = await tool.execute(problem_name="sum")

        assert isinstance(result, dict)
        assert "matches" in result
        assert result["count"] == 3
        assert result["query"] == "sum"
        assert len(result["matches"]) == 3
        assert result["matches"][0]["title"] == "Two Sum"
        assert result["matches"][1]["title"] == "Add Two Numbers"

    @pytest.mark.asyncio
    async def test_execute_with_problem_name_no_matches(self, tool):
        """Test loading problem by name with no matches."""
        tool.client.search_problems = AsyncMock(return_value=[])

        with pytest.raises(ValueError, match="No problems found matching"):
            await tool.execute(problem_name="nonexistent problem")

    @pytest.mark.asyncio
    async def test_execute_without_parameters_raises_error(self, tool):
        """Test that calling execute without parameters raises error."""
        with pytest.raises(ValueError, match="Either title_slug, problem_id, or problem_name must be provided"):
            await tool.execute()

    @pytest.mark.asyncio
    async def test_format_search_results(self, tool):
        """Test formatting search results."""
        matches = [
            ProblemSummary(
                questionFrontendId="1",
                title="Two Sum",
                titleSlug="two-sum",
                difficulty="Easy"
            ),
            ProblemSummary(
                questionFrontendId="15",
                title="3Sum",
                titleSlug="3sum",
                difficulty="Medium"
            )
        ]

        result = tool._format_search_results(matches, "sum")

        assert result["query"] == "sum"
        assert result["count"] == 2
        assert len(result["matches"]) == 2
        assert result["matches"][0]["problem_id"] == "1"
        assert result["matches"][0]["title"] == "Two Sum"
        assert result["matches"][0]["title_slug"] == "two-sum"
        assert result["matches"][0]["difficulty"] == "Easy"
        assert "message" in result

    @pytest.mark.asyncio
    async def test_execute_prefers_problem_name_over_other_params(self, tool, sample_problem):
        """Test that problem_name takes precedence when multiple params provided."""
        matches = [
            ProblemSummary(
                questionFrontendId="1",
                title="Two Sum",
                titleSlug="two-sum",
                difficulty="Easy"
            )
        ]
        tool.client.search_problems = AsyncMock(return_value=matches)
        tool.client.fetch_problem = AsyncMock(return_value=sample_problem)
        tool.client.fetch_problem_by_id = AsyncMock()

        # Provide all three parameters
        await tool.execute(problem_name="sum", title_slug="ignored", problem_id=999)

        # Should only call search_problems, not the other methods
        tool.client.search_problems.assert_called_once()
        tool.client.fetch_problem_by_id.assert_not_called()