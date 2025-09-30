"""Tests for file naming utilities."""
import pytest
from interview_prep_mcp.file_generator.naming import slugify, suggest_filename


class TestSlugify:
    """Tests for slugify function."""

    def test_simple_title(self):
        """Test basic title with spaces."""
        assert slugify("Two Sum") == "two_sum"

    def test_title_with_number(self):
        """Test title starting with number."""
        assert slugify("3Sum") == "3sum"

    def test_title_with_number_and_spaces(self):
        """Test title with number and spaces."""
        assert slugify("3Sum Closest") == "3sum_closest"

    def test_long_title(self):
        """Test longer title with multiple words."""
        assert slugify("Binary Tree Level Order Traversal II") == "binary_tree_level_order_traversal_ii"

    def test_title_with_special_characters(self):
        """Test title with special characters."""
        assert slugify("Maximum Sum of 3 Non-Overlapping Subarrays") == "maximum_sum_of_3_non_overlapping_subarrays"

    def test_title_with_hyphens(self):
        """Test that hyphens are converted to underscores."""
        assert slugify("Best-Time-To-Buy") == "best_time_to_buy"

    def test_title_with_parentheses(self):
        """Test title with parentheses."""
        assert slugify("Diameter of Binary Tree (Easy)") == "diameter_of_binary_tree_easy"

    def test_title_with_apostrophe(self):
        """Test title with apostrophes."""
        assert slugify("Pascal's Triangle") == "pascals_triangle"

    def test_title_with_multiple_spaces(self):
        """Test that multiple spaces are collapsed."""
        assert slugify("Two  Sum   Problem") == "two_sum_problem"

    def test_title_with_leading_trailing_spaces(self):
        """Test that leading/trailing spaces are removed."""
        assert slugify("  Two Sum  ") == "two_sum"

    def test_title_with_dots(self):
        """Test title with dots."""
        assert slugify("1.5 Sum") == "15_sum"

    def test_title_with_roman_numerals(self):
        """Test title with Roman numerals."""
        assert slugify("Two Sum II") == "two_sum_ii"
        assert slugify("Two Sum III") == "two_sum_iii"

    def test_title_all_uppercase(self):
        """Test that uppercase is converted to lowercase."""
        assert slugify("TWO SUM") == "two_sum"

    def test_title_mixed_case(self):
        """Test mixed case handling."""
        assert slugify("TwoSum") == "twosum"

    def test_empty_string(self):
        """Test empty string."""
        assert slugify("") == ""

    def test_only_special_characters(self):
        """Test string with only special characters."""
        assert slugify("!!!") == ""

    def test_title_with_underscores(self):
        """Test that existing underscores are preserved."""
        assert slugify("two_sum_problem") == "two_sum_problem"


class TestSuggestFilename:
    """Tests for suggest_filename function."""

    def test_python_filename(self):
        """Test Python filename generation."""
        assert suggest_filename("1", "Two Sum", "python3") == "1_two_sum.py"

    def test_java_filename(self):
        """Test Java filename generation."""
        assert suggest_filename("15", "3Sum", "java") == "15_3sum.java"

    def test_go_filename(self):
        """Test Go filename generation."""
        assert suggest_filename("167", "Two Sum II", "golang") == "167_two_sum_ii.go"

    def test_cpp_filename(self):
        """Test C++ filename generation."""
        assert suggest_filename("42", "Trapping Rain Water", "cpp") == "42_trapping_rain_water.cpp"

    def test_javascript_filename(self):
        """Test JavaScript filename generation."""
        assert suggest_filename("1", "Two Sum", "javascript") == "1_two_sum.js"

    def test_typescript_filename(self):
        """Test TypeScript filename generation."""
        assert suggest_filename("1", "Two Sum", "typescript") == "1_two_sum.ts"

    def test_csharp_filename(self):
        """Test C# filename generation."""
        assert suggest_filename("1", "Two Sum", "csharp") == "1_two_sum.cs"

    def test_ruby_filename(self):
        """Test Ruby filename generation."""
        assert suggest_filename("1", "Two Sum", "ruby") == "1_two_sum.rb"

    def test_kotlin_filename(self):
        """Test Kotlin filename generation."""
        assert suggest_filename("1", "Two Sum", "kotlin") == "1_two_sum.kt"

    def test_swift_filename(self):
        """Test Swift filename generation."""
        assert suggest_filename("1", "Two Sum", "swift") == "1_two_sum.swift"

    def test_rust_filename(self):
        """Test Rust filename generation."""
        assert suggest_filename("1", "Two Sum", "rust") == "1_two_sum.rs"

    def test_c_filename(self):
        """Test C filename generation."""
        assert suggest_filename("1", "Two Sum", "c") == "1_two_sum.c"

    def test_unknown_language_defaults_to_txt(self):
        """Test that unknown languages default to .txt."""
        assert suggest_filename("1", "Two Sum", "unknown") == "1_two_sum.txt"

    def test_case_insensitive_language(self):
        """Test that language matching is case-insensitive."""
        assert suggest_filename("1", "Two Sum", "PYTHON3") == "1_two_sum.py"
        assert suggest_filename("1", "Two Sum", "Java") == "1_two_sum.java"

    def test_complex_title(self):
        """Test with complex problem title."""
        result = suggest_filename(
            "1234",
            "Maximum Sum of 3 Non-Overlapping Subarrays",
            "python3"
        )
        assert result == "1234_maximum_sum_of_3_non_overlapping_subarrays.py"

    def test_problem_id_as_string(self):
        """Test that problem_id can be a string."""
        assert suggest_filename("001", "Two Sum", "python3") == "001_two_sum.py"

    def test_scala_filename(self):
        """Test Scala filename generation."""
        assert suggest_filename("1", "Two Sum", "scala") == "1_two_sum.scala"

    def test_php_filename(self):
        """Test PHP filename generation."""
        assert suggest_filename("1", "Two Sum", "php") == "1_two_sum.php"

    def test_sql_filenames(self):
        """Test SQL variant filenames."""
        assert suggest_filename("175", "SQL Query", "mysql") == "175_sql_query.sql"
        assert suggest_filename("175", "SQL Query", "mssql") == "175_sql_query.sql"
        assert suggest_filename("175", "SQL Query", "oraclesql") == "175_sql_query.sql"