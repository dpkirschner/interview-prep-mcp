# Interview Prep MCP

A Model Context Protocol (MCP) server for LeetCode practice problem management. This server provides tools to fetch LeetCode problems with their descriptions, code templates, test cases, and metadata.

## Features

- 🔍 **Flexible Problem Lookup**: Search by title slug, problem ID, or problem name
- 💻 **Multi-Language Support**: Get code templates for Python, Java, C++, Go, JavaScript, and more
- 🔄 **Smart Caching**: Efficient problem ID lookup with automatic caching
- 🛡️ **Retry Logic**: Automatic retry with exponential backoff for transient failures
- ⚡ **Rate Limiting**: Respectful 10 req/sec rate limiting for LeetCode API
- 🎯 **Search Results**: Find problems by keywords with ranked results

## Installation

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager

### Install from source

```bash
# Clone the repository
git clone <repository-url>
cd interview-prep-mcp

# Install dependencies
pip install -e .

# Or using uv
uv pip install -e .
```

## Usage

### As an MCP Server

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "interview-prep": {
      "command": "python",
      "args": ["-m", "interview_prep_mcp.server"]
    }
  }
}
```

Or using uv:

```json
{
  "mcpServers": {
    "interview-prep": {
      "command": "uv",
      "args": ["run", "interview-prep-mcp"]
    }
  }
}
```

### Available Tools

#### `load_problem`

Load a LeetCode problem by title slug, problem ID, or search by name.

**Parameters:**
- `title_slug` (string, optional): URL-friendly problem slug (e.g., "two-sum")
- `problem_id` (integer, optional): Problem ID number (e.g., 1)
- `problem_name` (string, optional): Search query for problem name (e.g., "two sum")
- `language` (string, optional): Specific language for code snippet (e.g., "python", "java", "golang")

**Examples:**

```python
# Load by title slug
load_problem(title_slug="two-sum")

# Load by problem ID
load_problem(problem_id=1)

# Search by name
load_problem(problem_name="binary tree")

# Get specific language code
load_problem(title_slug="two-sum", language="python")
load_problem(problem_id=1, language="golang")
```

**Returns:**

Single problem:
```json
{
  "problem_id": "1",
  "title": "Two Sum",
  "title_slug": "two-sum",
  "difficulty": "Easy",
  "description": "Given an array of integers nums...",
  "topics": ["Array", "Hash Table"],
  "hints": ["A hint for solving..."],
  "example_test_cases": "[2,7,11,15]\n9",
  "code_snippets": {
    "python3": "class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        pass",
    "java": "class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        \n    }\n}",
    "cpp": "class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        \n    }\n};"
  }
}
```

With language filter:
```json
{
  "problem_id": "1",
  "title": "Two Sum",
  "title_slug": "two-sum",
  "difficulty": "Easy",
  "description": "Given an array of integers nums...",
  "topics": ["Array", "Hash Table"],
  "hints": ["A hint for solving..."],
  "example_test_cases": "[2,7,11,15]\n9",
  "language": "python3",
  "code": "class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        pass",
  "suggested_filename": "1_two_sum.py"
}
```

Multiple search results:
```json
{
  "query": "binary tree",
  "matches": [
    {
      "problem_id": "94",
      "title": "Binary Tree Inorder Traversal",
      "title_slug": "binary-tree-inorder-traversal",
      "difficulty": "Easy"
    },
    {
      "problem_id": "102",
      "title": "Binary Tree Level Order Traversal",
      "title_slug": "binary-tree-level-order-traversal",
      "difficulty": "Medium"
    }
  ],
  "count": 2,
  "message": "Found 2 problems matching 'binary tree'. Use title_slug to load a specific problem."
}
```

## Supported Languages

The server supports code templates for the following languages:

- Python (`python`, `python3`)
- Java (`java`)
- C++ (`cpp`, `c++`)
- C (`c`)
- C# (`csharp`, `c#`, `cs`)
- JavaScript (`javascript`, `js`)
- TypeScript (`typescript`, `ts`)
- Go (`golang`, `go`)
- Rust (`rust`, `rs`)
- Swift (`swift`)
- Kotlin (`kotlin`, `kt`)
- Ruby (`ruby`, `rb`)
- Scala (`scala`)
- PHP (`php`)
- Elixir (`elixir`)
- Racket (`racket`)
- SQL (`mysql`, `mssql`, `oraclesql`)

