"""LeetCode GraphQL API client."""
import httpx
from typing import Optional, Dict, List, Union, cast, TypedDict
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from aiolimiter import AsyncLimiter
from .types import Problem, ProblemSummary, CachedProblemInfo


class GraphQLError(TypedDict):
    """Type for GraphQL error objects."""
    message: str


class QuestionData(TypedDict, total=False):
    """Type for question data from GraphQL."""
    questionId: str
    questionFrontendId: str
    title: str
    titleSlug: str
    difficulty: str
    content: str
    topicTags: List[Dict[str, str]]
    codeSnippets: List[Dict[str, str]]
    exampleTestcases: str
    sampleTestCase: str
    hints: List[str]


class GraphQLQuestionResponse(TypedDict, total=False):
    """Type for GraphQL question response."""
    data: Optional[Dict[str, Optional[QuestionData]]]
    errors: Optional[List[GraphQLError]]


class QuestionListItem(TypedDict):
    """Type for question list item."""
    questionFrontendId: str
    title: str
    titleSlug: str
    difficulty: Optional[str]


class ProblemsetQuestionList(TypedDict):
    """Type for problemset question list."""
    total: int
    questions: List[QuestionListItem]


class GraphQLListResponse(TypedDict, total=False):
    """Type for GraphQL list response."""
    data: Optional[Dict[str, ProblemsetQuestionList]]
    errors: Optional[List[GraphQLError]]


class StatData(TypedDict, total=False):
    """Type for stat data from REST API."""
    frontend_question_id: int
    question__title_slug: str
    question__title: str


class DifficultyData(TypedDict, total=False):
    """Type for difficulty data from REST API."""
    level: int


class StatStatusPair(TypedDict, total=False):
    """Type for stat status pair from REST API."""
    stat: StatData
    difficulty: DifficultyData


class RestAPIResponse(TypedDict, total=False):
    """Type for REST API response."""
    stat_status_pairs: List[StatStatusPair]


LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql/"
LEETCODE_API_URL = "https://leetcode.com/api/problems/algorithms/"


