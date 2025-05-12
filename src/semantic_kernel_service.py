import os
from openai import AsyncOpenAI
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAITextEmbedding,
    OpenAIChatPromptExecutionSettings)
from semantic_kernel.connectors.search_engine import BingConnector
from semantic_kernel.connectors.ai import FunctionChoiceBehavior


def create_kernel() -> Kernel:
    """Create a kernel with Azure OpenAI service and add services.

    Returns:
        Kernel: The created kernel instance with added services."""

    # Create a kernel with Azure OpenAI service.
    client = AsyncOpenAI(api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                         base_url=os.getenv("AZURE_OPENAI_ENDPOINT"))

    # Create a kernel instance
    kernel = Kernel()

    # Add chat completion service
    kernel.add_service(OpenAIChatCompletion(
        ai_model_id="gpt-4o-mini",
        async_client=client,
        service_id="gpt-4o-mini"
    ))

    # Add Embedding service
    kernel.add_service(OpenAITextEmbedding(
        ai_model_id="text-embedding-3-small",
        async_client=client,
        service_id="embedding-small"
    ))

    # Add web search skill
    # bing_api_key = os.getenv("BING_SEARCH_API_KEY")
    # if bing_api_key:
    #     web_search = BingConnector(api_key=bing_api_key)
    #     kernel.import_skill(web_search, skill_name="web-search")

    return kernel


def request_settings() -> any:
    """Create request settings for the OpenAI service.

    Returns:
        dict: The request settings for the OpenAI service.
    """

    request_settings = OpenAIChatPromptExecutionSettings(
        function_choice_behavior=FunctionChoiceBehavior.Auto(
            filters={"excluded_plugins": ["ChatBot"]}))

    return request_settings
