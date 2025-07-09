from semantic_kernel.agents import ChatCompletionAgent
from agent_factory import AgentFactory
from plugin_factory import PluginFactory
import chainlit as cl
from cosmos_db_service import CosmosDBService
from data_models import ChatMessage, ChatThread
from typing import Optional


class ChatService:
    """Service for managing chat agents and plugins."""

    def __init__(self):
        self.cosmos_db_service = CosmosDBService()
        self.agent_factory = AgentFactory()
        self.plugin_factory = PluginFactory(self.agent_factory)

    def get_orchestrator_agent(self) -> ChatCompletionAgent:
        """Creates and returns an orchestrator agent with the necessary plugins."""

        orchestrator_agent = self.agent_factory.create_orchestrator_agent()
        return orchestrator_agent

    def persist_chat_message(self, chat_message: cl.Message, user_id: str) -> None:
        """Persist the chat message to the database."""

        message = ChatMessage(message=chat_message, user_id=user_id)
        self.cosmos_db_service.create_item(
            message.to_dict(), container_name="chats")

    def persist_chat_thread(self, initial_message: cl.Message, user_id: str, user_job_title: str) -> None:
        """Persist the chat thread to the database."""

        thread = ChatThread(
            thread_id=initial_message.thread_id,
            user_id=user_id,
            title=f"{str(initial_message.content)[0:50]}...",
            user_job_title=user_job_title
        )
        self.cosmos_db_service.create_item(
            thread.to_dict(), container_name="chats")

    def get_welcome_message(self, user_first_name: str, user_job_title: Optional[str] = None) -> str:
        """Returns the welcome message to the user."""

        welcome_message = f"Hi **{user_first_name}**, welcome to the STU Copilot! "

        if user_job_title:
            welcome_message += f"I consider your role as a **{user_job_title}** while assisting you. How can I help? 🙂"
        else:
            welcome_message += "I can assist you with your queries. How can I help? 🙂"

        return welcome_message
