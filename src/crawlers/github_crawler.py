#!/usr/bin/env python3
"""
GitHub Repository Crawler for Azure Samples and Microsoft Repositories

This crawler fetches repository information from GitHub organizations
(azure-samples and microsoft) and saves detailed markdown reports to Azure Storage.

Features:
- Rate limiting and retry mechanisms
- Azure Storage account key authentication
- Comprehensive error handling and logging
- Parallel processing for improved performance
- Detailed repository information extraction
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import aiohttp
from dataclasses import dataclass
from azure.storage.blob.aio import BlobServiceClient
import backoff
from dotenv import load_dotenv

load_dotenv(override=True)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RepositoryInfo:
    """Data class to hold repository information"""
    name: str
    full_name: str
    description: Optional[str]
    html_url: str
    updated_at: str
    readme_content: Optional[str]
    owner: str


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors"""
    pass


class RateLimitError(Exception):
    """Custom exception for rate limiting"""
    pass


class GitHubCrawler:
    """
    GitHub repository crawler with Azure Storage integration
    
    This crawler fetches repositories from specified GitHub organizations,
    extracts detailed information, and saves markdown reports to Azure Storage.
    """
    
    def __init__(self, storage_account_name: str, storage_account_key: str, container_name: str = "github-repos"):
        """
        Initialize the GitHub crawler
        
        Args:
            storage_account_name: Azure Storage account name
            storage_account_key: Azure Storage account key
            container_name: Container name for storing markdown files
        """
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.storage_account_name = storage_account_name
        self.storage_account_key = storage_account_key
        self.container_name = container_name
        self.session: Optional[aiohttp.ClientSession] = None
        self.blob_service_client: Optional[BlobServiceClient] = None
        
        # Construct storage account URL
        self.storage_account_url = f"https://{storage_account_name}.blob.core.windows.net"
        
        # GitHub API configuration
        self.github_api_base = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Crawler/1.0"
        }
        
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"
            logger.info("GitHub token configured for authenticated requests")
        else:
            logger.warning("No GitHub token found. Rate limits will be lower.")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
    
    async def initialize(self):
        """Initialize HTTP session and Azure Storage client"""
        # Initialize HTTP session with connection pooling
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=10,
            keepalive_timeout=30
        )
        
        timeout = aiohttp.ClientTimeout(total=60, connect=10)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=self.headers
        )
        
        # Initialize Azure Storage client with account key
        try:
            self.blob_service_client = BlobServiceClient(
                account_url=self.storage_account_url,            
                credential=self.storage_account_key
            )
            logger.info("Azure Storage client initialized with account key")
        except Exception as e:
            logger.error(f"Failed to initialize Azure Storage client: {e}")
            raise
    
    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
        
        if self.blob_service_client:
            await self.blob_service_client.close()
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, RateLimitError),
        max_tries=5,
        max_time=300
    )
    async def make_github_request(self, url: str) -> Dict:
        """
        Make a request to GitHub API with retry logic
        
        Args:
            url: GitHub API URL
            
        Returns:
            JSON response data
            
        Raises:
            GitHubAPIError: For API errors
            RateLimitError: For rate limiting
        """
        try:
            async with self.session.get(url) as response:
                # Handle rate limiting
                if response.status == 403:
                    rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', '0')
                    if rate_limit_remaining == '0':
                        reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 3600))
                        wait_time = max(1, reset_time - int(time.time()))
                        logger.warning(f"Rate limit exceeded. Waiting {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
                        raise RateLimitError("Rate limit exceeded")
                
                if response.status == 404:
                    logger.warning(f"Resource not found: {url}")
                    return {}
                
                if response.status != 200:
                    error_text = await response.text()
                    raise GitHubAPIError(f"GitHub API error {response.status}: {error_text}")
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error for {url}: {e}")
            raise
    
    async def get_organization_repositories(self, org: str) -> List[Dict]:
        """
        Fetch all repositories for an organization
        
        Args:
            org: Organization name
            
        Returns:
            List of repository data
        """
        repositories = []
        page = 1
        per_page = 100
        
        logger.info(f"Fetching repositories for organization: {org}")
        
        while True:
            url = f"{self.github_api_base}/orgs/{org}/repos"
            params = {
                "page": page,
                "per_page": per_page,
                "sort": "updated",
                "direction": "desc"
            }
            
            # Add query parameters to URL
            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{param_str}"
            
            try:
                repos_data = await self.make_github_request(full_url)
                
                if not repos_data:
                    break
                
                repositories.extend(repos_data)
                logger.info(f"Fetched page {page} for {org}: {len(repos_data)} repositories")
                
                # If we got fewer repos than per_page, we're done
                if len(repos_data) < per_page:
                    break
                
                page += 1
                
                # Small delay between requests to be respectful
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error fetching repositories for {org} (page {page}): {e}")
                break
        
        logger.info(f"Total repositories found for {org}: {len(repositories)}")
        return repositories
    
    async def get_readme_content(self, owner: str, repo: str) -> Optional[str]:
        """
        Fetch README content for a repository
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            README content or None if not found
        """
        readme_urls = [
            f"{self.github_api_base}/repos/{owner}/{repo}/readme",
            f"{self.github_api_base}/repos/{owner}/{repo}/contents/README.md",
            f"{self.github_api_base}/repos/{owner}/{repo}/contents/readme.md"
        ]
        
        for url in readme_urls:
            try:
                readme_data = await self.make_github_request(url)
                if readme_data and 'content' in readme_data:
                    # Decode base64 content
                    import base64
                    content = base64.b64decode(readme_data['content']).decode('utf-8')
                    return content
            except Exception as e:
                logger.debug(f"Failed to fetch README from {url}: {e}")
                continue
        
        logger.warning(f"No README found for {owner}/{repo}")
        return None
    
    async def process_repository(self, repo_data: Dict, semaphore: asyncio.Semaphore) -> Optional[RepositoryInfo]:
        """
        Process a single repository and extract information
        
        Args:
            repo_data: Repository data from GitHub API
            semaphore: Semaphore for controlling concurrency
            
        Returns:
            RepositoryInfo object or None if processing failed
        """
        async with semaphore:
            try:
                owner = repo_data['owner']['login']
                name = repo_data['name']
                
                logger.info(f"Processing repository: {owner}/{name}")
                
                # Get README content
                readme_content = await self.get_readme_content(owner, name)
                
                return RepositoryInfo(
                    name=name,
                    full_name=repo_data['full_name'],
                    description=repo_data.get('description', ''),
                    html_url=repo_data['html_url'],
                    updated_at=repo_data['updated_at'],
                    readme_content=readme_content,
                    owner=owner
                )
                
            except Exception as e:
                logger.error(f"Error processing repository {repo_data.get('full_name', 'unknown')}: {e}")
                return None
    
    def create_markdown_content(self, repo_info: RepositoryInfo) -> str:
        """
        Create markdown content for a repository
        
        Args:
            repo_info: Repository information
            
        Returns:
            Formatted markdown content
        """
        markdown_content = f"""# {repo_info.name}

## Repository Information

- **Repository Name**: {repo_info.name}
- **Full Name**: {repo_info.full_name}
- **Repository Link**: [{repo_info.html_url}]({repo_info.html_url})
- **Description**: {repo_info.description or 'No description available'}
- **Last Update**: {repo_info.updated_at}
- **Owner**: {repo_info.owner}

## README Content

"""
        
        if repo_info.readme_content:
            markdown_content += repo_info.readme_content
        else:
            markdown_content += "No README content available for this repository."
        
        markdown_content += f"""

---
*Report generated on {datetime.utcnow().isoformat()}Z*
"""
        
        return markdown_content
    
    async def save_to_storage(self, filename: str, content: str) -> bool:
        """
        Save markdown content to Azure Storage
        
        Args:
            filename: Blob name
            content: Markdown content
            
        Returns:
            True if successful, False otherwise
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=filename
            )
            
            await blob_client.upload_blob(
                content,
                overwrite=True,
                content_type="text/markdown"
            )
            
            logger.info(f"Successfully saved {filename} to Azure Storage")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save {filename} to Azure Storage: {e}")
            return False
    
    async def crawl_organization(self, org: str) -> Tuple[int, int]:
        """
        Crawl all repositories for an organization
        
        Args:
            org: Organization name
            
        Returns:
            Tuple of (total_repos, successful_saves)
        """
        logger.info(f"Starting crawl for organization: {org}")
        
        # Get all repositories
        repositories = await self.get_organization_repositories(org)
        
        if not repositories:
            logger.warning(f"No repositories found for organization: {org}")
            return 0, 0
        
        # Process repositories with controlled concurrency
        semaphore = asyncio.Semaphore(10)  # Limit concurrent requests
        tasks = [
            self.process_repository(repo, semaphore)
            for repo in repositories
        ]
        
        # Process all repositories
        processed_repos = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Save to storage
        successful_saves = 0
        for repo_info in processed_repos:
            if isinstance(repo_info, RepositoryInfo):
                # Create filename based on organization and repository name
                filename = f"{org}--{repo_info.name}.md"
                markdown_content = self.create_markdown_content(repo_info)
                
                if await self.save_to_storage(filename, markdown_content):
                    successful_saves += 1
            elif isinstance(repo_info, Exception):
                logger.error(f"Repository processing failed: {repo_info}")
        
        logger.info(f"Completed crawl for {org}: {successful_saves}/{len(repositories)} repositories saved")
        return len(repositories), successful_saves
    
    async def run_crawler(self, organizations: List[str] = None) -> Dict[str, Tuple[int, int]]:
        """
        Run the crawler for specified organizations
        
        Args:
            organizations: List of organization names (defaults to azure-samples and microsoft)
            
        Returns:
            Dictionary with organization results
        """
        if organizations is None:
            organizations = ["azure-samples", "microsoft"]
        
        logger.info(f"Starting GitHub crawler for organizations: {organizations}")
        
        results = {}
        
        for org in organizations:
            try:
                total_repos, successful_saves = await self.crawl_organization(org)
                results[org] = (total_repos, successful_saves)
            except Exception as e:
                logger.error(f"Failed to crawl organization {org}: {e}")
                results[org] = (0, 0)
        
        return results


async def main():
    """
    Main function to run the GitHub crawler
    """
    # Configuration
    storage_account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
    storage_account_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
    
    if not storage_account_name:
        logger.error("AZURE_STORAGE_ACCOUNT_NAME environment variable is required")
        return
        
    if not storage_account_key:
        logger.error("AZURE_STORAGE_ACCOUNT_KEY environment variable is required")
        return
    
    container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'github-repos')
    
    # Run the crawler
    async with GitHubCrawler(storage_account_name, storage_account_key, container_name) as crawler:
        results = await crawler.run_crawler()
        
        # Print summary
        print("\n" + "="*50)
        print("GITHUB CRAWLER SUMMARY")
        print("="*50)
        
        total_repos = 0
        total_saved = 0
        
        for org, (repos, saved) in results.items():
            print(f"{org:20} | {repos:4} repos | {saved:4} saved")
            total_repos += repos
            total_saved += saved
        
        print("-"*50)
        print(f"{'TOTAL':20} | {total_repos:4} repos | {total_saved:4} saved")
        print("="*50)


if __name__ == "__main__":
    asyncio.run(main())