## Architecture

### Components

- **LeetCodeClient**: Handles all API interactions with LeetCode's GraphQL API
  - Automatic retry with exponential backoff (3 attempts)
  - Rate limiting at 10 requests/second
  - Caching for efficient problem ID lookups
  - Fallback to REST API when GraphQL fails

- **LoadProblemTool**: High-level interface for problem loading
  - Multi-method problem lookup (slug, ID, name)
  - Language filtering and code snippet extraction
  - Search result formatting

- **FileGenerator**: Utilities for filename generation
  - Consistent naming scheme: `{problem_id}_{slug}.{ext}`
  - Language-aware file extensions

### Error Handling

The server implements robust error handling:

- **Retryable Errors**: Network errors, timeouts, and HTTP status errors automatically retry with exponential backoff (1s → 2s → 4s)
- **Non-Retryable Errors**: GraphQL errors and validation errors fail immediately
- **Rate Limiting**: Requests are automatically throttled to respect API limits

### Caching Strategy

- **Problem ID Cache**: All problem IDs and slugs are cached on first use
- **Cache Initialization**: Can be preloaded at server startup to hide latency
- **Cache Lifetime**: Persists for the lifetime of the server process

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest -m "not integration"

# Run with coverage
pytest --cov=src/interview_prep_mcp

# Run specific test file
pytest tests/leetcode/test_client.py -xvs
```

### Code Quality

```bash
# Format code
black src tests

# Lint code
ruff check src tests

# Type checking
mypy src
```

### Project Structure

```
interview-prep-mcp/
├── src/
│   └── interview_prep_mcp/
│       ├── __init__.py
│       ├── server.py              # MCP server implementation
│       ├── leetcode/
│       │   ├── __init__.py
│       │   ├── client.py          # LeetCode API client
│       │   ├── types.py           # Pydantic models
│       │   └── search.py          # Search utilities
│       ├── file_generator/
│       │   ├── __init__.py
│       │   └── naming.py          # Filename generation
│       └── tools/
│           ├── __init__.py
│           └── load_problem.py    # Tool implementation
├── tests/
│   ├── leetcode/                  # Client tests
│   ├── tools/                     # Tool tests
│   └── file_generator/            # Generator tests
├── pyproject.toml
└── README.md
```

## Dependencies

- **mcp**: Model Context Protocol SDK
- **httpx**: Modern HTTP client for async requests
- **pydantic**: Data validation and serialization
- **beautifulsoup4**: HTML parsing for problem descriptions
- **python-slugify**: URL-friendly slug generation
- **tenacity**: Retry logic with exponential backoff
- **aiolimiter**: Async rate limiting

## License

[Add your license here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Troubleshooting

### Server won't start
- Ensure Python 3.10+ is installed
- Check that all dependencies are installed: `pip install -e .`
- Verify the server runs: `python -m interview_prep_mcp.server`

### Rate limiting errors
- The server automatically limits to 10 req/sec
- If you see rate limit errors from LeetCode, the built-in limiter should prevent this
- Consider adding delays between large batches of requests

### Problem not found
- Verify the problem exists on LeetCode
- Check the title slug matches the URL (e.g., "two-sum" not "Two Sum")
- Try searching by name instead: `load_problem(problem_name="two sum")`

### Timeout errors
- The server automatically retries with exponential backoff
- If timeouts persist, check your network connection
- LeetCode API may be experiencing issues
