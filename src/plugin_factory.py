
from semantic_kernel.functions import kernel_function
from agent_factory import create_agent
import chainlit as cl

class QuestionerPlugin:    
    def __init__(self):
        self.name = "questioner_plugin"
        self.description = "A plugin to ask questions and get answers."
        self.agent = create_agent(
            agent_name="questioner_agent",
            model_name="gpt-4o-mini"
        )

    @kernel_function
    @cl.step(type="tool")
    async def ask_questions(self, context: str) -> str:
        """
        Ask questions based on the provided context.

        Args:
            context (str): The context to ask questions about.

        Returns:
            str: The generated questions.
        """

        # Use the agent to ask questions
        response = await self.agent.invoke_async(context)
        return response
