import logging
from github_crawler import GitHubCrawler
from dotenv import load_dotenv
from cosmos_db_service import CosmosDBService
from foundry_service import FoundryService

# Load environment variables from .env file
load_dotenv(override=True)

cosmos_db_service = CosmosDBService()
foundry_service = FoundryService()

logging.basicConfig(level=logging.INFO)
logging.getLogger("azure.cosmos").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)
logger.info('GitHub crawler function started.')

github_crawler = GitHubCrawler(cosmos_db_service=cosmos_db_service,
                                   foundry_service=foundry_service)
github_crawler.run()
logger.info('GitHub crawler function finished.')