from typing import List, Dict, Optional
import chainlit as cl
from services.chat_service import ChatService
from services.agent_factory import AgentFactory
from semantic_kernel.contents import ChatHistory
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
import logging

# Basic logging configuration
logging.basicConfig(level=logging.WARNING)
logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("azure.cosmos").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.INFO)
logging.getLogger("semantic_kernel").setLevel(logging.INFO)
logging.getLogger("fastmcp").setLevel(logging.WARNING)
logging.getLogger("http").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# Initialize services and agents
chat_service: ChatService = ChatService()
agent_factory: AgentFactory = AgentFactory()
orchestrator_agent: ChatCompletionAgent = agent_factory.get_orchestrator_agent()
questioner_agent: ChatCompletionAgent = agent_factory.get_questioner_agent()
planner_agent: ChatCompletionAgent = agent_factory.get_planner_agent()
github_agent: ChatCompletionAgent = agent_factory.get_github_agent()
microsoft_docs_agent: ChatCompletionAgent = agent_factory.get_microsoft_docs_agent()
blog_posts_agent: ChatCompletionAgent = agent_factory.get_blog_posts_agent()
seismic_agent: ChatCompletionAgent = agent_factory.get_seismic_agent()

@cl.oauth_callback
async def oauth_callback(
    provider_id: str,
    token: str,
    raw_user_data: Dict[str, str],
    default_user: cl.User,
) -> Optional[cl.User]:
    print(f"OAuth callback for provider {provider_id}")
    default_user.identifier = raw_user_data["mail"]
    default_user.display_name = raw_user_data["displayName"]
    default_user.metadata["user_id"] = raw_user_data["id"]
    default_user.metadata["first_name"] = raw_user_data["givenName"]
    default_user.metadata["job_title"] = raw_user_data["jobTitle"]
    default_user.metadata["office_location"] = raw_user_data["officeLocation"]
    return default_user


@cl.on_chat_start
async def on_chat_start():
    chat_history: ChatHistory = ChatHistory()
    user = cl.user_session.get("user")
    welcome_message = chat_service.get_welcome_message(
        user_first_name=user.metadata.get("first_name", "Guest"),
        user_job_title=user.metadata.get("job_title", None),
    )

    # Show the welcome message to the user
    await cl.Message(content=welcome_message).send()
    
    icon_element = cl.CustomElement(name="Icon")
    await cl.Message(content="", elements=[icon_element]).send()

    chat_history.add_assistant_message(welcome_message)

    loading_message = cl.Message(content="⏳ Thinking...")

    cl.user_session.set("chat_service", chat_service)
    cl.user_session.set("chat_history", chat_history)
    cl.user_session.set("chat_thread", None)
    cl.user_session.set("loading_message", loading_message)


@cl.on_message
async def on_message(user_message: cl.Message):
    user_id: str = cl.user_session.get("user_id")
    user_job_title: str = cl.user_session.get("job_title")
    chat_service: ChatService = cl.user_session.get("chat_service")
    chat_history: ChatHistory = cl.user_session.get("chat_history")
    chat_thread: ChatHistoryAgentThread = cl.user_session.get("chat_thread")
    loading_message: cl.Message = cl.user_session.get("loading_message")
    responder_agent: ChatCompletionAgent = github_agent

    chat_history.add_user_message(user_message.content)
    answer = cl.Message(content="")

    chat_service.persist_chat_message(user_message, user_id)    
    
    # If this is the beginning of a new chat thread, use the questioner agent
    # if (len(chat_history) == 2):
    #     responder_agent = questioner_agent
    # # Otherwise, use the orchestrator agent
    # elif (len(chat_history) == 4):
    #     responder_agent = planner_agent
    #     await loading_message.send()
    # else:
    #     responder_agent = orchestrator_agent

    # Stream the agent's response token by token
    async for token in responder_agent.invoke_stream(
            messages=chat_history,
            thread=chat_thread
    ):        
        if token.content:
            await answer.stream_token(token.content.content)

    cl.user_session.set("chat_thread", token.thread)
    chat_history.add_assistant_message(answer.content)

    chat_service.persist_chat_message(answer, user_id)

    # Send the final message
    await answer.send()

    # Persist the chat thread if it is the first message
    if (len(chat_history) == 3):
        chat_service.persist_chat_thread(user_message, user_id, user_job_title)


@cl.set_starters  # type: ignore
async def set_starts() -> List[cl.Starter]:
    return [
        cl.Starter(
            label="AI Assistant",
            message="Design an AI assistant with frontend, backend, and database integration.",
        ),
        cl.Starter(
            label="Data Analysis Bot",
            message="Create a bot to analyze and visualize data trends.",
        ),
        cl.Starter(
            label="Weather Bot",
            message="How is the weather today?",
        ),
    ]
