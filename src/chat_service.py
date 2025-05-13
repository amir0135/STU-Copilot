from semantic_kernel.agents import ChatCompletionAgent
from agent_factory import AgentFactory
from plugin_factory import PluginFactory
from cosmos_db_service import CosmosDBService


class ChatService:
    """Service for managing chat agents and plugins."""

    def __init__(self):
        self.agent_factory = AgentFactory()
        self.plugin_factory = PluginFactory(self.agent_factory)
        # self.cosmos_db_service = CosmosDBService()

    def get_communicator_agent(self) -> ChatCompletionAgent:
        """
        Create a communicator agent for the kernel.

        Returns:
            ChatCompletionAgent: The created communicator agent.
        """

        communicator_agent = self.agent_factory.create_agent(
            agent_name="communicator_agent",
            model_name="gpt-4.1-mini"
        )

        communicator_agent.kernel.add_plugin(
            PluginFactory(),
            plugin_name="tools")

        return communicator_agent
