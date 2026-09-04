import asyncio
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()


async def main():
    required_vars = [
        "GOOGLE_API_KEY",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "GITHUB_USERNAME",
        "GITHUB_REPO",
    ]

    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        raise RuntimeError(
            f"Missing environment variables: {', '.join(missing)}"
        )

    print("Starting Gemini + GitHub MCP test...")
    print()

    model = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite-preview",
        temperature=0,
    )

    client = MultiServerMCPClient(
        {
            "github": {
                "transport": "stdio",
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-github",
                ],
                "env": {
                    "GITHUB_PERSONAL_ACCESS_TOKEN": os.environ[
                        "GITHUB_PERSONAL_ACCESS_TOKEN"
                    ]
                },
            }
        }
    )

    print("Connecting to GitHub MCP...")

    tools = await client.get_tools()

    print("GitHub MCP connection successful!")
    print(f"Available GitHub tools: {len(tools)}")
    print()

    print("Available tools:")
    for tool in tools:
        print(f"  - {tool.name}")

    print()
    print("Testing Gemini...")

    response = await model.ainvoke(
        "Reply with exactly: AI DevOps MCP connection successful"
    )

    print()
    print("Gemini response:")
    print(response.content)

    print()
    print("========================================")
    print("AI DevOps MCP TEST PASSED")
    print("========================================")


if __name__ == "__main__":
    asyncio.run(main())
