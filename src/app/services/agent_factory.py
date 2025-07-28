import os
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent, GroupChatManager, GroupChatOrchestration, BooleanResult, StringResult, MessageResult
from semantic_kernel.contents import ChatMessageContent, ChatHistory
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from .cache_service import load_prompt
from .plugin_factory import (
    GitHubPlugin, MicrosoftDocsPlugin, BlogPostsPlugin,
    SeismicPlugin, BingPlugin
)
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

        self.plugins = {
            "github": GitHubPlugin(),
            "microsoft_docs": MicrosoftDocsPlugin(),
            "blog_posts": BlogPostsPlugin(),
            "seismic": SeismicPlugin(),
            "bing": BingPlugin()
        }
        self.agents = {
            "questioner": self.get_questioner_agent(),
            "planner": self.get_planner_agent(),
            "github": self.get_github_agent(),
            "microsoft_docs": self.get_microsoft_docs_agent(),
            "blog_posts": self.get_blog_posts_agent(),
            "seismic": self.get_seismic_agent(),
            "bing_search": self.get_bing_search_agent(),
            "architect": self.get_architect_agent()
        }
        self.agents["orchestrator"] = self.get_orchestrator_agent()

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

    def get_agents(self) -> dict[str, ChatCompletionAgent]:
        """Get all agents."""
        return self.agents

    def get_orchestrator_agent(self) -> ChatCompletionAgent:
        """Create an orchestrator agent with the necessary plugins."""
        agent_name = "orchestrator_agent"
        model_name = "gpt-4.1"

        # Create a new kernel instance with the OpenAI service
        kernel = self.create_kernel(
            agent_name=agent_name,
            model_name=model_name,

        )

        # Create the agent
        orchestrator_agent = ChatCompletionAgent(
            kernel=kernel,
            name=agent_name,
            instructions=load_prompt(agent_name),
            plugins=[
                self.agents["questioner"],
                self.agents["planner"]
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
        model_name = "gpt-4.1-mini"

        # Clone the base kernel and add the OpenAI service
        kernel = self.create_kernel(
            agent_name=agent_name,
            model_name=model_name,
        )

        # Create the agent
        github_agent = ChatCompletionAgent(
            kernel=kernel,
            name=agent_name,
            instructions=load_prompt(agent_name),
            plugins=[self.plugins["github"].github_repository_search]
        )

        return github_agent

    def get_microsoft_docs_agent(self) -> ChatCompletionAgent:
        """Create a Microsoft Docs agent with the necessary plugins."""
        agent_name = "microsoft_docs_agent"
        model_name = "gpt-4.1"

        # Clone the base kernel and add the OpenAI service
        kernel = self.create_kernel(
            agent_name=agent_name,
            model_name=model_name
        )

        # Create the agent
        microsoft_docs_agent = ChatCompletionAgent(
            kernel=kernel,
            name=agent_name,
            instructions=load_prompt(agent_name),
            plugins=[self.plugins["microsoft_docs"].microsoft_docs_search]
        )

        return microsoft_docs_agent

    def get_blog_posts_agent(self) -> ChatCompletionAgent:
        """Create a Blog Posts agent with the necessary plugins."""
        agent_name = "blog_posts_agent"
        model_name = "gpt-4.1-mini"

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
            plugins=[self.plugins["blog_posts"].blog_posts_search]
        )

        return blog_posts_agent

    def get_seismic_agent(self) -> ChatCompletionAgent:
        """Create a Seismic agent with the necessary plugins."""
        agent_name = "seismic_agent"
        model_name = "gpt-4.1-mini"

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
            plugins=[self.plugins["seismic"].seismic_search]
        )

        return seismic_agent

    def get_bing_search_agent(self) -> ChatCompletionAgent:
        """Create a Bing Search agent with the necessary plugins."""
        agent_name = "bing_search_agent"
        model_name = "gpt-4.1-mini"

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
            plugins=[self.plugins["bing"].bing_search]
        )

        return bing_search_agent

    def get_architect_agent(self) -> ChatCompletionAgent:
        """Create an architect agent with the necessary plugins."""
        agent_name = "architect_agent"
        model_name = "o3-mini"

        # Clone the base kernel and add the OpenAI service
        kernel = self.create_kernel(
            agent_name=agent_name,
            model_name=model_name
        )

        # Create the agent
        architect_agent = ChatCompletionAgent(
            kernel=kernel,
            name=agent_name,
            instructions=load_prompt(agent_name),
            plugins=[
                self.plugins["microsoft_docs"].microsoft_docs_search,
                self.plugins["bing"].bing_search
            ]
        )

        return architect_agent

    def get_architecture_group_chat_manager(self) -> GroupChatOrchestration:
        """Create an architecture group chat manager."""
        agent_name = "seismic_agent"
        model_name = "gpt-4.1"

        # Clone the base kernel and add the OpenAI service
        kernel = self.create_kernel(
            agent_name=agent_name,
            model_name=model_name
        )

        # Create the group chat manager
        group_chat_orchestration = GroupChatOrchestration(
            kernel=kernel,
            name="architecture_group_chat_manager",
            manager=AgentFactory.ArchitectureGroupChatManager(max_rounds=5),
            members=[
                self.agents["questioner"],
                self.agents["microsoft_docs"],
                self.agents["github"]
            ],
            agent_response_callback=self.agent_response_callback
        )
        
        return group_chat_orchestration

    def agent_response_callback(self, message: ChatMessageContent) -> None:
        print(f"**{message.name}**\n{message.content}")

    @staticmethod
    def execution_settings() -> OpenAIChatPromptExecutionSettings:
        """Create request settings for the OpenAI service."""
        return OpenAIChatPromptExecutionSettings(
            function_choice_behavior=FunctionChoiceBehavior.Auto()
        )

    class ArchitectureGroupChatManager(GroupChatManager):
        async def filter_results(self, chat_history: ChatHistory) -> MessageResult:
            # Custom logic to filter or summarize chat results
            summary = "Summary of the discussion."
            return MessageResult(result=ChatMessageContent(role="assistant", content=summary), reason="Custom summary logic.")

        async def select_next_agent(self, chat_history: ChatHistory, participant_descriptions: dict[str, str]) -> StringResult:
            # Randomly select an agent from the participants
            print("Current round:", self.current_round)
            import random
            next_agent = random.choice(list(participant_descriptions.keys()))
            return StringResult(result=next_agent, reason="Custom selection logic.")

        async def should_request_user_input(self, chat_history: ChatHistory) -> BooleanResult:
            # Custom logic to decide if user input is needed
            if len(chat_history.messages) < 3:
                return BooleanResult(result=True, reason="More context needed from user.")
            return BooleanResult(result=False, reason="No user input required.")

        async def should_terminate(self, chat_history: ChatHistory) -> BooleanResult:
            # Optionally call the base implementation to check for default termination logic
            base_result = await super().should_terminate(chat_history)
            if base_result.result:
                return base_result
            # Custom logic to determine if the chat should terminate
            # Example: end after 50 messages
            should_end = len(chat_history.messages) > 50
            return BooleanResult(result=should_end, reason="Custom termination logic.")
