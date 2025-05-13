
from chat_service import get_communicator_agent
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

agent = get_communicator_agent()
logger.info("Agent created successfully.")
logger.info(agent)
logger.info("Agent kernel:")
logger.info(agent.kernel)


