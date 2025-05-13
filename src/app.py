from typing import List
import chainlit as cl
from chat_service import ChatService
from semantic_kernel.contents import ChatHistory
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread


@cl.on_chat_start
async def on_chat_start():
    chatService = ChatService()
    agent = chatService.get_communicator_agent()
    cl.user_session.set("agent", agent)
    cl.user_session.set("thread", None)
    cl.user_session.set("chat_history", ChatHistory())


@cl.on_message
async def on_message(message: cl.Message):
    agent: ChatCompletionAgent = cl.user_session.get("agent")
    chat_history: ChatHistory = cl.user_session.get("chat_history")
    thread: ChatHistoryAgentThread = cl.user_session.get("thread")

    chat_history.add_user_message(message.content)
    answer = cl.Message(content="")

    # Stream the agent's response token by token
    async for token in agent.invoke_stream(
            messages=chat_history,
            thread=thread
    ):
        if token.content:
            await answer.stream_token(token.content.content)
    thread = token.thread
    chat_history.add_assistant_message(answer.content)

    # Send the final message
    await answer.send()


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
