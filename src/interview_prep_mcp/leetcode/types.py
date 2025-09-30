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