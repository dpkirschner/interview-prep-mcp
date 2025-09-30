"""Tool for loading LeetCode problems."""
from typing import Optional, Union
from ..leetcode.client import LeetCodeClient
from ..leetcode.types import Problem, ProblemSummary, CodeSnippet
from ..file_generator.naming import suggest_filename
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

    async def execute(
        self,
        title_slug: Optional[str] = None,
        problem_id: Optional[int] = None,
        problem_name: Optional[str] = None,
        language: Optional[str] = None
    ) -> Union[dict, list[dict]]:
        """
        Load a LeetCode problem by its title slug, problem ID, or name.

        Args:
            title_slug: The URL-friendly slug of the problem (e.g., "two-sum")
            problem_id: The frontend ID of the problem (e.g., 1)
            problem_name: Search query for problem name/title (e.g., "two sum")
            language: Optional language for code snippet (e.g., "python", "java", "golang")
                     If omitted, returns all available code snippets

        Returns:
            Dictionary containing formatted problem information if single match,
            or list of dictionaries with search results if multiple matches

        Raises:
            ValueError: If the problem is not found or fetch fails
        """
        if not title_slug and not problem_id and not problem_name:
            raise ValueError("Either title_slug, problem_id, or problem_name must be provided")

        # Handle search by name
        if problem_name:
            matches = await self.client.search_problems(problem_name, limit=10)

            if not matches:
                raise ValueError(f"No problems found matching: {problem_name}")

            # If exactly one match, load and return the full problem
            if len(matches) == 1:
                problem = await self.client.fetch_problem(matches[0].titleSlug)
                if problem:
                    return self._format_problem(problem, language)
                else:
                    raise ValueError(f"Problem not found: {matches[0].titleSlug}")

            # Multiple matches - return search results
            return self._format_search_results(matches, problem_name)

        # Handle fetch by ID or slug
        if problem_id:
            problem = await self.client.fetch_problem_by_id(problem_id)
            identifier = f"ID {problem_id}"
        else:
            problem = await self.client.fetch_problem(title_slug)
            identifier = title_slug

        if not problem:
            raise ValueError(f"Problem not found: {identifier}")

        return self._format_problem(problem, language)

    def _find_code_snippet(self, problem: Problem, language: str) -> Optional[CodeSnippet]:
        """
        Find code snippet by language name or langSlug (case-insensitive).

        Args:
            problem: The Problem object
            language: Language name or slug (e.g., "python", "python3", "java", "golang")

        Returns:
            CodeSnippet if found, None otherwise
        """
        language_lower = language.lower()

        # Try exact langSlug match first
        for snippet in problem.codeSnippets:
            if snippet.langSlug.lower() == language_lower:
                return snippet

        # Try language name match
        for snippet in problem.codeSnippets:
            if snippet.lang.lower() == language_lower:
                return snippet

        # Try common aliases
        aliases = {
            "py": "python3",
            "python": "python3",
            "js": "javascript",
            "ts": "typescript",
            "go": "golang",
            "c++": "cpp",
            "cplusplus": "cpp",
            "c#": "csharp",
            "cs": "csharp",
            "rb": "ruby",
            "kt": "kotlin",
            "rs": "rust",
        }

        if language_lower in aliases:
            target_slug = aliases[language_lower]
            for snippet in problem.codeSnippets:
                if snippet.langSlug.lower() == target_slug:
                    return snippet

        return None

    def _format_problem(self, problem: Problem, language: Optional[str] = None) -> dict:
        """
        Format problem data for display.

        Args:
            problem: The Problem object to format
            language: Optional language filter for code snippets

        Returns:
            Dictionary with formatted problem information
        """
        # Parse HTML content to plain text
        soup = BeautifulSoup(problem.content, "html.parser")
        description = soup.get_text(separator="\n").strip()

        # Format topic tags
        topics = [tag.name for tag in problem.topicTags]

        # Base response
        result = {
            "problem_id": problem.questionFrontendId,
            "title": problem.title,
            "title_slug": problem.titleSlug,
            "difficulty": problem.difficulty,
            "description": description,
            "topics": topics,
            "hints": problem.hints,
            "example_test_cases": problem.exampleTestcases,
        }

        # Handle language-specific or all code snippets
        if language:
            # Find specific language
            code_snippet = self._find_code_snippet(problem, language)

            if not code_snippet:
                # Return error response
                available = [s.langSlug for s in problem.codeSnippets]
                return {
                    "error": f"Language '{language}' not available for this problem",
                    "available_languages": available,
                    "problem_id": problem.questionFrontendId,
                    "title": problem.title,
                    "title_slug": problem.titleSlug,
                }

            result["language"] = code_snippet.langSlug
            result["code"] = code_snippet.code
            result["suggested_filename"] = suggest_filename(
                problem.questionFrontendId,
                problem.title,
                code_snippet.langSlug
            )
        else:
            # Return all code snippets
            result["code_snippets"] = {
                snippet.langSlug: snippet.code
                for snippet in problem.codeSnippets
            }

        return result

    def _format_search_results(self, matches: list[ProblemSummary], query: str) -> dict:
        """
        Format search results for display.

        Args:
            matches: List of matching problem summaries
            query: The original search query

        Returns:
            Dictionary with search results information
        """
        return {
            "query": query,
            "matches": [
                {
                    "problem_id": match.questionFrontendId,
                    "title": match.title,
                    "title_slug": match.titleSlug,
                    "difficulty": match.difficulty,
                }
                for match in matches
            ],
            "count": len(matches),
            "message": f"Found {len(matches)} problems matching '{query}'. Use title_slug to load a specific problem."
        }