"""LeetCode GraphQL API client."""
import httpx
from typing import Optional, Dict
from .types import Problem


LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql/"
LEETCODE_API_URL = "https://leetcode.com/api/problems/algorithms/"


class LeetCodeClient:
    """Client for interacting with LeetCode GraphQL API."""

    def __init__(self):
        self.url = LEETCODE_GRAPHQL_URL
        self.api_url = LEETCODE_API_URL
        self._id_to_slug_cache: Optional[Dict[str, str]] = None

    async def fetch_problem(self, title_slug: str) -> Optional[Problem]:
        """
        Fetch a problem by its title slug.

        Args:
            title_slug: The URL-friendly slug of the problem (e.g., "two-sum")

        Returns:
            Problem object if found, None otherwise

        Raises:
            httpx.HTTPError: If the request fails
            ValueError: If the response format is invalid
        """
        query = """
        query questionContent($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
                questionFrontendId
                title
                titleSlug
                difficulty
                content
                topicTags {
                    name
                    slug
                }
                codeSnippets {
                    lang
                    langSlug
                    code
                }
                exampleTestcases
                sampleTestCase
                hints
            }
        }
        """

        variables = {"titleSlug": title_slug}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.url,
                json={"query": query, "variables": variables},
                headers={
                    "Content-Type": "application/json",
                    "Referer": "https://leetcode.com",
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            if "errors" in data:
                error_messages = [error.get("message", "") for error in data["errors"]]
                raise ValueError(f"GraphQL errors: {', '.join(error_messages)}")

            if "data" not in data or not data["data"] or not data["data"].get("question"):
                return None

            question_data = data["data"]["question"]
            return Problem(**question_data)

    async def _build_id_to_slug_cache(self) -> Dict[str, str]:
        """
        Build a cache mapping problem IDs to title slugs.
        Uses pagination to fetch all problems efficiently.

        Returns:
            Dictionary mapping questionFrontendId to titleSlug

        Raises:
            httpx.HTTPError: If the request fails
            ValueError: If the response format is invalid
        """
        cache: Dict[str, str] = {}

        # GraphQL query with pagination
        query = """
        query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
            problemsetQuestionList: questionList(
                categorySlug: $categorySlug
                limit: $limit
                skip: $skip
                filters: $filters
            ) {
                total: totalNum
                questions: data {
                    questionFrontendId
                    titleSlug
                }
            }
        }
        """

        limit = 100
        skip = 0

        async with httpx.AsyncClient() as client:
            while True:
                variables = {
                    "categorySlug": "",
                    "skip": skip,
                    "limit": limit,
                    "filters": {}
                }

                try:
                    response = await client.post(
                        self.url,
                        json={"query": query, "variables": variables},
                        headers={
                            "Content-Type": "application/json",
                            "Referer": "https://leetcode.com",
                        },
                        timeout=30.0,
                    )
                    response.raise_for_status()
                    data = response.json()

                    if "errors" in data:
                        # Try fallback API
                        return await self._build_cache_from_api()

                    if "data" not in data or not data["data"]:
                        break

                    questions = data["data"]["problemsetQuestionList"]["questions"]
                    if not questions:
                        break

                    # Add to cache
                    for question in questions:
                        cache[question["questionFrontendId"]] = question["titleSlug"]

                    # Check if we've fetched all problems
                    total = data["data"]["problemsetQuestionList"]["total"]
                    skip += limit
                    if skip >= total:
                        break

                except Exception:
                    # Try fallback API
                    return await self._build_cache_from_api()

        return cache

    async def _build_cache_from_api(self) -> Dict[str, str]:
        """
        Fallback method to build cache using REST API.

        Returns:
            Dictionary mapping questionFrontendId to titleSlug

        Raises:
            httpx.HTTPError: If the request fails
        """
        cache: Dict[str, str] = {}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.api_url,
                headers={"Referer": "https://leetcode.com"},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            if "stat_status_pairs" in data:
                for item in data["stat_status_pairs"]:
                    stat = item.get("stat", {})
                    frontend_id = str(stat.get("frontend_question_id", ""))
                    slug = stat.get("question__title_slug", "")
                    if frontend_id and slug:
                        cache[frontend_id] = slug

        return cache

    async def _get_slug_by_id(self, problem_id: int) -> Optional[str]:
        """
        Get title slug for a given problem ID, using cache.

        Args:
            problem_id: The frontend ID of the problem

        Returns:
            Title slug if found, None otherwise
        """
        # Build cache on first use
        if self._id_to_slug_cache is None:
            self._id_to_slug_cache = await self._build_id_to_slug_cache()

        return self._id_to_slug_cache.get(str(problem_id))

    async def fetch_problem_by_id(self, problem_id: int) -> Optional[Problem]:
        """
        Fetch a problem by its frontend ID.

        Args:
            problem_id: The frontend ID of the problem (e.g., 1 for "Two Sum")

        Returns:
            Problem object if found, None otherwise

        Raises:
            httpx.HTTPError: If the request fails
            ValueError: If the response format is invalid
        """
        # Get title slug from cache
        title_slug = await self._get_slug_by_id(problem_id)

        if not title_slug:
            return None

        # Fetch the full problem details using the title slug
        return await self.fetch_problem(title_slug)