"""Utilities for generating consistent file names."""
import re


def slugify(title: str) -> str:
    """
    Convert problem title to snake_case.

    Examples:
        "Two Sum" -> "two_sum"
        "3Sum" -> "3sum"
        "Binary Tree Level Order Traversal II" -> "binary_tree_level_order_traversal_ii"

    Args:
        title: Problem title

    Returns:
        Slugified title in snake_case
    """
    # Convert to lowercase
    slug = title.lower()

    # Replace spaces and hyphens with underscores
    slug = re.sub(r'[\s\-]+', '_', slug)

    # Remove any non-alphanumeric characters except underscores
    slug = re.sub(r'[^a-z0-9_]', '', slug)

    # Remove leading/trailing underscores
    slug = slug.strip('_')

    # Collapse multiple underscores
    slug = re.sub(r'_+', '_', slug)

    return slug


def suggest_filename(problem_id: str, title: str, language: str) -> str:
    """
    Suggest a filename based on problem and language.

    Examples:
        (1, "Two Sum", "python3") -> "1_two_sum.py"
        (15, "3Sum", "java") -> "15_3sum.java"
        (167, "Two Sum II", "golang") -> "167_two_sum_ii.go"

    Args:
        problem_id: Problem ID
        title: Problem title
        language: Language slug (e.g., "python3", "java", "golang")

    Returns:
        Suggested filename with extension
    """
    slug = slugify(title)

    # Map common language slugs to file extensions
    extension_map = {
        "python3": "py",
        "python": "py",
        "java": "java",
        "golang": "go",
        "cpp": "cpp",
        "c": "c",
        "csharp": "cs",
        "javascript": "js",
        "typescript": "ts",
        "ruby": "rb",
        "swift": "swift",
        "kotlin": "kt",
        "rust": "rs",
        "scala": "scala",
        "php": "php",
        "mysql": "sql",
        "mssql": "sql",
        "oraclesql": "sql",
        "elixir": "ex",
        "racket": "rkt",
    }

    ext = extension_map.get(language.lower(), "txt")
    return f"{problem_id}_{slug}.{ext}"