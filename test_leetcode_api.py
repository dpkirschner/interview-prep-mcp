"""
Standalone script to test LeetCode GraphQL API
"""
import asyncio
import httpx


LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql/"


async def fetch_problem_by_slug(title_slug: str) -> dict:
    """Fetch a problem from LeetCode by its title slug."""

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
            LEETCODE_GRAPHQL_URL,
            json={"query": query, "variables": variables},
            headers={
                "Content-Type": "application/json",
                "Referer": "https://leetcode.com",
            },
        )
        response.raise_for_status()
        return response.json()


async def main():
    """Test fetching a problem."""
    # Test with Two Sum (problem #1)
    result = await fetch_problem_by_slug("two-sum")

    print("Response structure:")
    print(f"Keys: {result.keys()}")

    if "data" in result and result["data"]:
        question = result["data"]["question"]
        print(f"\n=== Problem #{question['questionFrontendId']}: {question['title']} ===")
        print(f"Difficulty: {question['difficulty']}")
        print(f"Title Slug: {question['titleSlug']}")
        print(f"\nTopics: {', '.join(tag['name'] for tag in question['topicTags'])}")
        print(f"\nAvailable languages: {', '.join(snippet['lang'] for snippet in question['codeSnippets'])}")
        print(f"\nDescription preview (first 200 chars):")
        print(question['content'][:200] + "...")

        # Print Python starter code if available
        for snippet in question['codeSnippets']:
            if snippet['langSlug'] == 'python3':
                print(f"\nPython3 starter code:")
                print(snippet['code'])
                break
    elif "errors" in result:
        print(f"\nError: {result['errors']}")
    else:
        print("\nUnexpected response format")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())