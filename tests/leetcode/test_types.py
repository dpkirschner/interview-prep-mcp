"""Tests for leetcode types."""
import pytest
from pydantic import ValidationError
from interview_prep_mcp.leetcode.types import TopicTag, CodeSnippet, Problem


class TestTopicTag:
    """Tests for TopicTag model."""

    def test_create_topic_tag(self) -> None:
        """Test creating a valid TopicTag."""
        tag = TopicTag(name="Array", slug="array")
        assert tag.name == "Array"
        assert tag.slug == "array"

    def test_topic_tag_validation(self) -> None:
        """Test TopicTag validation."""
        with pytest.raises(ValidationError):
            TopicTag(name="Array")  # type: ignore[call-arg]  # Missing slug


class TestCodeSnippet:
    """Tests for CodeSnippet model."""

    def test_create_code_snippet(self) -> None:
        """Test creating a valid CodeSnippet."""
        snippet = CodeSnippet(
            lang="Python3",
            langSlug="python3",
            code="class Solution:\n    def method(self):\n        pass"
        )
        assert snippet.lang == "Python3"
        assert snippet.langSlug == "python3"
        assert "class Solution" in snippet.code

    def test_code_snippet_validation(self) -> None:
        """Test CodeSnippet validation."""
        with pytest.raises(ValidationError):
            CodeSnippet(lang="Python3", langSlug="python3")  # type: ignore[call-arg]  # Missing code


