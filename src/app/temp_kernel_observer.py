from cosmos_db_service import CosmosDBService
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_service = CosmosDBService()
logger.info("CosmosDBService initialized successfully.")

logger.info(db_service.database)

container_client = db_service.get_container("chats")

logger.info(container_client)


