"""Tests for load_problem tool language-specific functionality."""
import pytest
from unittest.mock import AsyncMock
from interview_prep_mcp.tools.load_problem import LoadProblemTool
from interview_prep_mcp.leetcode.types import Problem, CodeSnippet, TopicTag


@pytest.fixture
def sample_problem_multi_language():
    """Create a sample problem with multiple language code snippets."""
    return Problem(
        questionId="1",
        questionFrontendId="1",
        title="Two Sum",
        titleSlug="two-sum",
        difficulty="Easy",
        content="<p>Given an array of integers...</p>",
        topicTags=[
            TopicTag(name="Array", slug="array"),
            TopicTag(name="Hash Table", slug="hash-table"),
        ],
        codeSnippets=[
            CodeSnippet(
                lang="Python3",
                langSlug="python3",
                code="class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        pass"
            ),
            CodeSnippet(
                lang="Java",
                langSlug="java",
                code="class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        \n    }\n}"
            ),
            CodeSnippet(
                lang="Go",
                langSlug="golang",
                code="func twoSum(nums []int, target int) []int {\n    \n}"
            ),
            CodeSnippet(
                lang="C++",
                langSlug="cpp",
                code="class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        \n    }\n};"
            ),
        ],
        exampleTestcases="[2,7,11,15]\n9",
        sampleTestCase="[2,7,11,15]\n9",
        hints=["A hint"],
    )


@pytest.fixture
def tool():
    """Create a LoadProblemTool instance."""
    return LoadProblemTool()


