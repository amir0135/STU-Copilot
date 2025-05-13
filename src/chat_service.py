from agent_factory import create_agent, AgentType
from semantic_kernel.agents import ChatCompletionAgent
from plugin_factory import QuestionerPlugin





def get_communicator_agent() -> ChatCompletionAgent:
    """
    Create a communicator agent for the kernel.

    Returns:
        ChatCompletionAgent: The created communicator agent.
    """

    communicator_agent = create_agent(
        agent_name=AgentType.communicator_agent,
        model_name="gpt-4.1-mini"
    )

    communicator_agent.kernel.add_plugin(
        QuestionerPlugin(),
        plugin_name=AgentType.questioner_agent)

    return communicator_agent
