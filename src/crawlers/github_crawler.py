from dotenv import load_dotenv
import logging
import asyncio
import aiohttp
from typing import List
from data_models import RepositoryInfo
from cosmos_db_service import CosmosDBService
from foundry_service import FoundryService

# Load environment variables from .env file
load_dotenv(override=True)

# Configure logging
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("azure.cosmos").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Organizations to crawl
github_organizations = [
    "Azure-Samples",
    "Microsoft",
    "AzureCosmosDB",
    "Azure"
]

# Azure CosmosDB configuration
cosmosdb_container_name = "github-repos"

# Initialize the CosmosDB service
cosmos_db_service = CosmosDBService()

# Initialize the embedding service
foundry_service = FoundryService()


async def fetch_org_repositories(organization: str) -> List[RepositoryInfo]:
    """Fetch repositories for a given organization from GitHub API in a paginated manner."""

    logger.info(f"Fetching repositories for organization: {organization}")

    # Fetch repositories for the organization in paginated manner
    async with aiohttp.ClientSession() as session:
        page = 1
        page_size = 5
        total_repos = 0
        org_repos: List[RepositoryInfo] = []

        headers = {
            'User-Agent': 'GitHubCrawler/1.0',
            'Accept': 'application/vnd.github.v3+json',
        }

        while total_repos == 0:  # Pagination loop
            url = f"https://api.github.com/orgs/{organization}/repos?type=public&per_page={page_size}&page={page}"
            async with session.get(url, headers=headers) as response:
                if response.status == 403:
                    # Check for rate limit
                    remaining = response.headers.get("X-RateLimit-Remaining")
                    reset = response.headers.get("X-RateLimit-Reset")
                    if remaining == "0" and reset:
                        reset_time = int(reset)
                        wait_seconds = max(
                            reset_time - int(asyncio.get_event_loop().time()), 1)
                        logger.warning(
                            f"Rate limit reached for {organization}. Waiting {wait_seconds} seconds before retrying."
                        )
                        await asyncio.sleep(wait_seconds)
                        continue  # Retry the same page after sleeping
                    else:
                        logger.error(
                            f"Failed to fetch repositories for {organization}: {response.status} (possibly forbidden)"
                        )
                        break

                if response.status != 200:
                    logger.error(
                        f"Failed to fetch repositories for {organization}: {response.status}")
                    break

                repos = await response.json()
                if not repos:
                    break
                else:
                    for repo in repos:
                        repo_info = RepositoryInfo(
                            id=str(repo['id']),
                            organization=organization,
                            name=repo['name'],
                            description=repo["description"],
                            url=repo['html_url'],
                            updated_at=repo['updated_at'],
                            stars_count=repo['stargazers_count'],
                            archived=repo['archived']
                        )
                        org_repos.append(repo_info)

                total_repos += len(repos)

                logger.info(
                    f"Fetched {len(repos)} repositories from {organization} (Page {page})")

                page += 1
                await asyncio.sleep(0.1)

        return org_repos


def generate_readme_urls(repo: RepositoryInfo) -> list:
    """
    Generate possible README file URLs for a given repository.
    """
    branches = ["master", "main"]
    filenames = [
        "README.md", "readme.md",
        "README.text", "readme.text",
        "README.txt", "readme.txt",
        # "README", "readme"
    ]
    urls = [
        f"https://raw.githubusercontent.com/{repo.organization}/{repo.name}/refs/heads/{branch}/{filename}"
        for branch in branches
        for filename in filenames
    ]
    return urls


async def fetch_readme_content(repo: RepositoryInfo) -> str:
    """Fetch README content for a repository"""

    readme_urls = generate_readme_urls(repo)
    readme_content = None

    async with aiohttp.ClientSession() as session:
        for url in readme_urls:
            async with session.get(url) as response:
                if response.status == 200:
                    readme_content = await response.text()
                    break  # Stop after first successful fetch

    if readme_content is None:
        logger.warning(
            f"No README found for {repo.name} in {repo.organization}")
    return readme_content or ""


async def process_repository(repo: RepositoryInfo) -> None:
    """Process a repository: fetch README, generate embeddings, and save to CosmosDB."""

    try:
        # Fetch README content for the repository
        readme_content = await fetch_readme_content(repo)
        
        # Generate description for the repository
        context = f"{repo.description}\n\n{readme_content}"
        summary, keywords = foundry_service.summarize_and_generate_keywords(context)
        repo.description = summary
        repo.keywords = keywords

        # Save repository to CosmosDB
        cosmos_db_service.upsert_item(
            item=repo.to_dict(),
            container_name=cosmosdb_container_name
        )

    except Exception as e:
        logger.error(
            f"Error processing repository {repo.organization}/{repo.name}: {e}")


async def crawl_organization(organization: str) -> None:
    """Main function to crawl an organization and save repositories to CosmosDB."""

    logger.info(f"Starting crawl for organization: {organization}")

    # Fetch repositories for the organization
    org_repos = await fetch_org_repositories(organization)
    if not org_repos:
        logger.info(
            f"No repositories found for organization: {organization}")
        return

    logger.info(
        f"Total repositories fetched for {organization}: {len(org_repos)}")

    for repo in org_repos:
        await process_repository(repo)
        await asyncio.sleep(0.1)

    logger.info(
        f"Finished processing {len(org_repos)} repositories for organization: {organization}")


async def main():
    """Main function to run the GitHub crawler"""
    logger.info("GitHub crawler started.")

    # Crawl each organization
    for org in github_organizations:
        await crawl_organization(org)

    logger.info("GitHub crawler finished.")

if __name__ == "__main__":
    asyncio.run(main())
