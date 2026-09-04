import asyncio
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent


load_dotenv("/root/ai-devops-agent/.env")


async def main():
    required_vars = [
        "GOOGLE_API_KEY",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "GITHUB_USERNAME",
        "GITHUB_REPO",
    ]

    missing = [v for v in required_vars if not os.getenv(v)]

    if missing:
        raise RuntimeError(
            f"Missing environment variables: {', '.join(missing)}"
        )

    owner = os.environ["GITHUB_USERNAME"]
    repo = os.environ["GITHUB_REPO"]
    branch = "ai-cicd-agent-setup"

    print("========================================")
    print("AI DOCKER BUILD AUTOMATION AGENT")
    print("========================================")
    print(f"Repository: {owner}/{repo}")
    print(f"Branch: {branch}")
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

    print("Loading GitHub MCP tools...")
    all_tools = await client.get_tools()

    allowed_names = {
        "get_file_contents",
        "create_or_update_file",
    }

    tools = [
        tool for tool in all_tools
        if tool.name in allowed_names
    ]

    print("Allowed tools:")
    for tool in tools:
        print(f"  - {tool.name}")

    print()

    system_prompt = f"""
You are an AI DevOps Docker automation agent.

Repository:
{owner}/{repo}

Existing feature branch:
{branch}

You may use ONLY:
- get_file_contents
- create_or_update_file

Rules:
1. Never modify main.
2. Never create another branch.
3. Never create or merge a pull request.
4. Work only on {branch}.
5. Inspect existing files before updating them.
6. Modify only Dockerfile and .github/workflows/ci.yml.
7. Do not expose secrets or credentials.
8. Preserve the existing CI workflow unless a change is required for Docker building.
"""

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
    )

    task = f"""
Enhance the CI/CD setup in:

{owner}/{repo}

Use the existing branch:
{branch}

Do NOT create another branch.
Do NOT create or merge a pull request.
Do NOT modify main.

The repository currently contains:
- README.md
- .github/workflows/ci.yml

Perform these changes:

1. Create a Dockerfile at the repository root.

The repository currently has no application source code, so create a simple,
valid Docker image that packages README.md.

Use a small Python base image.

The Dockerfile should:
- use python:3.11-slim
- set WORKDIR to /app
- copy README.md into /app
- have a valid CMD that displays README.md

2. Update:
.github/workflows/ci.yml

Keep the existing CI behavior.

Add a Docker build step that runs:

docker build -t ai-cicd-agent:ci .

The workflow must remain valid GitHub Actions YAML.

Use only the existing branch:
{branch}

Create the required commits using GitHub MCP.

Do not modify any other files.

Report:
1. Dockerfile created
2. CI workflow updated
3. Commit message(s)
4. Commit SHA(s)
5. Branch used
"""

    print("Sending Docker automation task...")
    print()

    try:
        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": task,
                    }
                ]
            }
        )

        print("========================================")
        print("AI AGENT RESPONSE")
        print("========================================")

        messages = result.get("messages", [])

        if messages:
            final_message = messages[-1]
            print(
                final_message.content
                if hasattr(final_message, "content")
                else final_message
            )
        else:
            print(result)

        print()
        print("========================================")
        print("DOCKER AUTOMATION COMPLETE")
        print("========================================")

    except Exception as e:
        print()
        print("========================================")
        print("AI AGENT ERROR")
        print("========================================")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error: {e}")
        print("========================================")
        raise


if __name__ == "__main__":
    asyncio.run(main())
