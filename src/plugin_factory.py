from semantic_kernel.functions import kernel_function
import chainlit as cl
from agent_factory import AgentFactory


class PluginFactory:
    """A plugin to ask questions and get answers."""

    def __init__(self, agent_factory: AgentFactory = None) -> None:
        self.agent_factory = agent_factory or AgentFactory()

    @kernel_function
    @cl.step(type="tool")
    async def ask_questions(self, input: str) -> str:
        """
        Ask questions based on the provided context.

        Args:
            input (str): The context to ask questions about.

        Returns:
            str: The generated questions.
        """
        agent = self.agent_factory.create_agent(
            agent_name="questioner_agent",
            model_name="gpt-4.1-mini"
        )
        return await agent.get_response(messages=input)
