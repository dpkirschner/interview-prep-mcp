"""Tool for loading LeetCode problems."""
from typing import Optional
from ..leetcode.client import LeetCodeClient
from ..leetcode.types import Problem
from bs4 import BeautifulSoup


class LoadProblemTool:
    """Tool for fetching and formatting LeetCode problems."""

    def __init__(self):
        self.client = LeetCodeClient()

    async def initialize(self):
        """
        Initialize the tool by preloading the problem ID cache.
        This should be called when the server starts to hide latency.
        """
        # Trigger cache build by calling _get_slug_by_id with a dummy ID
        # This will populate the cache for all subsequent calls
        await self.client._get_slug_by_id(1)

    async def execute(self, title_slug: Optional[str] = None, problem_id: Optional[int] = None) -> dict:
        """
        Load a LeetCode problem by its title slug or problem ID.

        Args:
            title_slug: The URL-friendly slug of the problem (e.g., "two-sum")
            problem_id: The frontend ID of the problem (e.g., 1)

        Returns:
            Dictionary containing formatted problem information

        Raises:
            ValueError: If the problem is not found or fetch fails
        """
        if not title_slug and not problem_id:
            raise ValueError("Either title_slug or problem_id must be provided")

        if problem_id:
            problem = await self.client.fetch_problem_by_id(problem_id)
            identifier = f"ID {problem_id}"
        else:
            problem = await self.client.fetch_problem(title_slug)
            identifier = title_slug

        if not problem:
            raise ValueError(f"Problem not found: {identifier}")

        return self._format_problem(problem)

    def _format_problem(self, problem: Problem) -> dict:
        """
        Format problem data for display.

        Args:
            problem: The Problem object to format

        Returns:
            Dictionary with formatted problem information
        """
        # Parse HTML content to plain text
        soup = BeautifulSoup(problem.content, "html.parser")
        description = soup.get_text(separator="\n").strip()

        # Get Python code snippet if available
        python_code = None
        for snippet in problem.codeSnippets:
            if snippet.langSlug == "python3":
                python_code = snippet.code
                break

        # Format topic tags
        topics = [tag.name for tag in problem.topicTags]

        return {
            "problem_id": problem.questionFrontendId,
            "title": problem.title,
            "title_slug": problem.titleSlug,
            "difficulty": problem.difficulty,
            "description": description,
            "topics": topics,
            "python_code": python_code,
            "hints": problem.hints,
            "example_test_cases": problem.exampleTestcases,
        }