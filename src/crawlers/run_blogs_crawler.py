"""
Example usage of simplified BlogsCrawler with Azure services
This script demonstrates how to use the BlogsCrawler to process blog items.
"""

import os
import logging
from blogs_crawler import BlogsCrawler
from cosmos_db_service import CosmosDBService
from foundry_service import FoundryService
from data_models import BlogItem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_blog_items():
    """Create some sample blog items for testing"""
    return [
        BlogItem(
            id="sample-1",
            title="Getting Started with Azure Functions",
            url="https://example.com/blog/azure-functions",
            published_date="2025-01-18T10:00:00",
            description="Learn how to build serverless applications with Azure Functions.",
            content="Azure Functions is a serverless compute service that lets you run event-triggered code without having to explicitly provision or manage infrastructure...",
            author="Microsoft Developer",
            tags="azure, functions, serverless"
        ),
        BlogItem(
            id="sample-2", 
            title="Building Modern Web Apps with Next.js",
            url="https://example.com/blog/nextjs-guide",
            published_date="2025-01-18T11:00:00",
            description="A comprehensive guide to building modern web applications.",
            content="Next.js is a React framework that provides production-ready features like server-side rendering, API routes, and automatic code splitting...",
            author="Web Developer",
            tags="nextjs, react, web development"
        )
    ]

def main():
    """Main function to run the simplified BlogsCrawler with Azure services"""
    
    try:
        # Check environment variables
        required_env_vars = [
            'COSMOSDB_ENDPOINT',
            'COSMOSDB_KEY', 
            'COSMOSDB_DATABASE'
        ]
        
        missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            logger.info("Please set the following environment variables:")
            for var in missing_vars:
                logger.info(f"  - {var}")
            return
        
        # Initialize services
        logger.info("Initializing Azure services...")
        cosmos_db_service = CosmosDBService()
        foundry_service = FoundryService()
        
        # Initialize BlogsCrawler
        logger.info("Initializing BlogsCrawler...")
        blogs_crawler = BlogsCrawler(
            cosmos_db_service=cosmos_db_service,
            foundry_service=foundry_service
        )
        
        # Create sample blog items (in a real scenario, these would come from another source)
        sample_blog_items = create_sample_blog_items()
        
        # Process the blog items
        logger.info(f"Processing {len(sample_blog_items)} blog items...")
        blogs_crawler.process_blog_items(sample_blog_items)
        
        logger.info("Blog items processing completed successfully!")
        
    except Exception as e:
        logger.error(f"Error running BlogsCrawler: {e}")
        raise

if __name__ == "__main__":
    main()
