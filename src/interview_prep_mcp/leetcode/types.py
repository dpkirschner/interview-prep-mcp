"""Data models for LeetCode problems."""
from typing import Optional
from pydantic import BaseModel


class TopicTag(BaseModel):
    """A topic tag for a problem."""
    name: str
    slug: str


class CodeSnippet(BaseModel):
    """Code snippet in a specific language."""
    lang: str
    langSlug: str
    code: str


class Problem(BaseModel):
    """A LeetCode problem."""
    questionId: str
    questionFrontendId: str
    title: str
    titleSlug: str
    difficulty: str
    content: str
    topicTags: list[TopicTag]
    codeSnippets: list[CodeSnippet]
    exampleTestcases: Optional[str] = None
    sampleTestCase: Optional[str] = None
    hints: list[str] = []


class ProblemSummary(BaseModel):
    """A summary of a LeetCode problem (used for search results)."""
    questionFrontendId: str
    title: str
    titleSlug: str
    difficulty: Optional[str] = None


class CachedProblemInfo(BaseModel):
    """Cached problem information for fast lookups."""
    questionFrontendId: str
    title: str
    titleSlug: str
    difficulty: Optional[str] = None