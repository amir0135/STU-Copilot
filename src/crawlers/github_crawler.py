
import logging
import time
import requests
from typing import List
from data_models import RepositoryInfo
from cosmos_db_service import CosmosDBService
from foundry_service import FoundryService


# Configure logging
logging.getLogger().setLevel(logging.INFO)
# logging.getLogger("azure").setLevel(logging.WARNING)
# logging.getLogger("httpx").setLevel(logging.WARNING)
# logging.getLogger("azure.cosmos").setLevel(logging.WARNING)
logger = logging.getLogger("azure.functions")

# Organizations to crawl
github_organizations = [
    "Azure-Samples",
    "Microsoft",
    "AzureCosmosDB",
    "Azure"
]

# CosmosDB configuration
cosmosdb_container_name = "github-repos"


class GitHubCrawler:
    """GitHub Crawler to fetch repositories and their README files."""

    def __init__(self,
                 cosmos_db_service: CosmosDBService,
                 foundry_service: FoundryService):
        """Initialize the GitHub Crawler."""
        self.cosmos_db_service = cosmos_db_service
        self.foundry_service = foundry_service

    def fetch_org_repositories(self, organization: str) -> List[RepositoryInfo]:
        """Fetch repositories for a given organization from GitHub API in a paginated manner."""

        logger.info(f"Fetching repositories for organization: {organization}")

        # Fetch repositories for the organization in paginated manner
        page = 1
        page_size = 10  # Increased page size for efficiency
        org_repos: List[RepositoryInfo] = []

        headers = {
            'User-Agent': 'GitHubCrawler/1.0',
            'Accept': 'application/vnd.github.v3+json',
        }

        while page == 1:  # Pagination loop
            url = f"https://api.github.com/orgs/{organization}/repos?type=public&per_page={page_size}&page={page}"
            response = requests.get(url, headers=headers)

            if response.status_code == 403:
                # Check for rate limit
                remaining = response.headers.get("X-RateLimit-Remaining")
                reset = response.headers.get("X-RateLimit-Reset")
                if remaining == "0" and reset:
                    reset_time = int(reset)
                    wait_seconds = max(reset_time - int(time.time()), 1)
                    logger.warning(
                        f"Rate limit reached for {organization}. Waiting {wait_seconds} seconds before retrying."
                    )
                    time.sleep(wait_seconds)
                    continue  # Retry the same page after sleeping
                else:
                    logger.error(
                        f"Failed to fetch repositories for {organization}: {response.status_code} (possibly forbidden)"
                    )
                    break

            if response.status_code != 200:
                logger.error(
                    f"Failed to fetch repositories for {organization}: {response.status_code}")
                break

            repos = response.json()
            if not repos:
                break

            for repo in repos:
                repo_info = RepositoryInfo(
                    id=str(repo['id']),
                    organization=organization,
                    name=repo['name'],
                    # Handle None description
                    description=repo.get("description", ""),
                    url=repo['html_url'],
                    updated_at=repo['updated_at'],
                    stars_count=repo['stargazers_count'],
                    archived=repo['archived']
                )
                org_repos.append(repo_info)

            logger.info(
                f"Fetched {len(repos)} repositories from {organization} (Page {page})")

            page += 1
            time.sleep(0.1)  # Rate limiting

            # If we got fewer repos than the page size, we've reached the end
            if len(repos) < page_size:
                break

        return org_repos

    def generate_readme_urls(self, repo: RepositoryInfo) -> list:
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

    def fetch_readme_content(self, repo: RepositoryInfo) -> str:
        """Fetch README content for a repository"""

        readme_urls = self.generate_readme_urls(repo)
        readme_content = None

        headers = {
            'User-Agent': 'GitHubCrawler/1.0'
        }

        for url in readme_urls:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                readme_content = response.text
                break  # Stop after first successful fetch

        if readme_content is None:
            logger.warning(
                f"No README found for {repo.name} in {repo.organization}")
        return readme_content or ""

    def process_repository(self, repo: RepositoryInfo) -> None:
        """Process a repository: fetch README, generate embeddings, and save to CosmosDB."""

        try:
            # Fetch README content for the repository
            readme_content = self.fetch_readme_content(repo)

            # Generate description for the repository
            context = f"{repo.description}\n\n{readme_content}"
            summary, tags = self.foundry_service.summarize_and_generate_tags(
                context)
            repo.description = summary
            repo.tags = tags

            # Generate embedding for the repository
            repo.embedding = self.foundry_service.generate_embedding(summary)

            # Save repository to CosmosDB
            self.cosmos_db_service.upsert_item(
                item=repo.to_dict(),
                container_name=cosmosdb_container_name
            )

        except Exception as e:
            logger.error(
                f"Error processing repository {repo.organization}/{repo.name}: {e}")

    def crawl_organization(self, organization: str) -> None:
        """Main function to crawl an organization and save repositories to CosmosDB."""

        logger.info(f"Starting crawl for organization: {organization}")

        # Fetch repositories for the organization
        org_repos = self.fetch_org_repositories(organization)
        if not org_repos:
            logger.info(
                f"No repositories found for organization: {organization}")
            return

        logger.info(
            f"Total repositories fetched for {organization}: {len(org_repos)}")

        for repo in org_repos:
            self.process_repository(repo)
            time.sleep(0.1)  # Rate limiting

        logger.info(
            f"Finished processing {len(org_repos)} repositories for organization: {organization}")

    def run(self):
        """Main function to run the GitHub crawler"""
        logger.info("GitHub crawler started.")

        # Crawl each organization
        for org in github_organizations:
            self.crawl_organization(org)

        logger.info("GitHub crawler finished.")
