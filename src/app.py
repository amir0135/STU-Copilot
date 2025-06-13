from typing import List, Dict, Optional
import chainlit as cl
from chat_service import ChatService
from semantic_kernel.contents import ChatHistory
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
import logging

# Basic logging configuration
logging.basicConfig(level=logging.WARNING)

logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("azure.cosmos").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.INFO)
logging.getLogger("semantic_kernel").setLevel(logging.INFO)


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
    cl.user_session.set("user_id", "test_user")
    cl.user_session.set("chat_service", ChatService())
    cl.user_session.set("chat_history", ChatHistory())
    cl.user_session.set("chat_thread", None)


@cl.on_message
async def on_message(user_message: cl.Message):
    user_id: str = cl.user_session.get("user_id")
    chat_service: ChatService = cl.user_session.get("chat_service")
    chat_history: ChatHistory = cl.user_session.get("chat_history")
    chat_thread: ChatHistoryAgentThread = cl.user_session.get("chat_thread")
    agent: ChatCompletionAgent = chat_service.get_communicator_agent()

    chat_history.add_user_message(user_message.content)
    answer = cl.Message(content="")

    chat_service.persist_chat_message(user_message, user_id)

    # Stream the agent's response token by token
    async for token in agent.invoke_stream(
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
    if (len(chat_history) == 2):
        await chat_service.persist_chat_thread(user_message, user_id)


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
