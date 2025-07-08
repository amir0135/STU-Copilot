import os
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from utils import load_prompt


class AgentFactory:
    """Factory for creating chat completion agents."""

    def __init__(self):
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AI_FOUNDRY_KEY")
        if not endpoint or not api_key:
            raise EnvironmentError(
                "Missing Azure Open AI endpoint or API key.")

    def create_orchestrator_agent(self) -> ChatCompletionAgent:
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
                self.create_questioner_agent(),  # Add the questioner agent as a plugin
            ]
        )

        # Add plugins to the agent
        # orchestrator_agent.kernel.add_plugin(
        #     kernel.get_plugin("tools"),
        #     plugin_name="tools"
        # )

        return orchestrator_agent

    def create_questioner_agent(self) -> ChatCompletionAgent:
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

    def create_kernel(self,
                      agent_name: str,
                      model_name: str) -> Kernel:
        """Create a kernel with the desired model."""
        kernel = Kernel()
        kernel.add_service(
            AzureChatCompletion(
                deployment_name=model_name,
                service_id=agent_name)
        )
        return kernel

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
    def request_settings() -> OpenAIChatPromptExecutionSettings:
        """Create request settings for the OpenAI service."""
        return OpenAIChatPromptExecutionSettings(
            function_choice_behavior=FunctionChoiceBehavior.Auto(
                filters={"excluded_plugins": ["ChatBot"]}
            )
        )