class TestProblem:
    """Tests for Problem model."""

    def test_create_minimal_problem(self) -> None:
        """Test creating a Problem with minimal required fields."""
        problem = Problem(
            questionId="1",
            questionFrontendId="1",
            title="Two Sum",
            titleSlug="two-sum",
            difficulty="Easy",
            content="<p>Given an array...</p>",
            topicTags=[],
            codeSnippets=[]
        )
        assert problem.questionId == "1"
        assert problem.questionFrontendId == "1"
        assert problem.title == "Two Sum"
        assert problem.titleSlug == "two-sum"
        assert problem.difficulty == "Easy"
        assert problem.topicTags == []
        assert problem.codeSnippets == []
        assert problem.hints == []

    def test_create_full_problem(self) -> None:
        """Test creating a Problem with all fields."""
        problem = Problem(
            questionId="1",
            questionFrontendId="1",
            title="Two Sum",
            titleSlug="two-sum",
            difficulty="Easy",
            content="<p>Given an array...</p>",
            topicTags=[
                TopicTag(name="Array", slug="array"),
                TopicTag(name="Hash Table", slug="hash-table")
            ],
            codeSnippets=[
                CodeSnippet(
                    lang="Python3",
                    langSlug="python3",
                    code="class Solution:\n    pass"
                )
            ],
            exampleTestcases="[2,7,11,15]\n9",
            sampleTestCase="[2,7,11,15]\n9",
            hints=["Use a hash table"]
        )
        assert len(problem.topicTags) == 2
        assert problem.topicTags[0].name == "Array"
        assert len(problem.codeSnippets) == 1
        assert problem.exampleTestcases is not None
        if problem.exampleTestcases is not None:
            assert isinstance(problem.exampleTestcases, str)
        assert problem.sampleTestCase is not None
        if problem.sampleTestCase is not None:
            assert isinstance(problem.sampleTestCase, str)
        assert len(problem.hints) == 1

    def test_problem_optional_fields(self) -> None:
        """Test that optional fields can be None."""
        problem = Problem(
            questionId="1",
            questionFrontendId="1",
            title="Two Sum",
            titleSlug="two-sum",
            difficulty="Easy",
            content="<p>Given an array...</p>",
            topicTags=[],
            codeSnippets=[],
            exampleTestcases=None,
            sampleTestCase=None
        )
        assert problem.exampleTestcases is None
        assert problem.sampleTestCase is None

    def test_problem_validation(self) -> None:
        """Test Problem validation."""
        with pytest.raises(ValidationError):
            Problem(
                questionId="1",
                title="Two Sum",
                # Missing required fields
            )  # type: ignore[call-arg]

    def test_problem_with_empty_lists(self) -> None:
        """Test Problem with empty topicTags and codeSnippets."""
        problem = Problem(
            questionId="999",
            questionFrontendId="999",
            title="Empty Lists Problem",
            titleSlug="empty-lists-problem",
            difficulty="Medium",
            content="<p>Test content</p>",
            topicTags=[],
            codeSnippets=[]
        )
        assert problem.topicTags == []
        assert problem.codeSnippets == []
        assert problem.hints == []

    def test_problem_with_multiple_hints(self) -> None:
        """Test Problem with multiple hints."""
        hints = ["Hint 1", "Hint 2", "Hint 3"]
        problem = Problem(
            questionId="1",
            questionFrontendId="1",
            title="Multi Hint Problem",
            titleSlug="multi-hint-problem",
            difficulty="Hard",
            content="<p>Complex problem</p>",
            topicTags=[],
            codeSnippets=[],
            hints=hints
        )
        assert len(problem.hints) == 3
        assert problem.hints == hints

    def test_problem_difficulty_values(self) -> None:
        """Test Problem with different difficulty values."""
        for difficulty in ["Easy", "Medium", "Hard"]:
            problem = Problem(
                questionId="1",
                questionFrontendId="1",
                title="Test",
                titleSlug="test",
                difficulty=difficulty,
                content="<p>Test</p>",
                topicTags=[],
                codeSnippets=[]
            )
            assert problem.difficulty == difficulty

    def test_problem_with_html_content(self) -> None:
        """Test Problem with complex HTML content."""
        html_content = "<p>Given an array <code>nums</code> of <strong>n</strong> integers...</p>"
        problem = Problem(
            questionId="1",
            questionFrontendId="1",
            title="Test",
            titleSlug="test",
            difficulty="Easy",
            content=html_content,
            topicTags=[],
            codeSnippets=[]
        )
        assert problem.content == html_content
        assert "<code>" in problem.content
        assert "<strong>" in problem.content

    def test_problem_with_multiline_testcases(self) -> None:
        """Test Problem with multiline test cases."""
        testcases = "[2,7,11,15]\n9\n[3,2,4]\n6\n[3,3]\n6"
        problem = Problem(
            questionId="1",
            questionFrontendId="1",
            title="Test",
            titleSlug="test",
            difficulty="Easy",
            content="<p>Test</p>",
            topicTags=[],
            codeSnippets=[],
            exampleTestcases=testcases,
            sampleTestCase="[2,7,11,15]\n9"
        )
        assert problem.exampleTestcases is not None
        if problem.exampleTestcases is not None:
            assert "\n" in problem.exampleTestcases
            assert problem.exampleTestcases.count("\n") > 1

    def test_code_snippet_with_multiple_languages(self) -> None:
        """Test creating multiple CodeSnippets for different languages."""
        snippets = [
            CodeSnippet(lang="Python3", langSlug="python3", code="class Solution:\n    pass"),
            CodeSnippet(lang="Java", langSlug="java", code="class Solution {\n}"),
            CodeSnippet(lang="C++", langSlug="cpp", code="class Solution {\n};"),
        ]
        problem = Problem(
            questionId="1",
            questionFrontendId="1",
            title="Multi Language",
            titleSlug="multi-language",
            difficulty="Easy",
            content="<p>Test</p>",
            topicTags=[],
            codeSnippets=snippets
        )
        assert len(problem.codeSnippets) == 3
        assert problem.codeSnippets[0].langSlug == "python3"
        assert problem.codeSnippets[1].langSlug == "java"
        assert problem.codeSnippets[2].langSlug == "cpp"

    def test_topic_tag_special_characters(self) -> None:
        """Test TopicTag with special characters in name."""
        tag = TopicTag(name="Depth-First Search", slug="depth-first-search")
        assert tag.name == "Depth-First Search"
        assert "-" in tag.slug

    def test_code_snippet_multiline_code(self) -> None:
        """Test CodeSnippet with multiline code."""
        multiline_code = """class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # Your code here
        pass"""
        snippet = CodeSnippet(
            lang="Python3",
            langSlug="python3",
            code=multiline_code
        )
        assert snippet.code.count("\n") == 3
        assert "def twoSum" in snippet.code

    def test_problem_json_serialization(self) -> None:
        """Test that Problem can be serialized to JSON."""
        problem = Problem(
            questionId="1",
            questionFrontendId="1",
            title="Two Sum",
            titleSlug="two-sum",
            difficulty="Easy",
            content="<p>Test</p>",
            topicTags=[TopicTag(name="Array", slug="array")],
            codeSnippets=[CodeSnippet(lang="Python3", langSlug="python3", code="pass")]
        )
        json_data = problem.model_dump()
        assert isinstance(json_data, dict)
        assert json_data["questionId"] == "1"
        assert json_data["title"] == "Two Sum"
        assert isinstance(json_data["topicTags"], list)
        assert len(json_data["topicTags"]) == 1
        assert isinstance(json_data["codeSnippets"], list)
        assert len(json_data["codeSnippets"]) == 1

    def test_problem_empty_content(self) -> None:
        """Test Problem with empty content string."""
        problem = Problem(
            questionId="1",
            questionFrontendId="1",
            title="Empty Content",
            titleSlug="empty-content",
            difficulty="Easy",
            content="",
            topicTags=[],
            codeSnippets=[]
        )
        assert problem.content == ""

    def test_code_snippet_empty_code(self) -> None:
        """Test CodeSnippet with empty code string."""
        snippet = CodeSnippet(
            lang="Python3",
            langSlug="python3",
            code=""
        )
        assert snippet.code == ""