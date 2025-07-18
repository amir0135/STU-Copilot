import os
import logging
import time
import requests
from typing import List, Dict, Optional
from azure.cosmos import CosmosClient, ContainerProxy, CosmosDict
from openai import AzureOpenAI
from openai.types import CreateEmbeddingResponse
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

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


class RepositoryInfo:
    """Data class to hold repository information"""

    def __init__(self, id: str, organization: str, name: str, url: str,
                 updated_at: str, stars_count: int, archived: bool,
                 description: Optional[str] = None, keywords: Optional[str] = None,
                 embedding: Optional[float] = None):
        self.id = id  # Unique identifier for the repository
        self.organization = organization
        self.name = name
        self.url = url
        self.description = description
        self.keywords = keywords
        self.updated_at = updated_at
        self.stars_count = stars_count
        self.archived = archived
        self.embedding = embedding

    def to_dict(self) -> Dict:
        """Convert the repository info to a dictionary for saving to CosmosDB"""
        return {
            "id": self.id,
            "organization": self.organization,
            "name": self.name,
            "url": self.url,
            "description": self.description,
            "keywords": self.keywords,
            "updated_at": self.updated_at,
            "stars_count": self.stars_count,
            "archived": self.archived,
            "embedding": self.embedding
        }

    @staticmethod
    def from_dict(data: Dict) -> 'RepositoryInfo':
        """Create a RepositoryInfo instance from a dictionary"""
        return RepositoryInfo(
            id=data.get("id"),
            organization=data.get("organization"),
            name=data.get("name"),
            url=data.get("url"),
            description=data.get("description"),
            keywords=data.get("keywords"),
            updated_at=data.get("updated_at"),
            stars_count=data.get("stars_count", 0),
            archived=data.get("archived", False),
            embedding=data.get("embedding")
        )


class CosmosDBService:
    """Service to interact with Azure CosmosDB"""

    def __init__(self, ):

        endpoint = os.environ.get('COSMOSDB_ENDPOINT')
        key = os.environ.get('COSMOSDB_KEY')
        database_name = os.environ.get('COSMOSDB_DATABASE')
        if not endpoint or not key or not database_name:
            raise EnvironmentError(
                "CosmosDB credentials are not set in environment variables.")
        self.client = CosmosClient(endpoint, key)
        self.database = self.client.get_database_client(database_name)

    def get_container(self, container_name: str) -> ContainerProxy:
        return self.database.get_container_client(container_name)

    def upsert_item(self, item: dict) -> CosmosDict:
        container = self.get_container(cosmosdb_container_name)
        return container.upsert_item(body=item)


class FoundryService:
    """Service to handle text embeddings using Azure OpenAI."""

    def __init__(self):
        self.endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
        self.api_key = os.environ.get('AI_FOUNDRY_KEY')
        self.embedding_model = "text-embedding-3-small"
        self.chat_model = "gpt-4.1-nano"
        self.api_version = "2024-12-01-preview"

        if not self.endpoint or not self.api_key:
            raise EnvironmentError(
                "Azure OpenAI credentials are not set in environment variables.")

        self.embedding_client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            azure_deployment=self.embedding_model,
            api_version=self.api_version,
            api_key=self.api_key
        )

        self.chat_client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            azure_deployment=self.chat_model,
            api_version=self.api_version,
            api_key=self.api_key
        )

    def generate_embedding(self, text: str) -> list:
        """Get the embedding for a given text."""
        if not text:
            return []

        response: CreateEmbeddingResponse = self.embedding_client.embeddings.create(
            input=text,
            model=self.embedding_model,
            encoding_format="float",
            dimensions=1536,
        )
        return response.data[0].embedding if response.data else []

    def summarize_and_generate_keywords(self, text: str) -> tuple:
        """Summarize the given text using a GPT model and extract keywords.

        Args:
            text (str): The text to summarize and extract keywords from

        Returns:
            tuple: (summary, keywords) where summary is the summarized text and 
                  keywords is a comma-separated string of keywords
        """
        if not text:
            return ("", "")

        try:
            response = self.chat_client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {
                        "role": "system",
                        "content": """
                            Your task is to process the following text in two steps:
                            
                            1. Summarize the text into less than 2000 characters, keeping words as similar as possible to the original text.
                               - Remove code blocks, markdown formatting, and unnecessary whitespace
                               - Do not include explanations or comments
                            
                            2. Extract exactly 5 keywords that best represent the main topics from the content.
                            
                            IMPORTANT: You must respond ONLY with a valid JSON object using this exact format:
                            {
                                "summary": "<your summarized text>",
                                "keywords": "<five keywords separated by commas>"
                            }
                            
                            Do not include any text before or after the JSON object. No markdown formatting, no code blocks, no explanations.
                        """
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                max_tokens=4096,
                timeout=30  # Add timeout for better reliability
            )

            # Extract content from response
            content = response.choices[0].message.content if response.choices else ''

            # Default values in case parsing fails
            summary = content
            keywords = ""

            # Try to parse as JSON if content looks like JSON
            if content and content.strip():
                # Strip any potential non-JSON leading/trailing characters
                content_stripped = content.strip()
                json_start = content_stripped.find('{')
                json_end = content_stripped.rfind('}')

                if json_start >= 0 and json_end > json_start:
                    try:
                        json_content = content_stripped[json_start:json_end+1]
                        data = json.loads(json_content)
                        summary = data.get("summary", "")
                        keywords = data.get("keywords", "")
                        if not summary and not keywords:
                            logger.warning(
                                "JSON parsed but missing expected fields")
                    except json.JSONDecodeError as e:
                        logger.warning(
                            f"Failed to parse model response as JSON: {e}")
                else:
                    logger.warning(
                        "Model response does not contain valid JSON structure")
            elif not content:
                logger.warning("Model response is empty.")
            else:
                logger.warning("Model response is not in expected JSON format")

            return summary, keywords

        except Exception as e:
            logger.error(f"Error during text summarization: {e}")
            return ("", "")


class GitHubCrawler:
    """GitHub Crawler to fetch repositories and their README files."""

    def __init__(self):
        """Initialize the GitHub Crawler."""
        self.cosmos_db_service = CosmosDBService()
        self.foundry_service = FoundryService()

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
            summary, keywords = self.foundry_service.summarize_and_generate_keywords(
                context)
            repo.description = summary
            repo.keywords = keywords

            # Generate embedding for the repository
            repo.embedding = self.foundry_service.generate_embedding(summary)

            # Save repository to CosmosDB
            self.cosmos_db_service.upsert_item(
                item=repo.to_dict()
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