class TestLanguageSpecificLoading:
    """Tests for language-specific problem loading."""

    @pytest.mark.asyncio
    async def test_load_problem_with_python_language(self, tool, sample_problem_multi_language):
        """Test loading problem with Python language specified."""
        tool.client.fetch_problem = AsyncMock(return_value=sample_problem_multi_language)

        result = await tool.execute(title_slug="two-sum", language="python")

        assert "code" in result
        assert "class Solution:" in result["code"]
        assert "def twoSum" in result["code"]
        assert result["language"] == "python3"
        assert result["suggested_filename"] == "1_two_sum.py"
        # Should not have code_snippets (only specific language)
        assert "code_snippets" not in result

    @pytest.mark.asyncio
    async def test_load_problem_with_java_language(self, tool, sample_problem_multi_language):
        """Test loading problem with Java language specified."""
        tool.client.fetch_problem = AsyncMock(return_value=sample_problem_multi_language)

        result = await tool.execute(title_slug="two-sum", language="java")

        assert "code" in result
        assert "public int[] twoSum" in result["code"]
        assert result["language"] == "java"
        assert result["suggested_filename"] == "1_two_sum.java"

    @pytest.mark.asyncio
    async def test_load_problem_with_golang(self, tool, sample_problem_multi_language):
        """Test loading problem with Go language specified."""
        tool.client.fetch_problem = AsyncMock(return_value=sample_problem_multi_language)

        result = await tool.execute(title_slug="two-sum", language="golang")

        assert "code" in result
        assert "func twoSum" in result["code"]
        assert result["language"] == "golang"
        assert result["suggested_filename"] == "1_two_sum.go"

    @pytest.mark.asyncio
    async def test_load_problem_with_go_alias(self, tool, sample_problem_multi_language):
        """Test that 'go' alias works for 'golang'."""
        tool.client.fetch_problem = AsyncMock(return_value=sample_problem_multi_language)

        result = await tool.execute(title_slug="two-sum", language="go")

        assert "code" in result
        assert result["language"] == "golang"

    @pytest.mark.asyncio
    async def test_load_problem_no_language_returns_all(self, tool, sample_problem_multi_language):
        """Test that omitting language returns all code snippets."""
        tool.client.fetch_problem = AsyncMock(return_value=sample_problem_multi_language)

        result = await tool.execute(title_slug="two-sum")

        assert "code_snippets" in result
        assert "python3" in result["code_snippets"]
        assert "java" in result["code_snippets"]
        assert "golang" in result["code_snippets"]
        assert "cpp" in result["code_snippets"]
        assert len(result["code_snippets"]) == 4
        # Should not have individual code/language fields
        assert "code" not in result
        assert "language" not in result
        assert "suggested_filename" not in result

    @pytest.mark.asyncio
    async def test_load_problem_unsupported_language(self, tool, sample_problem_multi_language):
        """Test error response when language not available."""
        tool.client.fetch_problem = AsyncMock(return_value=sample_problem_multi_language)

        result = await tool.execute(title_slug="two-sum", language="rust")

        assert "error" in result
        assert "rust" in result["error"].lower()
        assert "available_languages" in result
        assert "python3" in result["available_languages"]
        assert result["problem_id"] == "1"
        assert result["title"] == "Two Sum"

    @pytest.mark.asyncio
    async def test_load_problem_language_case_insensitive(self, tool, sample_problem_multi_language):
        """Test that language matching is case-insensitive."""
        tool.client.fetch_problem = AsyncMock(return_value=sample_problem_multi_language)

        result = await tool.execute(title_slug="two-sum", language="PYTHON")

        assert "code" in result
        assert result["language"] == "python3"

    @pytest.mark.asyncio
    async def test_load_problem_by_id_with_language(self, tool, sample_problem_multi_language):
        """Test loading by problem ID with language."""
        tool.client.fetch_problem_by_id = AsyncMock(return_value=sample_problem_multi_language)

        result = await tool.execute(problem_id=1, language="java")

        assert "code" in result
        assert result["language"] == "java"
        assert result["suggested_filename"] == "1_two_sum.java"

    @pytest.mark.asyncio
    async def test_load_problem_cpp_language(self, tool, sample_problem_multi_language):
        """Test loading with C++ language."""
        tool.client.fetch_problem = AsyncMock(return_value=sample_problem_multi_language)

        result = await tool.execute(title_slug="two-sum", language="cpp")

        assert "code" in result
        assert "vector<int> twoSum" in result["code"]
        assert result["language"] == "cpp"
        assert result["suggested_filename"] == "1_two_sum.cpp"

    @pytest.mark.asyncio
    async def test_load_problem_language_alias_python(self, tool, sample_problem_multi_language):
        """Test that 'py' and 'python' both work."""
        tool.client.fetch_problem = AsyncMock(return_value=sample_problem_multi_language)

        result_py = await tool.execute(title_slug="two-sum", language="py")
        assert result_py["language"] == "python3"

        result_python = await tool.execute(title_slug="two-sum", language="python")
        assert result_python["language"] == "python3"


class TestFindCodeSnippet:
    """Tests for _find_code_snippet helper method."""

    def test_find_by_exact_langslug(self, tool, sample_problem_multi_language):
        """Test finding by exact langSlug match."""
        snippet = tool._find_code_snippet(sample_problem_multi_language, "python3")
        assert snippet is not None
        assert snippet.langSlug == "python3"

    def test_find_by_language_name(self, tool, sample_problem_multi_language):
        """Test finding by language name."""
        snippet = tool._find_code_snippet(sample_problem_multi_language, "Python3")
        assert snippet is not None
        assert snippet.lang == "Python3"

    def test_find_by_alias(self, tool, sample_problem_multi_language):
        """Test finding by common alias."""
        snippet = tool._find_code_snippet(sample_problem_multi_language, "go")
        assert snippet is not None
        assert snippet.langSlug == "golang"

    def test_find_returns_none_for_missing(self, tool, sample_problem_multi_language):
        """Test that None is returned for missing language."""
        snippet = tool._find_code_snippet(sample_problem_multi_language, "rust")
        assert snippet is None

    def test_find_case_insensitive(self, tool, sample_problem_multi_language):
        """Test case-insensitive matching."""
        snippet = tool._find_code_snippet(sample_problem_multi_language, "JAVA")
        assert snippet is not None
        assert snippet.langSlug == "java"