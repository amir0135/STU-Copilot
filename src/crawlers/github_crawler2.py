import os
from dotenv import load_dotenv
import logging
import asyncio
import aiohttp
from typing import List, Dict, Optional
from cosmos_db_service import CosmosDBService
from embedding_service import EmbeddingService

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
    "azure-samples",
    "microsoft",
]

# Initialize the CosmosDB service
cosmos_db_service = CosmosDBService()

# Initialize the embedding service
embedding_service = EmbeddingService()


class RepositoryInfo:
    """Data class to hold repository information"""

    def __init__(self, id: str, organization: str, name: str, url: str, description: Optional[str],
                 created_at: str, updated_at: str, stars_count: int, archived: bool,
                 readme_content: Optional[str] = None, embeddings: Optional[List[float]] = None):
        self.id = id  # Unique identifier for the repository
        self.organization = organization
        self.name = name
        self.url = url
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at
        self.stars_count = stars_count
        self.archived = archived
        self.readme_content = readme_content
        self.embeddings = embeddings

    def to_dict(self) -> Dict:
        """Convert the repository info to a dictionary for saving to CosmosDB"""
        return {
            "id": self.id,
            "organization": self.organization,
            "name": self.name,
            "url": self.url,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "stars_count": self.stars_count,
            "archived": self.archived,
            "readme_content": self.readme_content,
            "embeddings": self.embeddings if self.embeddings else []
        }


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

        while total_repos == 0:  # Limit to 100 repositories per organization
            url = f"https://api.github.com/orgs/{organization}/repos?type=public&per_page={page_size}&page={page}"
            async with session.get(url, headers=headers) as response:
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
                            url=repo['html_url'],
                            description=repo['description'],
                            created_at=repo['created_at'],
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
        #"README", "readme"
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

    async with aiohttp.ClientSession() as session:
        for url in readme_urls:
            async with session.get(url) as response:
                if response.status == 200:
                    repo.readme_content = await response.text()
                    break  # Stop after first successful fetch
                
    if repo.readme_content is None:
        logger.warning(
            f"No README found for {repo.name} in {repo.organization}")
    return repo.readme_content or ""


async def process_repository(repo: RepositoryInfo) -> None:
    """Process a repository: fetch README, generate embeddings, and save to CosmosDB."""

    try:
        # Fetch README content for the repository
        readme_content = await fetch_readme_content(repo)
        repo.readme_content = readme_content

        # Generate embeddings for the repository
        embedding_context = f"""
            Repository: {repo.name}\n\n
            Description: {repo.description}\n\n
            README Content: {repo.readme_content}"""
        repo.embeddings = embedding_service.create_embedding(embedding_context)

        # Save repository to CosmosDB
        cosmos_db_service.upsert_item(
            item=repo.to_dict(),
            container_name='github-repos'
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
        f"{len(org_repos)} repositories processed for organization: {organization}")


async def main():
    """Main function to run the GitHub crawler"""

    # Initialize the crawler with environment variables
    storage_account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
    storage_account_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
    container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'github-repos')

    if not storage_account_name or not storage_account_key or not container_name:
        logger.error(
            "Please set AZURE_STORAGE_ACCOUNT_NAME and AZURE_STORAGE_ACCOUNT_KEY and AZURE_STORAGE_CONTAINER_NAME environment variables")
        return

    # Crawl each organization
    for org in github_organizations:
        await crawl_organization(org)


if __name__ == "__main__":
    asyncio.run(main())
