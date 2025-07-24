import chainlit as cl
from .cosmos_db_service import CosmosDBService
from .data_models import ChatMessage, ChatThread
from typing import Optional
import logging

# Basic logging configuration
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing chat agents and plugins."""

    def __init__(self):
        self.cosmos_db_service = CosmosDBService()

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

        welcome_message = f"👋 Hi **{user_first_name}**, welcome to **STU Copilot**! "

        if user_job_title:
            welcome_message += f"I consider your role as a **{user_job_title}** while assisting you. "

        welcome_message += "If you have any questions or need support related to Microsoft solutions, sales, technical guidance, or industry insights, please let me know. "

        return welcome_message

    def get_commands(self) -> list:
        """Return the list of available commands."""

        return [
            {"id": "GitHub", "icon": "github", "description": "Search for GitHub repositories"},            
            {"id": "Microsoft Docs", "icon": "file-search", "description": "Search Microsoft documentation"},
            {"id": "Seismic Presentation", "icon": "presentation", "description": "Search for Seismic content"},
            {"id": "Blog Posts", "icon": "rss", "description": "Search for blog posts", },            
            {"id": "Bing Search", "icon": "search", "description": "Use Bing to search the web"},
        ]
