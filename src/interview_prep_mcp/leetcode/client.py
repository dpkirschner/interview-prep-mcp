"""LeetCode GraphQL API client."""
import httpx
from typing import Optional
from .types import Problem


LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql/"


class LeetCodeClient:
    """Client for interacting with LeetCode GraphQL API."""

    def __init__(self):
        self.url = LEETCODE_GRAPHQL_URL

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