from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.mcp import MCPStreamableHttpPlugin
import chainlit as cl
from .cosmos_db_service import CosmosDBService
import random
import logging

# Basic logging configuration
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Initialize CosmosDBService
cosmos_db_service = CosmosDBService()

# Initialize the MCP plugin for Microsoft documentation search
ms_docs_plugin = MCPStreamableHttpPlugin(
    name="Microsoft Documentation Search",
    url="https://learn.microsoft.com/api/mcp",
    timeout=30
)


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

    @kernel_function(name="microsoft_docs_tool", description="Get relevant Microsoft documentation for a given topic.")
    @cl.step(type="tool", name="Microsoft Documentation Search")
    async def microsoft_docs_tool(input: str) -> str:
        """Get relevant Microsoft documentation for a given topic."""
        await ms_docs_plugin.connect()
        result = await ms_docs_plugin.call_tool("microsoft_docs_search", question=input)
        await ms_docs_plugin.close()
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
