import chainlit as cl
from typing import Optional, List
from chainlit.types import CommandDict
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.contents import ChatHistory


class ChatService:
    """Service for managing chat agents and plugins."""

    def get_welcome_message(self, user_first_name: str, user_job_title: Optional[str] = None) -> str:
        """Returns the welcome message to the user."""

        welcome_message = f"👋 Hi **{user_first_name}**, welcome to **STU Copilot**! "

        if user_job_title:
            welcome_message += f"I consider your role as a **{user_job_title}** while assisting you. "

        welcome_message += "If you have any questions or need support related to Microsoft solutions, sales, technical guidance, or industry insights, please let me know. "

        return welcome_message

    def get_commands(self) -> list[CommandDict]:
        """Return the list of available commands."""

        return [

            {
                "id": "Microsoft Docs",
                "icon": "file-search",
                "description": "Search Microsoft documentation"
            },
            {
                "id": "GitHub Docs",
                "icon": "file-search",
                "description": "Search GitHub documentation"
            },
            {
                "id": "GitHub",
                "icon": "github",
                "description": "Search for GitHub repositories"
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
            "github_docs_search_agent":
                cl.Action(name="action_button",
                          label="Search GitHub Docs",
                          payload={"command": "GitHub Docs"},
                          icon="file-search"),
            "github_agent":
                cl.Action(name="action_button",
                          label="Search GitHub Repositories",
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

    def select_responder_agent(self,
                               agents: dict[str, ChatCompletionAgent],
                               current_message: cl.Message,
                               chat_history: ChatHistory,
                               latest_agent_name: str) -> ChatCompletionAgent:
        """Select the appropriate agent based on the current message and chat history."""

        print(f"Current message command: {current_message.command}")
        print(f"Chat history length: {len(chat_history)}")
        print(f"Latest agent in use: {latest_agent_name}")

        # If the current message is a command, use the corresponding agent
        if current_message.command:
            # Handle command messages using dictionary mapping
            command_agent_map = {
                "Microsoft Docs": agents["microsoft_docs"],
                "GitHub Docs": agents["github_docs_search"],
                "GitHub": agents["github"],
                "Seismic Presentations": agents["seismic"],
                "Blog Posts": agents["blog_posts"],
                "Bing Search": agents["bing_search"],
            }
            return command_agent_map.get(current_message.command)

        # If the current message is not a command, determine the agent based on the chat history
        elif latest_agent_name is None:
            return agents["questioner"]
        elif latest_agent_name == "questioner_agent":
            return agents["microsoft_docs"]
        else:
            return agents["orchestrator"]



# Global instance
chat_service = ChatService()
