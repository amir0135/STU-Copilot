from typing import List
from semantic_kernel.kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent


def router_agent(kernel: Kernel) -> ChatCompletionAgent:
    """
    Create a router agent for the kernel.
    """
    # Create a router agent
    router_agent = ChatCompletionAgent(
        kernel=kernel,
        name="RouterAgent",
        instructions=get_instructions("RouterAgent"),
        #plugins=get_agents(kernel)    
    )

    # Add the agent to the kernel
    kernel.add_agent(router_agent)

    return router_agent


def get_agents(kernel: Kernel) -> List[ChatCompletionAgent]:
    """
    Create a list of agents for the kernel.

    Args:
        kernel (Kernel): The kernel instance to which the agents will be added.

    Returns:
        List[ChatCompletionAgent]: A list of created agents.
    """

    agents = []

    # Questioner agent
    questioner_agent = ChatCompletionAgent(
        kernel=kernel,
        name="QuestionerAgent",
        instructions=get_instructions("QuestionerAgent"))
    agents.append(questioner_agent)
    
    # GitHub agent
    github_agent = ChatCompletionAgent(
        kernel=kernel,
        name="GitHubAgent",
        instructions=get_instructions("GitHubAgent"))
    agents.append(github_agent)
    
    # Industry agent
    industry_agent = ChatCompletionAgent(
        kernel=kernel,
        name="IndustryAgent",
        instructions=get_instructions("IndustryAgent"))
    agents.append(industry_agent)
    
    # Architect agent
    architect_agent = ChatCompletionAgent(
        kernel=kernel,
        name="ArchitectAgent",
        instructions=get_instructions("ArchitectAgent"))
    agents.append(architect_agent)
    
    # Price calculator agent
    price_calculator_agent = ChatCompletionAgent(
        kernel=kernel,
        name="PriceCalculatorAgent",
        instructions=get_instructions("PriceCalculatorAgent"))
    agents.append(price_calculator_agent)

    

    return agents


def get_instructions(agent_name: str) -> str:
    """
    Get the instructions for a specific agent.

    Args:
        agent_name (str): The name of the agent.

    Returns:
        str: The instructions for the agent.
    """

    # Define instructions for each agent
    instructions = {
        "QuestionerAgent": """
        
        """,
        "GitHubAgent": """
        
        """,
        "IndustryAgent": """
        
        """,
        "ArchitectAgent": """
        
        """,
        "PriceCalculatorAgent": """
        
        """,
        "RouterAgent": """
        """

    }

    return instructions.get(agent_name, "")
