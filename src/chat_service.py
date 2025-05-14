from semantic_kernel.agents import ChatCompletionAgent
from agent_factory import AgentFactory
from plugin_factory import PluginFactory
import chainlit as cl
from cosmos_db_service import CosmosDBService
from data_models import ChatMessage

class ChatService:
    """Service for managing chat agents and plugins."""

    def __init__(self):
        self.cosmos_db_service = CosmosDBService()
        self.agent_factory = AgentFactory()
        self.plugin_factory = PluginFactory(self.agent_factory)

    def get_communicator_agent(self) -> ChatCompletionAgent:
        """Creates and returns a communicator agent with the necessary plugins."""

        communicator_agent = self.agent_factory.create_agent(
            agent_name="communicator_agent",
            model_name="gpt-4.1-mini"
        )

        communicator_agent.kernel.add_plugin(
            PluginFactory(),
            plugin_name="tools")

        return communicator_agent
    
    def persist_message(self, chat_message: cl.Message, user_id: str):
        """Persist the chat message to the database."""
        
        message = ChatMessage(message=chat_message, user_id=user_id)    
        self.cosmos_db_service.create_item(message.to_dict(), container_name="chats")
