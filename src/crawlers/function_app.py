import azure.functions as func
import logging
from dotenv import load_dotenv
from cosmos_db_service import CosmosDBService
from foundry_service import FoundryService

# Load environment variables from .env file
load_dotenv(override=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("azure.functions")

app = func.FunctionApp()

cosmos_db_service = CosmosDBService()
foundry_service = FoundryService()

@app.timer_trigger(schedule="0 */5 * * * *",
                   arg_name="timer_request",
                   run_on_startup=True,
                   use_monitor=False)
def github_crawler_func(timer_request: func.TimerRequest) -> None:
    logger.info('GitHub crawler function started.')
    from github_crawler import GitHubCrawler
    github_crawler = GitHubCrawler(cosmos_db_service=cosmos_db_service,
                                   foundry_service=foundry_service)
    github_crawler.run()
    logger.info('GitHub crawler function finished.')
