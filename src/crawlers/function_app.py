import azure.functions as func
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("azure.functions")

app = func.FunctionApp()


@app.timer_trigger(schedule="0 */5 * * * *",
                   arg_name="timer_request",
                   run_on_startup=True,
                   use_monitor=False)
def github_crawler_func(timer_request: func.TimerRequest) -> None:
    logger.info('GitHub crawler function started.')
    from github_crawler import GitHubCrawler
    github_crawler = GitHubCrawler()
    github_crawler.run()
    logger.info('GitHub crawler function finished.')
