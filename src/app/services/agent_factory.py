import os
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from .cache_service import load_prompt
from .plugin_factory import PluginFactory
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory for creating chat completion agents."""

    def __init__(self):
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AI_FOUNDRY_KEY")
        if not endpoint or not api_key:
            raise EnvironmentError(
                "Missing Azure Open AI endpoint or API key.")
        self.plugin_factory = PluginFactory()

    def create_kernel(self,
                      agent_name: str,
                      model_name: str,
                      api_version: str = "2024-12-01-preview") -> Kernel:
        """Create a kernel with the desired model."""
        kernel = Kernel()
        kernel.add_service(
            AzureChatCompletion(
                deployment_name=model_name,
                service_id=agent_name,
                api_version=api_version)
        )

        return kernel

    def get_orchestrator_agent(self) -> ChatCompletionAgent:
        """Create an orchestrator agent with the necessary plugins."""
        agent_name = "orchestrator_agent"
        model_name = "gpt-4.1"

        # Create a new kernel instance with the OpenAI service
        kernel = self.create_kernel(
            agent_name=agent_name,
            model_name=model_name
        )

        # Create the agent
        orchestrator_agent = ChatCompletionAgent(
            kernel=kernel,
            name=agent_name,
            instructions=load_prompt(agent_name),
            plugins=[
                self.get_github_agent(),
                self.plugin_factory.microsoft_docs_tool
            ]
        )

        return orchestrator_agent

    def get_questioner_agent(self) -> ChatCompletionAgent:
        """Create a questioner agent with the necessary plugins."""
        agent_name = "questioner_agent"
        model_name = "gpt-4.1-mini"

        # Clone the base kernel and add the OpenAI service
        kernel = self.create_kernel(
            agent_name=agent_name,
            model_name=model_name
        )

        # Create the agent
        questioner_agent = ChatCompletionAgent(
            kernel=kernel,
            name=agent_name,
            instructions=load_prompt(agent_name)
        )

        return questioner_agent

    def get_planner_agent(self) -> ChatCompletionAgent:
        """Create a planner agent with the necessary plugins."""
        agent_name = "planner_agent"
        model_name = "o3-mini"

        # Clone the base kernel and add the OpenAI service
        kernel = self.create_kernel(
            agent_name=agent_name,
            model_name=model_name
        )

        # Create the agent
        planner_agent = ChatCompletionAgent(
            kernel=kernel,
            name=agent_name,
            instructions=load_prompt(agent_name)
        )

        return planner_agent

    def get_github_agent(self) -> ChatCompletionAgent:
        """Create a GitHub agent with the necessary plugins."""
        agent_name = "github_agent"
        model_name = "gpt-4.1-nano"

        # Clone the base kernel and add the OpenAI service
        kernel = self.create_kernel(
            agent_name=agent_name,
            model_name=model_name
        )

        # Create the agent
        github_agent = ChatCompletionAgent(
            kernel=kernel,
            name=agent_name,
            instructions=load_prompt(agent_name),
            plugins=[
                self.plugin_factory.github_tool
            ]
        )

        return github_agent

    def get_microsoft_docs_agent(self) -> ChatCompletionAgent:
        """Create a Microsoft Docs agent with the necessary plugins."""
        agent_name = "microsoft_docs_agent"
        model_name = "gpt-4.1-mini"

        # Clone the base kernel and add the OpenAI service
        kernel = self.create_kernel(
            agent_name=agent_name,
            model_name=model_name
        )
        kernel.add_plugins([
            self.plugin_factory.microsoft_docs_tool
        ])

        # Create the agent
        microsoft_docs_agent = ChatCompletionAgent(
            kernel=kernel,
            name=agent_name,
            instructions=load_prompt(agent_name),
        )

        return microsoft_docs_agent

    def get_blog_posts_agent(self) -> ChatCompletionAgent:
        """Create a Blog Posts agent with the necessary plugins."""
        agent_name = "blog_posts_agent"
        model_name = "gpt-4.1-nano"

        # Clone the base kernel and add the OpenAI service
        kernel = self.create_kernel(
            agent_name=agent_name,
            model_name=model_name
        )

        # Create the agent
        blog_posts_agent = ChatCompletionAgent(
            kernel=kernel,
            name=agent_name,
            instructions=load_prompt(agent_name),
            plugins=[
                self.plugin_factory.blog_posts_tool
            ]
        )

        return blog_posts_agent
    
    def get_seismic_agent(self) -> ChatCompletionAgent:
        """Create a Seismic agent with the necessary plugins."""
        agent_name = "seismic_agent"
        model_name = "gpt-4.1-nano"

        # Clone the base kernel and add the OpenAI service
        kernel = self.create_kernel(
            agent_name=agent_name,
            model_name=model_name
        )

        # Create the agent
        seismic_agent = ChatCompletionAgent(
            kernel=kernel,
            name=agent_name,
            instructions=load_prompt(agent_name),
            plugins=[
                self.plugin_factory.seismic_tool
            ]
        )

        return seismic_agent

    def get_bing_search_agent(self) -> ChatCompletionAgent:
        """Create a Bing Search agent with the necessary plugins."""
        agent_name = "bing_search_agent"
        model_name = "gpt-4.1-nano"

        # Clone the base kernel and add the OpenAI service
        kernel = self.create_kernel(
            agent_name=agent_name,
            model_name=model_name
        )

        # Create the agent
        bing_search_agent = ChatCompletionAgent(
            kernel=kernel,
            name=agent_name,
            instructions=load_prompt(agent_name),
            plugins=[
                self.plugin_factory.bing_search_tool
            ]
        )

        return bing_search_agent

    # def create_agent(self,
    #                  kernel: Kernel,
    #                  agent_name: str,
    #                  model_name: str,
    #                  instructions: str = None
    #                  ) -> ChatCompletionAgent:
    #     """Create a chat completion agent."""
    #     kernel.add_service(
    #         OpenAIChatCompletion(
    #             ai_model_id=model_name,
    #             async_client=self.base_client,
    #             service_id=agent_name,
    #         )
    #     )
    #     return ChatCompletionAgent(
    #         kernel=kernel,
    #         name=agent_name,
    #         instructions=instructions or load_prompt(agent_name),
    #     )

    @staticmethod
    def execution_settings() -> OpenAIChatPromptExecutionSettings:
        """Create request settings for the OpenAI service."""
        return OpenAIChatPromptExecutionSettings(
            function_choice_behavior=FunctionChoiceBehavior.Auto(
                filters={"excluded_plugins": ["ChatBot"]}
            )
        )
