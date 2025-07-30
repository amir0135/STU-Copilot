import chainlit as cl
from typing import Optional, List


class ChatService:
    """Service for managing chat agents and plugins."""
        
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
            {
                "id": "GitHub",
                "icon": "github",
                "description": "Search for GitHub repositories"
            },
            {
                "id": "Microsoft Docs",
                "icon": "file-search",
                "description": "Search Microsoft documentation"
            },
            {
                "id": "Seismic Presentations",
                "icon": "presentation",
                "description": "Search for Seismic content"
            },
            {
                "id": "Blog Posts",
                "icon": "rss",
                "description": "Search for blog posts"
            },
            {
                "id": "Bing Search",
                "icon": "search",
                "description": "Search the web using Bing",
            }
        ]

    def get_actions(self, agent_name: str) -> List[cl.Action]:
        """Get the actions available for the specified agent."""

        agents_dict = {
            "microsoft_docs_agent":
                cl.Action(name="action_button",
                          label="Search Microsoft Docs",
                          payload={"command": "Microsoft Docs"},
                          icon="file-search"),
            "github_agent":
                cl.Action(name="action_button",
                          label="Search GitHub Repos",
                          payload={"command": "GitHub"},
                          icon="github"),
            "seismic_agent":
                cl.Action(name="action_button",
                          label="Search Seismic Content",
                          payload={"command": "Seismic Presentations"},
                          icon="presentation"),
            "blog_posts_agent":
                cl.Action(name="action_button",
                          label="Search Blog Posts",
                          payload={"command": "Blog Posts"},
                          icon="rss"),
            "bing_search_agent":
                cl.Action(name="action_button",
                          label="Search with Bing",
                          payload={"command": "Bing Search"},
                          icon="search"),
        }

        # Return all the actions except the one for the specified agent
        actions: List[cl.Action] = []
        for key, action in agents_dict.items():
            if key != agent_name:
                actions.append(action)

        return actions

# Global instance
chat_service = ChatService()