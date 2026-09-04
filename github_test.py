import asyncio
import os

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()


async def main():
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

    tools = await client.get_tools()

    print(f"Loaded {len(tools)} GitHub tools\n")

    for tool in tools:
        print(f"{tool.name}: {tool.description[:100]}")

    print("\nTesting GitHub repository search...")

    search_tool = next(
        tool for tool in tools
        if tool.name == "search_repositories"
    )

    result = await search_tool.ainvoke(
        {
            "query": "ai-cicd-agent",
        }
    )

    print("\nGitHub MCP result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
