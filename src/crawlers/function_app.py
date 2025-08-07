import azure.functions as func
import logging
from dotenv import load_dotenv
from cosmos_db_service import CosmosDBService
from foundry_service import FoundryService
from psql_ping_service import PostgresPingService

# Load environment variables from .env file
load_dotenv(override=True)

# Configure logging
# logging.basicConfig(level=logging.INFO)
# logging.getLogger("azure.functions")
logging.getLogger("azure.cosmos").setLevel(logging.CRITICAL)

app = func.FunctionApp()

cosmos_db_service = CosmosDBService()
foundry_service = FoundryService()


# @app.timer_trigger(schedule="0 0 0 1 1 *",  # Run every 1 day
#                    arg_name="timer_request",
#                    run_on_startup=False,
#                    use_monitor=False)
# def github_crawler_func(timer_request: func.TimerRequest) -> None:
#     logging.info('GitHub crawler function started.')
#     from github_crawler import GitHubCrawler
#     github_crawler = GitHubCrawler(cosmos_db_service=cosmos_db_service,
#                                    foundry_service=foundry_service)
#     github_crawler.run()
#     logging.info('GitHub crawler function finished.')


@app.timer_trigger(schedule="0 0 0 * * *",  # Run every 1 day
                   arg_name="timer_request",
                   run_on_startup=True,
                   use_monitor=False)
def blogs_crawler_func(timer_request: func.TimerRequest) -> None:
    logging.info('Blogs crawler function started.')
    from blogs_crawler import BlogsCrawler
    blogs_crawler = BlogsCrawler(cosmos_db_service=cosmos_db_service,
                                 foundry_service=foundry_service)
    blogs_crawler.run()
    logging.info('Blogs crawler function finished.')


# @app.timer_trigger(schedule="0 0 0 1 1 *",  # Run every year on January 1st
#                    arg_name="timer_request",
#                    run_on_startup=False,
#                    use_monitor=False)
# def seismic_crawler_func(timer_request: func.TimerRequest) -> None:
#     logging.info('Seismic crawler function started.')
#     from seismic_crawler import SeismicCrawler
#     seismic_crawler = SeismicCrawler(cosmos_db_service=cosmos_db_service,
#                                      foundry_service=foundry_service)
#     seismic_crawler.run()
#     logging.info('Seismic crawler function finished.')


@app.timer_trigger(schedule="0 */5 * * * *",
                   arg_name="timer_request",
                   run_on_startup=True,
                   use_monitor=False)
def ping_psql_func(timer_request: func.TimerRequest) -> None:
    logging.info('Ping PostgreSQL function started.')
    postgres_ping_service = PostgresPingService()
    postgres_ping_service.run()
    logging.info('Ping PostgreSQL function finished.')
