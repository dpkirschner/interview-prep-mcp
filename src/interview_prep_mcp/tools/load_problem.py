"""Tool for loading LeetCode problems."""
from typing import Optional
from ..leetcode.client import LeetCodeClient
from ..leetcode.types import Problem
from bs4 import BeautifulSoup


class LoadProblemTool:
    """Tool for fetching and formatting LeetCode problems."""

    def __init__(self):
        self.client = LeetCodeClient()

    async def execute(self, title_slug: str) -> dict:
        """
        Load a LeetCode problem by its title slug.

        Args:
            title_slug: The URL-friendly slug of the problem (e.g., "two-sum")

        Returns:
            Dictionary containing formatted problem information

        Raises:
            ValueError: If the problem is not found or fetch fails
        """
        problem = await self.client.fetch_problem(title_slug)

        if not problem:
            raise ValueError(f"Problem not found: {title_slug}")

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