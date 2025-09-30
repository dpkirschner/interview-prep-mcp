# LeetCode MCP Server - Implementation Plan

## Overview
This document outlines an iterative approach to building an MCP server for LeetCode practice. The server will provide tools to load problems and create practice files with consistent formatting.

## Phase 1: Basic Setup & Validation

### Step 1: Initialize Python project
- Create `pyproject.toml` with MCP SDK and basic dependencies
- Set up project structure (src/interview_prep_mcp/)
- Create minimal `server.py` with MCP server boilerplate

### Step 2: Test MCP server works
- Implement a simple "hello world" tool to verify MCP setup
- Test connection with Claude Desktop or MCP inspector

## Phase 2: LeetCode API Integration

### Step 3: Research & test LeetCode GraphQL API
- Write standalone script to query LeetCode GraphQL endpoint
- Test fetching a problem by ID (e.g., problem #1 - Two Sum)
- Document the API response structure

### Step 4: Build basic LeetCode client
- Create `leetcode/client.py` with a function to fetch problem by ID
- Add error handling for invalid IDs, network errors
- Create data models for problem data (using dataclasses or Pydantic)

## Phase 3: First MCP Tool

### Step 5: Implement `load_problem` tool
- Create tool that accepts `problem_id` parameter
- Return formatted problem information (title, difficulty, description)
- Test with several different problems

### Step 6: Add problem search by name
- Extend client to search problems by title/keywords
- Update `load_problem` to accept `problem_name` parameter
- Handle multiple matches gracefully

## Phase 4: File Generation

### Step 7: Build template generator for Python
- Create `file_generator/template.py`
- Generate file with problem description as docstring
- Include starter code from LeetCode
- Add basic test case structure

### Step 8: Implement naming schema
- Create `file_generator/naming.py` for consistent naming
- Handle slug generation (problem title → snake_case)
- Format: `{problem_id}_{slug}.py`

### Step 9: Implement `create_problem_file` tool
- Accept `problem_id`, `output_path` parameters
- Generate and write file to specified location
- Return confirmation with file path

## Phase 5: Enhancement & Polish

### Step 10: Add test case parsing
- Extract example inputs/outputs from problem description
- Generate test cases automatically when possible
- Format as runnable assertions

### Step 11: Add multi-language support (optional)
- Add `language` parameter to tools
- Create templates for JavaScript, Java, C++, etc.
- Handle language-specific file extensions and syntax

### Step 12: Error handling & validation
- Validate paths before writing files
- Handle rate limiting from LeetCode API
- Add helpful error messages

## Phase 6: Testing & Documentation

### Step 13: Test with real usage
- Try loading various problems (easy, medium, hard)
- Test edge cases (special characters, long descriptions)
- Verify files are correctly formatted

### Step 14: Write documentation
- README with installation instructions
- Usage examples for both tools
- Configuration options

## Implementation Notes

### Project Structure
```
interview-prep-mcp/
├── pyproject.toml
├── README.md
├── plans/
│   └── original.md
└── src/
    └── interview_prep_mcp/
        ├── __init__.py
        ├── server.py
        ├── leetcode/
        │   ├── __init__.py
        │   ├── client.py
        │   ├── parser.py
        │   └── types.py
        ├── file_generator/
        │   ├── __init__.py
        │   ├── template.py
        │   └── naming.py
        └── tools/
            ├── __init__.py
            ├── load_problem.py
            └── create_file.py
```

### Dependencies
- `mcp`: MCP Python SDK
- `httpx` or `requests`: HTTP requests
- `pydantic`: Data validation
- `beautifulsoup4`: HTML parsing
- `python-slugify`: URL-friendly slugs

### File Template Example
```python
"""
[Problem ID]. [Problem Title]
Difficulty: [Easy/Medium/Hard]

[Problem Description]

Example 1:
Input: [...]
Output: [...]

Constraints:
[...]
"""

# Starter code from LeetCode
class Solution:
    def methodName(self, params):
        pass

# Test cases
def test_solution():
    solution = Solution()
    assert solution.methodName(...) == expected
    # More test cases...

if __name__ == "__main__":
    test_solution()
    print("All tests passed!")
```

### Naming Schema
- Format: `{problem_number}_{problem_slug}.{ext}`
- Examples:
  - `1_two_sum.py`
  - `42_trapping_rain_water.py`
  - `200_number_of_islands.java`

## Success Criteria
- MCP server successfully connects to Claude Desktop
- Can load any LeetCode problem by ID or search by name
- Generates properly formatted practice files
- Files include problem description, starter code, and test cases
- Consistent naming across all generated files