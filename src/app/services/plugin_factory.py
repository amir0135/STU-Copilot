import os
from contextlib import asynccontextmanager
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.mcp import MCPStreamableHttpPlugin, TextContent, MCPStdioPlugin
from semantic_kernel.contents import ChatMessageContent
from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import AzureAIAgent
import chainlit as cl
from .cosmos_db_service import cosmos_db_service
import json

# Environment variables for AI Foundry project endpoint and agent IDs
ai_foundry_project_endpoint = os.getenv("AI_FOUNDRY_PROJECT_ENDPOINT")
if not ai_foundry_project_endpoint:
    raise EnvironmentError(
        "AI_FOUNDRY_PROJECT_ENDPOINT environment variable is not set.")

bing_search_agent_id = os.getenv("BING_SEARCH_AGENT_ID")
if not bing_search_agent_id:
    raise EnvironmentError(
        "BING_SEARCH_AGENT_ID environment variable is not set.")

github_docs_search_agent_id = os.getenv("GITHUB_DOCS_SEARCH_AGENT_ID")
if not github_docs_search_agent_id:
    raise EnvironmentError(
        "GITHUB_DOCS_SEARCH_AGENT_ID environment variable is not set.")


class GitHubPlugin:
    """A plugin to search GitHub repositories."""

    @kernel_function(name="github_repository_search",
                     description="Search for relevant GitHub repositories for a given topic.")
    @cl.step(type="tool", name="GitHub Repository Search")
    async def github_repository_search(input: str) -> list:
        """Search for relevant GitHub repositories."""
        results = cosmos_db_service.hybrid_search(
            search_terms=input,
            container_name="github-repos",
            fields=["name", "url", "description",
                    "stars_count", "archived", "updated_at"],
            top_count=10)
        return results

    @kernel_function(name="github_docs_search",
                     description="Search for relevant GitHub documentation for a given topic.")
    @cl.step(type="tool", name="GitHub Documentation Search")
    async def github_docs_search(input: str) -> list:
        """Search for relevant GitHub documentation."""
        async with get_ai_foundry_client() as client:
            agent_definition = await client.agents.get_agent(agent_id=github_docs_search_agent_id)
            agent = AzureAIAgent(client=client, definition=agent_definition)
            structured_message: ChatMessageContent = ChatMessageContent(
                role="user",
                content=input
            )
            response = await agent.get_response(messages=[structured_message])
            return response.items


class MicrosoftDocsPlugin:
    """A plugin to search Microsoft documentation."""

    @kernel_function(name="microsoft_docs_search",
                     description="Search for relevant Microsoft documentation for a given topic.")
    @cl.step(type="tool", name="Microsoft Documentation Search")
    async def microsoft_docs_search(input: str) -> str:
        """Search for relevant Microsoft documentation."""

        async with MCPStreamableHttpPlugin(
            name="Microsoft Documentation Search",
            url="https://learn.microsoft.com/api/mcp",
            request_timeout=15
        ) as plugin:
            response: list[TextContent] = await plugin.call_tool(
                "microsoft_docs_search",
                query=input)
            results = response[0].inner_content.text if response else ""
            if not isinstance(results, str) or not results:
                return "Could not retrieve results from Microsoft Docs MCP Server."

            # Parse the JSON response
            data = json.loads(results)

            aggregated = {}

            for item in data:
                title = item["title"]
                content = item["content"]
                heading = f"# {title}\n"
                # Remove the heading from the content if it exists
                if content.startswith(heading):
                    content = content[len(heading):]
                if title in aggregated:
                    aggregated[title].append(content)
                else:
                    aggregated[title] = [content]

            aggregated_results = [
                {"title": title, "content": "\n\n".join(contents)}
                for title, contents in aggregated.items()
            ]

        return json.dumps(aggregated_results, indent=2, ensure_ascii=False)


class BlogPostsPlugin:
    """A plugin to search blog posts."""

    @kernel_function(name="blog_posts_search",
                     description="Search for relevant blog posts for a given topic.")
    @cl.step(type="tool", name="Blog Posts Search")
    async def blog_posts_search(input: str) -> list:
        """Search for relevant blog posts."""
        results = cosmos_db_service.hybrid_search(
            search_terms=input,
            container_name="blog-posts",
            fields=["title", "description", "published_date", "url"],
            top_count=5)
        return results


class SeismicPlugin:
    """A plugin to search seismic data."""

    @kernel_function(name="seismic_search",
                     description="Search for relevant Seismic data for a given topic.")
    @cl.step(type="tool", name="Seismic Data Search")
    async def seismic_search(input: str) -> list:
        """Search for relevant Seismic data."""
        results = cosmos_db_service.hybrid_search(
            search_terms=input,
            container_name="seismic-contents",
            fields=["name", "url", "description", "last_update", "expiration_date",
                    "level", "solution_area", "format", "size", "confidentiality"],
            top_count=10)
        return results


class BingPlugin:
    """A plugin to perform Bing searches."""

    @kernel_function(name="bing_search", description="Search Bing for a given query.")
    @cl.step(type="tool", name="Bing Search")
    async def bing_search(input: str) -> list:
        """Perform a Bing search."""
        async with get_ai_foundry_client() as client:
            agent_definition = await client.agents.get_agent(agent_id=bing_search_agent_id)
            agent = AzureAIAgent(client=client, definition=agent_definition)
            structured_message: ChatMessageContent = ChatMessageContent(
                role="user",
                content=input
            )
            response = await agent.get_response(messages=[structured_message])
            return response.items


class AWSDocsPlugin:
    """A plugin to search AWS documentation."""

    @kernel_function(name="aws_docs_search",
                     description="Search for relevant AWS documentation for a given topic.")
    @cl.step(type="tool", name="AWS Documentation Search")
    async def aws_docs_search(input: str) -> str:
        """Search for relevant AWS documentation."""
        async with MCPStdioPlugin(
            name="AWS Docs",
            description="AWS Docs Search",
            command="docker",
            args=[
                "run",
                "--rm",
                "--interactive",
                "--env",
                "FASTMCP_LOG_LEVEL=ERROR",
                "--env",
                "AWS_DOCUMENTATION_PARTITION=aws",
                "mcp/aws-documentation:latest"
            ],
            env={},
            request_timeout=30

        ) as aws_docs_plugin:
            contents = []
            response: list[TextContent] = await aws_docs_plugin.call_tool(
                tool_name="search_documentation",
                search_phrase=input,
                limit=5)
            for item in response:
                if isinstance(item, TextContent):
                    data = json.loads(item.text)
                    contents.append({
                        "url": data["url"],
                        "title": data["title"],
                        "context": data["context"]
                    })
                else:
                    contents.append({
                        "url": "",
                        "title": "Invalid content type received from AWS Docs plugin.",
                        "context": ""
                    })
        # <-- context manager closes here, after all items are buffered
        return json.dumps(contents, indent=2)


@asynccontextmanager
async def get_ai_foundry_client():
    async with (
        DefaultAzureCredential() as creds,
        AzureAIAgent.create_client(
            credential=creds,
            endpoint=ai_foundry_project_endpoint,
        ) as client
    ):
        yield client

# Global instances
github_plugin = GitHubPlugin()
microsoft_docs_plugin = MicrosoftDocsPlugin()
blog_posts_plugin = BlogPostsPlugin()
seismic_plugin = SeismicPlugin()
bing_plugin = BingPlugin()
aws_docs_plugin = AWSDocsPlugin()
