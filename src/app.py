from typing import List
import chainlit as cl
from chat_service import get_communicator_agent
from semantic_kernel.contents import ChatHistory
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread


@cl.on_chat_start
async def on_chat_start():
    # kernel = sks.create_kernel()
    # ai_service = kernel.get_service("gpt-4o-mini")
    agent = get_communicator_agent()

    # Initialize the kernel with the AI service
    # cl.user_session.set("kernel", kernel)
    # cl.user_session.set("ai_service", ai_service)
    cl.user_session.set("agent", agent)
    cl.user_session.set("chat_history", ChatHistory())


@cl.on_message
async def on_message(message: cl.Message):
    # kernel = cl.user_session.get("kernel")  # type: sk.Kernel
    # ai_service = cl.user_session.get("ai_service")  # type: AzureChatCompletion
    agent: ChatCompletionAgent = cl.user_session.get(
        "agent")  # type: ChatCompletionAgent
    chat_history = cl.user_session.get("chat_history")  # type: ChatHistory

    # Add user message to history
    chat_history.add_user_message(message.content)

    # Print the source before answering
    # source = getattr(ai_service, 'name', str(ai_service))
    # print(f"Source: {source}")

    # Create a Chainlit message for the response stream
    answer = cl.Message(content="")
    
    # async for msg in ai_service.get_streaming_chat_message_content(
    #     chat_history=chat_history,
    #     user_input=message.content,
    #     settings=sks.request_settings(),
    #     kernel=kernel,
    # ):
    thread: ChatHistoryAgentThread = None
    async for msg in agent.invoke_stream(
        messages=message.content,
        #thread=thread
    ):
        if msg.content:
            #await answer.stream_token(msg.content)
            await answer.stream_token(msg.content)
        

    # Add the full assistant response to history
    #chat_history.add_assistant_message(answer.content)
    #thread = answer.content
    
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
