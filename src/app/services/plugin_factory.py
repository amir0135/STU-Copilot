import os
from contextlib import asynccontextmanager
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.mcp import MCPStreamableHttpPlugin, TextContent
from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import AzureAIAgent
import chainlit as cl
from .cosmos_db_service import CosmosDBService
import json


# Initialize CosmosDBService
cosmos_db_service = CosmosDBService()

ai_foundry_project_endpoint = os.getenv("AI_FOUNDRY_PROJECT_ENDPOINT")
if not ai_foundry_project_endpoint:
    raise EnvironmentError(
        "AI_FOUNDRY_PROJECT_ENDPOINT environment variable is not set.")

bing_search_agent_id = os.getenv("BING_SEARCH_AGENT_ID")
if not bing_search_agent_id:
    raise EnvironmentError(
        "BING_SEARCH_AGENT_ID environment variable is not set.")


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
            top_count=5)
        return results


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
            response: list[TextContent] = await plugin.call_tool("microsoft_docs_search", question=input)
            # Now process the first item as before
            text = response[0].inner_content.text
            json_data = json.loads(text)
            contents = [item["content"] for item in json_data]
        # <-- context manager closes here, after all items are buffered
        return "----".join(contents)


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
            response = await agent.get_response(messages=[input])
            return response.items


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
