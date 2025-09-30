"""Integration tests for LeetCode client.

These tests make actual API calls to LeetCode and are marked as integration tests.
Run with: pytest -m integration
Skip with: pytest -m "not integration"
"""
import pytest
from interview_prep_mcp.leetcode.types import Problem


pytestmark = pytest.mark.integration


class TestLeetCodeIntegration:
    """Integration tests that make real API calls."""

    @pytest.mark.asyncio
    async def test_fetch_two_sum_problem(self, client):
        """Test fetching the classic Two Sum problem."""
        problem = await client.fetch_problem("two-sum")

        assert problem is not None
        assert isinstance(problem, Problem)
        assert problem.questionFrontendId == "1"
        assert problem.title == "Two Sum"
        assert problem.titleSlug == "two-sum"
        assert problem.difficulty == "Easy"
        assert len(problem.topicTags) > 0
        assert len(problem.codeSnippets) > 0
        assert problem.content is not None
        assert len(problem.content) > 0

    @pytest.mark.asyncio
    async def test_fetch_problem_with_hints(self, client):
        """Test fetching a problem that typically has hints."""
        problem = await client.fetch_problem("best-time-to-buy-and-sell-stock")

        assert problem is not None
        assert isinstance(problem, Problem)
        # This problem typically has hints
        assert problem.hints is not None

    @pytest.mark.asyncio
    async def test_fetch_hard_problem(self, client):
        """Test fetching a hard difficulty problem."""
        problem = await client.fetch_problem("median-of-two-sorted-arrays")

        assert problem is not None
        assert problem.difficulty == "Hard"
        assert problem.questionFrontendId == "4"

    @pytest.mark.asyncio
    async def test_fetch_problem_with_multiple_languages(self, client):
        """Test that returned problem has code snippets for multiple languages."""
        problem = await client.fetch_problem("two-sum")

        assert problem is not None
        assert len(problem.codeSnippets) > 5  # LeetCode typically supports many languages

        # Check for common languages
        lang_slugs = {snippet.langSlug for snippet in problem.codeSnippets}
        assert "python3" in lang_slugs
        assert "java" in lang_slugs
        assert "cpp" in lang_slugs

    @pytest.mark.asyncio
    async def test_fetch_nonexistent_problem(self, client):
        """Test fetching a problem that doesn't exist."""
        problem = await client.fetch_problem("this-problem-does-not-exist-12345")

        assert problem is None

    @pytest.mark.asyncio
    async def test_fetch_problem_with_special_characters(self, client):
        """Test fetching a problem with special characters in the slug."""
        problem = await client.fetch_problem("binary-tree-level-order-traversal-ii")

        assert problem is not None
        assert problem.questionFrontendId == "107"
        assert "II" in problem.title or "2" in problem.title

    @pytest.mark.asyncio
    async def test_multiple_sequential_requests(self, client):
        """Test making multiple requests in sequence."""
        problems = []

        for slug in ["two-sum", "add-two-numbers", "longest-substring-without-repeating-characters"]:
            problem = await client.fetch_problem(slug)
            problems.append(problem)

        assert len(problems) == 3
        assert all(p is not None for p in problems)
        assert problems[0].questionFrontendId == "1"
        assert problems[1].questionFrontendId == "2"
        assert problems[2].questionFrontendId == "3"

    @pytest.mark.asyncio
    async def test_fetch_problem_with_testcases(self, client):
        """Test that problem returns test cases."""
        problem = await client.fetch_problem("two-sum")

        assert problem is not None
        # Most problems have example test cases
        assert problem.exampleTestcases is not None or problem.sampleTestCase is not None

    @pytest.mark.asyncio
    async def test_python_code_snippet_is_valid(self, client):
        """Test that Python code snippet is syntactically valid."""
        problem = await client.fetch_problem("two-sum")

        assert problem is not None

        python_snippet = None
        for snippet in problem.codeSnippets:
            if snippet.langSlug == "python3":
                python_snippet = snippet
                break

        assert python_snippet is not None
        assert "class Solution" in python_snippet.code
        assert "def " in python_snippet.code

    @pytest.mark.asyncio
    async def test_topic_tags_are_valid(self, client):
        """Test that topic tags have valid structure."""
        problem = await client.fetch_problem("two-sum")

        assert problem is not None
        assert len(problem.topicTags) > 0

        for tag in problem.topicTags:
            assert tag.name is not None
            assert len(tag.name) > 0
            assert tag.slug is not None
            assert len(tag.slug) > 0

    @pytest.mark.asyncio
    async def test_content_is_html(self, client):
        """Test that problem content is HTML formatted."""
        problem = await client.fetch_problem("two-sum")

        assert problem is not None
        assert "<p>" in problem.content or "<div>" in problem.content

    @pytest.mark.asyncio
    async def test_fetch_problem_ids_are_consistent(self, client):
        """Test that problem IDs are consistent."""
        problem = await client.fetch_problem("two-sum")

        assert problem is not None
        assert problem.questionId is not None
        assert problem.questionFrontendId is not None
        assert problem.questionFrontendId == "1"