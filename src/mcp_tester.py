# import asyncio
# from fastmcp import Client


# client = Client("https://learn.microsoft.com/api/mcp")

# async def call_tool(name: str):
#     async with client:
#         result = await client.call_tool("microsoft_docs_search", {"question": name})
#         print(result)

# asyncio.run(call_tool("ai foundry ref architecture"))


# async with MCPStreamableHttpPlugin(
#     name="Microsoft Documentation Search",
#     url="https://learn.microsoft.com/api/mcp"
# ) as plugin:
#     results = await plugin.call_tool("microsoft_docs_search", question=input)
# return results

# result = None
# transport = StreamableHttpTransport(url="https://learn.microsoft.com/api/mcp")
# async with Client(transport) as client:
#     result = await client.call_tool(
#         name="microsoft_docs_search",
#         raise_on_error=False,
#         arguments={"question": input})
# return result


from typing import List
import dotenv
import chainlit as cl
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel.contents import ChatHistory
from services.agent_factory import AgentFactory
from semantic_kernel.connectors.mcp import MCPStdioPlugin, MCPSsePlugin
import logging

dotenv.load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)
logging.getLogger("openai").setLevel(logging.INFO)
logging.getLogger("semantic_kernel").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

agent_factory = AgentFactory()
agent_name = "orchestrator_agent"
model_name = "gpt-4.1"

# Create a new kernel instance with the OpenAI service
kernel = agent_factory.create_kernel(
    agent_name=agent_name,
    model_name=model_name
)


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("chat_history", ChatHistory())
    cl.user_session.set("thread", None)


@cl.on_message
async def on_message(user_message: cl.Message):
    chat_history: ChatHistory = cl.user_session.get("chat_history")
    thread: ChatHistoryAgentThread = cl.user_session.get("thread")

    chat_history.add_user_message(user_message.content)
    answer = cl.Message(content="")

    async with MCPSsePlugin(
        name="MS Docs",
        description="MS Docs Plugin",
        url="https://learn.microsoft.com/api/mcp",
        request_timeout=60
    ) as ms_docs_plugin:

        # Create the agent
        agent = ChatCompletionAgent(
            kernel=kernel,
            name=agent_name,
            instructions="Answer the user's question using the available plugins.",
            plugins=[
                ms_docs_plugin
            ]
        )

        # Stream the agent's response token by token
        async for token in agent.invoke_stream(
                messages=chat_history,
                thread=thread
        ):
            if token.content:
                await answer.stream_token(token.content.content)

        chat_history.add_assistant_message(answer.content)
        cl.user_session.set("thread", thread)
        await answer.send()


@cl.set_starters  # type: ignore
async def set_starts() -> List[cl.Starter]:
    return [
        cl.Starter(
            label="Latest 10 commits",
            message="What are the last 10 commits in the Microsoft/semantic-kernel repository?",
        ),
        cl.Starter(
            label="Issue #10785?",
            message="What is the status of issue #10785 in the Microsoft/semantic-kernel repository? Provide the link to the issue.",
        ),
        cl.Starter(
            label="Latest 10 issues",
            message="List the last 10 issues in Microsoft/semantic-kernel?",
        )
    ]
