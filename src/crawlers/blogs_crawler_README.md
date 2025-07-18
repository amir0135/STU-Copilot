# BlogsCrawler

The BlogsCrawler module is designed to process blog post data and store them in Azure CosmosDB with embeddings for semantic search. This is a simplified version that does not fetch content from external URLs.

## Features

- **Blog Item Processing**: Processes `BlogItem` objects and generates embeddings
- **Content Processing**: Handles blog post content and metadata
- **Embedding Generation**: Creates vector embeddings for semantic search using Azure AI Foundry
- **CosmosDB Storage**: Stores blog posts with metadata in Azure CosmosDB
- **Error Handling**: Robust error handling for processing and storage operations

## Data Model

The `BlogItem` class represents a blog post with the following fields:

- `id`: Unique identifier 
- `title`: Blog post title
- `url`: Link to the original blog post
- `description`: Clean text summary/description
- `content`: Full text content
- `author`: Author name
- `tags`: Comma-separated tags
- `published_date`: ISO format publication date
- `embedding`: Vector embedding for semantic search

## Usage

### Standalone Usage

```python
from blogs_crawler import BlogsCrawler
from cosmos_db_service import CosmosDBService
from foundry_service import FoundryService
from data_models import BlogItem

# Initialize services
cosmos_db_service = CosmosDBService()
foundry_service = FoundryService()

# Create crawler
crawler = BlogsCrawler(cosmos_db_service, foundry_service)

# Create blog items (from your data source)
blog_items = [
    BlogItem(
        id="example-1",
        title="Sample Blog Post",
        url="https://example.com/blog/sample",
        published_date="2025-01-18T10:00:00",
        description="A sample blog post description",
        content="Full blog post content...",
        author="Author Name",
        tags="tag1, tag2"
    )
]

# Process blog items
crawler.process_blog_items(blog_items)
```

### Azure Functions Integration

The BlogsCrawler is integrated into the Azure Functions app and runs automatically every 6 hours:

```python
@app.timer_trigger(schedule="0 0 */6 * * *")  # Every 6 hours
def blogs_crawler_func(timer_request: func.TimerRequest) -> None:
    # Crawler logic here
```

### Testing

Use the test script to verify functionality without Azure services:

```bash
python test_blogs_crawler.py
```

## Configuration

### Environment Variables

Required environment variables for Azure services:

- `COSMOSDB_ENDPOINT`: Azure CosmosDB endpoint URL
- `COSMOSDB_KEY`: Azure CosmosDB access key
- `COSMOSDB_DATABASE`: CosmosDB database name

## Dependencies

- `azure-cosmos`: CosmosDB integration
- `hashlib`: ID generation (built-in)

## Storage Container

Blog posts are stored in the CosmosDB container named `blog-posts`.

## Rate Limiting

The crawler includes built-in rate limiting with 100ms delay between processing items.

## Error Handling

- Content processing failures
- CosmosDB connection issues
- Embedding generation errors

## Methods

### `process_blog_item(blog_item: BlogItem)`

Processes a single blog item:
- Generates embeddings for the content
- Saves to CosmosDB

### `process_blog_items(blog_items: List[BlogItem])`

Processes a list of blog items with rate limiting.

### `generate_blog_id(url: str, published_date: str)`

Generates a unique MD5 hash ID based on URL and published date.

## Future Enhancements

- Batch processing optimizations
- Content deduplication
- Advanced content filtering
- Configurable processing schedules
