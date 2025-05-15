import os
from openai import AsyncOpenAI
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from utils import load_prompt


class AgentFactory:
    """Factory for creating chat completion agents."""

    def __init__(self):
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if not api_key or not endpoint:
            raise EnvironmentError("Missing Azure OpenAI API key or endpoint.")
        self.base_kernel = Kernel()
        self.base_client = AsyncOpenAI(api_key=api_key, base_url=endpoint)

    def create_agent(self,
                     agent_name: str,
                     model_name: str,
                     instructions: str = None
                     ) -> ChatCompletionAgent:
        """Create a chat completion agent."""
        kernel = self.base_kernel.clone()
        kernel.add_service(
            OpenAIChatCompletion(
                ai_model_id=model_name,
                async_client=self.base_client,
                service_id=agent_name,
            )
        )
        return ChatCompletionAgent(
            kernel=kernel,
            name=agent_name,
            instructions=instructions or load_prompt(agent_name),
        )

    @staticmethod
    def request_settings() -> OpenAIChatPromptExecutionSettings:
        """Create request settings for the OpenAI service."""
        return OpenAIChatPromptExecutionSettings(
            function_choice_behavior=FunctionChoiceBehavior.Auto(
                filters={"excluded_plugins": ["ChatBot"]}
            )
        )
