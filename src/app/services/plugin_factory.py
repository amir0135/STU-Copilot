import os
from contextlib import asynccontextmanager
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.mcp import MCPStreamableHttpPlugin
from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import AzureAIAgent
import chainlit as cl
from .cosmos_db_service import CosmosDBService
import random
import logging

# Basic logging configuration
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

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


class PluginFactory:
    """A plugin to ask questions and get answers."""

    def __init__(self) -> None:
        pass

    @kernel_function(name="github_tool", description="Get relevant GitHub repositories for a given topic.")
    @cl.step(type="tool", name="GitHub Repository Search")
    async def github_tool(input: str) -> list:
        """Get relevant GitHub repositories for a given topic."""

        results = cosmos_db_service.hybrid_search(
            search_terms=input,
            container_name="github-repos",
            fields=["name", "url", "description",
                    "stars_count", "archived", "updated_at"],
            top_count=5)
        return results

    @kernel_function(name="microsoft_docs_tool", description="Get relevant Microsoft documentation for a given topic.", )
    @cl.step(type="tool", name="Microsoft Documentation Search")
    async def microsoft_docs_tool(input: str) -> str:
        """Get relevant Microsoft documentation for a given topic."""

        async with MCPStreamableHttpPlugin(
            name="Microsoft Documentation Search",
            url="https://learn.microsoft.com/api/mcp",
            request_timeout=30
        ) as plugin:
            result = await plugin.call_tool("microsoft_docs_search", question=input)
            return result

    @kernel_function(name="blog_posts_tool", description="Get relevant blog posts for a given topic.")
    @cl.step(type="tool", name="Blog Posts Search")
    async def blog_posts_tool(input: str) -> list:
        """Get relevant blog posts for a given topic."""

        results = cosmos_db_service.hybrid_search(
            search_terms=input,
            container_name="blog-posts",
            fields=["title", "description", "published_date", "url"],
            top_count=5)
        return results

    @kernel_function(name="price_generator_tool", description="Generate random prices")
    @cl.step(type="tool", name="Random Price Generator")
    async def price_generator_tool(input: str) -> str:
        """Generate random prices."""
        return f"Random price for {input}: ${round(random.uniform(10, 100), 2)}"

    @kernel_function(name="seismic_tool", description="Get seismic data for a given location.")
    @cl.step(type="tool", name="Seismic Data Search")
    async def seismic_tool(input: str) -> list:
        """Get seismic data for a given location."""
        results = cosmos_db_service.hybrid_search(
            search_terms=input,
            container_name="seismic-contents",
            fields=["name", "url", "description", "publish_date", "level",
                    "solution_area", "audience", "format", "size", "confidentiality"],
            top_count=10)
        return results

    @kernel_function(name="bing_search_tool", description="Perform a Bing search using the Bing Search agent.")
    @cl.step(type="tool", name="Bing Search")
    async def bing_search_tool(input: str) -> list:
        """Get Bing search results for a given query."""

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
