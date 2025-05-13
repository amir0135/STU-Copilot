import os
from openai import AsyncOpenAI
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.search_engine import BingConnector
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAIChatPromptExecutionSettings)
from semantic_kernel.connectors.search_engine import BingConnector
from utils import load_prompt
from enum import Enum


class AgentType(str, Enum):
    communicator_agent = "communicator_agent"
    questioner_agent = "questioner_agent"
    github_agent = "github_agent"
    industry_agent = "industry_agent"
    architect_agent = "architect_agent"
    price_calculator_agent = "price_calculator_agent"



def create_agent(agent_name: AgentType, model_name: str) -> ChatCompletionAgent:
    """
    Create an agent for the kernel.

    Args:
        agent_name (str): The name of the agent.
        model_name (str): The model name for the agent.

    Returns:
        ChatCompletionAgent: The created agent.
    """

    # Create a kernel instance
    # Create a kernel with Azure OpenAI service.
    client = AsyncOpenAI(api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                         base_url=os.getenv("AZURE_OPENAI_ENDPOINT"))

    # Create a kernel instance
    kernel = Kernel()

    # Add chat completion service
    kernel.add_service(OpenAIChatCompletion(
        ai_model_id=model_name,
        async_client=client,
        service_id=agent_name
    ))

    # Create the agent
    agent = ChatCompletionAgent(
        kernel=kernel,
        name=agent_name,
        instructions=load_prompt(agent_name)
    )   
 
    return agent


def request_settings() -> any:
    """Create request settings for the OpenAI service.

    Returns:
        dict: The request settings for the OpenAI service.
    """

    request_settings = OpenAIChatPromptExecutionSettings(
        function_choice_behavior=FunctionChoiceBehavior.Auto(
            filters={"excluded_plugins": ["ChatBot"]}))

    return request_settings
