from typing import List
import chainlit as cl
import semantic_kernel_service as sks
from semantic_kernel.contents import ChatHistory


@cl.on_chat_start
async def on_chat_start():
    kernel = sks.create_kernel()
    ai_service = kernel.get_service("gpt-4o-mini")

    # Initialize the kernel with the AI service
    cl.user_session.set("kernel", kernel)
    cl.user_session.set("ai_service", ai_service)
    cl.user_session.set("chat_history", ChatHistory())


@cl.on_message
async def main(message: cl.Message):
    kernel = cl.user_session.get("kernel")  # type: sk.Kernel
    ai_service = cl.user_session.get("ai_service")  # type: AzureChatCompletion
    chat_history = cl.user_session.get("chat_history")  # type: ChatHistory

    # Add user message to history
    chat_history.add_user_message(message.content)

    # Create a Chainlit message for the response stream
    answer = cl.Message(content="")

    async for msg in ai_service.get_streaming_chat_message_content(
        chat_history=chat_history,
        user_input=message.content,
        settings=sks.request_settings(),
        kernel=kernel,
    ):
        if msg.content:
            await answer.stream_token(msg.content)

    # Add the full assistant response to history
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
            label="Customer Support Agent",
            message="Develop an AI agent to handle customer support queries.",
        ),
    ]