class LeetCodeClient:
    """Client for interacting with LeetCode GraphQL API."""

    def __init__(self) -> None:
        self.url = LEETCODE_GRAPHQL_URL
        self.api_url = LEETCODE_API_URL
        self._id_to_slug_cache: Optional[Dict[str, str]] = None
        self._problem_cache: Optional[List[CachedProblemInfo]] = None
        # Rate limiter: 10 requests per second to be respectful to LeetCode API
        self._rate_limiter = AsyncLimiter(10, 1)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError)),
        reraise=True,
    )
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

        async with self._rate_limiter:
            async with httpx.AsyncClient() as client:
                json_payload: Dict[str, Union[str, Dict[str, str]]] = {
                    "query": query,
                    "variables": variables
                }
                response = await client.post(
                    self.url,
                    json=json_payload,
                    headers={
                        "Content-Type": "application/json",
                        "Referer": "https://leetcode.com",
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                data: GraphQLQuestionResponse = cast(GraphQLQuestionResponse, response.json())

                if data.get("errors"):
                    errors = data["errors"]
                    error_messages: List[str] = [
                        error.get("message", "") for error in (errors or [])
                    ]
                    raise ValueError(f"GraphQL errors: {', '.join(error_messages)}")

                if not data.get("data") or not data["data"] or not data["data"].get("question"):
                    return None

                question_data = data["data"]["question"]
                if question_data is None:
                    return None

                # Use Pydantic's model_validate which handles nested model conversion automatically
                # This will validate all fields and raise ValidationError for missing required fields
                return Problem.model_validate(question_data)

    async def _build_id_to_slug_cache(self) -> Dict[str, str]:
        """
        Build a cache mapping problem IDs to title slugs.
        Uses pagination to fetch all problems efficiently.
        Also populates _problem_cache with full problem info.

        Returns:
            Dictionary mapping questionFrontendId to titleSlug

        Raises:
            httpx.HTTPError: If the request fails
            ValueError: If the response format is invalid
        """
        cache: Dict[str, str] = {}
        problem_list: List[CachedProblemInfo] = []

        # GraphQL query with pagination - now includes title and difficulty
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
                    title
                    titleSlug
                    difficulty
                }
            }
        }
        """

        limit = 100
        skip = 0

        async with httpx.AsyncClient() as client:
            while True:
                variables: Dict[str, Union[str, int, Dict[str, Union[str, int]]]] = {
                    "categorySlug": "",
                    "skip": skip,
                    "limit": limit,
                    "filters": {}
                }

                try:
                    json_payload: Dict[str, Union[str, Dict[str, Union[str, int, Dict[str, Union[str, int]]]]]] = {
                        "query": query,
                        "variables": variables
                    }
                    async with self._rate_limiter:
                        response = await client.post(
                            self.url,
                            json=json_payload,
                            headers={
                                "Content-Type": "application/json",
                                "Referer": "https://leetcode.com",
                            },
                            timeout=30.0,
                        )
                        response.raise_for_status()
                        data: GraphQLListResponse = cast(GraphQLListResponse, response.json())

                    if data.get("errors"):
                        # Try fallback API
                        return await self._build_cache_from_api()

                    if not data.get("data") or not data["data"]:
                        break

                    problem_set_data = data["data"]["problemsetQuestionList"]
                    questions = problem_set_data["questions"]
                    if not questions:
                        break

                    # Add to both caches
                    for question in questions:
                        question_id = question["questionFrontendId"]
                        title_slug = question["titleSlug"]
                        cache[question_id] = title_slug
                        problem_list.append(CachedProblemInfo(
                            questionFrontendId=question["questionFrontendId"],
                            title=question["title"],
                            titleSlug=question["titleSlug"],
                            difficulty=question["difficulty"]
                        ))

                    # Check if we've fetched all problems
                    total = problem_set_data["total"]
                    skip += limit
                    if skip >= total:
                        break

                except Exception:
                    # Try fallback API
                    return await self._build_cache_from_api()

        # Store the full problem cache
        self._problem_cache = problem_list
        return cache

    async def _build_cache_from_api(self) -> Dict[str, str]:
        """
        Fallback method to build cache using REST API.
        Also populates _problem_cache with full problem info.

        Returns:
            Dictionary mapping questionFrontendId to titleSlug

        Raises:
            httpx.HTTPError: If the request fails
        """
        cache: Dict[str, str] = {}
        problem_list: List[CachedProblemInfo] = []

        async with httpx.AsyncClient() as client:
            async with self._rate_limiter:
                response = await client.get(
                    self.api_url,
                    headers={"Referer": "https://leetcode.com"},
                    timeout=30.0,
                )
                response.raise_for_status()
                data: RestAPIResponse = cast(RestAPIResponse, response.json())

            if data.get("stat_status_pairs"):
                stat_status_pairs = data["stat_status_pairs"]
                for item in stat_status_pairs:
                    stat = item.get("stat", {})
                    difficulty_info = item.get("difficulty", {})

                    frontend_id_int = stat.get("frontend_question_id", 0)
                    frontend_id = str(frontend_id_int)
                    slug = stat.get("question__title_slug", "")
                    title = stat.get("question__title", "")
                    difficulty_level = difficulty_info.get("level", 0)

                    # Map difficulty level to string
                    difficulty_map: Dict[int, str] = {1: "Easy", 2: "Medium", 3: "Hard"}
                    difficulty: Optional[str] = difficulty_map.get(difficulty_level)

                    if frontend_id and slug:
                        cache[frontend_id] = slug
                        problem_list.append(CachedProblemInfo(
                            questionFrontendId=frontend_id,
                            title=title,
                            titleSlug=slug,
                            difficulty=difficulty
                        ))

        # Store the full problem cache
        self._problem_cache = problem_list
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

    async def search_problems(self, query: str, limit: int = 10) -> List[ProblemSummary]:
        """
        Search for problems by title or keywords using cached data.

        Args:
            query: Search query (title or keywords)
            limit: Maximum number of results to return (default: 10)

        Returns:
            List of ProblemSummary objects matching the query
        """
        # Build cache if not already built
        if self._problem_cache is None:
            await self._build_id_to_slug_cache()

        # Search through cached problems (fast, no API calls)
        query_lower = query.lower()
        matches: List[ProblemSummary] = []

        # Assert that cache is not None after initialization
        assert self._problem_cache is not None, "Problem cache should be initialized"

        for problem in self._problem_cache:
            title_lower: str = problem.title.lower()
            slug_lower: str = problem.titleSlug.lower()

            # Match if query is in title or slug
            if query_lower in title_lower or query_lower in slug_lower:
                matches.append(ProblemSummary(
                    questionFrontendId=problem.questionFrontendId,
                    title=problem.title,
                    titleSlug=problem.titleSlug,
                    difficulty=problem.difficulty
                ))

                if len(matches) >= limit:
                    break

        return matches