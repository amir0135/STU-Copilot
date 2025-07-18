import logging
import time
import hashlib
from typing import List
import feedparser
from data_models import BlogItem
from cosmos_db_service import CosmosDBService
from foundry_service import FoundryService
from datetime import datetime

# Configure logging
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger("azure.functions")

# CosmosDB configuration
cosmosdb_container_name = "blog-posts"

# Blog feed URLs
blog_feed_urls = [    
    "https://devblogs.microsoft.com/landing", # Microsoft Developer Blogs
    "https://news.microsoft.com/source/feed/", # Microsoft News
    "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/Community?interaction.style=blog&feeds.replies=false" # Microsoft Tech Community Blogs
]


class BlogsCrawler:
    """Blogs Crawler to process blog posts and store in CosmosDB."""

    def __init__(self,
                 cosmos_db_service: CosmosDBService,
                 foundry_service: FoundryService):
        """Initialize the Blogs Crawler."""
        self.cosmos_db_service = cosmos_db_service
        self.foundry_service = foundry_service

    def generate_blog_id(self, url: str, published_date: str) -> str:
        """Generate a unique ID for a blog post based on URL and published date."""
        content = f"{url}_{published_date}"
        return hashlib.md5(content.encode()).hexdigest()

    def process_blog_item(self, blog_item: BlogItem) -> None:
        """Process a blog item: generate embeddings and save to CosmosDB."""
        try:
            # Prepare content for embedding generation
            summary, tags = self.foundry_service.summarize_and_generate_tags(
                blog_item.description)
            blog_item.description = summary
            blog_item.tags = tags
            embedding_content = f"{blog_item.title}\n\n{blog_item.description}"

            # Generate embedding for the blog post
            blog_item.embedding = self.foundry_service.generate_embedding(
                embedding_content)

            # Save blog item to CosmosDB
            self.cosmos_db_service.upsert_item(
                item=blog_item.to_dict(),
                container_name=cosmosdb_container_name
            )

            logger.info(f"Successfully processed blog post: {blog_item.title}")

        except Exception as e:
            logger.error(
                f"Error processing blog item '{blog_item.title}': {e}")

    def process_blog_items(self, blog_items: List[BlogItem]) -> None:
        """Process a list of blog items."""
        logger.info(f"Processing {len(blog_items)} blog items")

        for blog_item in blog_items:
            try:
                # Check if the blog item already exists in CosmosDB
                if self.cosmos_db_service.check_item_exists(
                        item_id=blog_item.id,
                        container_name=cosmosdb_container_name):
                    logger.info(
                        f"Blog item already exists: {blog_item.title}")
                    continue

                # Process each blog item
                self.process_blog_item(blog_item)

                # Rate limiting
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error processing blog item: {e}")
                continue

        logger.info(f"Finished processing {len(blog_items)} blog items")

    def rss_feed_to_json(self, feed_url: str) -> List[BlogItem]:
        """Fetch RSS feed from the given URL and convert items to JSON serializable dicts."""
        logger.info(f"Fetching RSS feed: {feed_url}")
        feed = feedparser.parse(feed_url)
        items: List[BlogItem] = []
        for entry in feed.entries:
            published_date = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", entry.get("published_parsed", ""))

            description = entry.get("content")[0]["value"] if entry.get(
                "content") else entry.get("summary", "")

            id = self.generate_blog_id(
                url=entry.get("link", ""),
                published_date=published_date
            )

            blog_item = BlogItem(
                id=id,
                title=entry.get("title", ""),
                url=entry.get("link", ""),
                published_date=published_date,
                description=description
            )
            items.append(blog_item)

        logger.info(f"Fetched {len(items)} items from RSS feed.")
        return items

    def run(self):
        """Main function to run the Blogs crawler."""
        logger.info("Blogs crawler started.")

        for feed_url in blog_feed_urls:
            try:
                logger.info(f"Processing feed: {feed_url}")
                blog_items = self.rss_feed_to_json(feed_url)
                self.process_blog_items(blog_items)

            except Exception as e:
                logger.error(f"Error processing feed '{feed_url}': {e}")

        logger.info("Blogs crawler finished.")
