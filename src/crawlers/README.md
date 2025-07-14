# Crawlers

This folder contains Python scripts for crawling GitHub repositories and processing their data using Azure services.

## Components

- **github_crawler.py**: Main script to fetch repositories from specified GitHub organizations, retrieve README files, generate embeddings using Azure OpenAI, and store results in Azure CosmosDB.
- **cosmos_db_service.py**: Service for interacting with Azure CosmosDB.
- **embedding_service.py**: Service for generating text embeddings and summaries using Azure OpenAI.

## Prerequisites

- Python 3.8+
- Azure account with CosmosDB and OpenAI resources
- GitHub API access
- Environment variables set for Azure and GitHub credentials (see below)

## Environment Variables

Copy the `.env.example` file to `.env` and fill in your credentials:

```
cp .env.example .env
```

Edit the `.env` file with your values. The required variables are:

```
COSMOSDB_ENDPOINT="https://your-cosmosdb-instance-name.documents.azure.com:443/"
COSMOSDB_KEY="your_cosmosdb_key_here"
COSMOSDB_DATABASE="your_database_name_here"
AZURE_OPENAI_ENDPOINT="https://your-openai-endpoint.openai.azure.com/"
AZURE_OPENAI_API_KEY="your_openai_api_key_here"
```

> **Note:** Ensure the variable names match those used in the code (e.g., `AZURE_OPENAI_ENDPOINT`, not `Azure_OPENAI_ENDPOINT`).

## Usage

Run the GitHub crawler:

```
python github_crawler.py
```

## Notes
- The crawler fetches repositories for organizations listed in `github_crawler.py`.
- Embeddings are generated for repository descriptions and README content.
- Data is stored in the specified CosmosDB container.
- See `.env.example` for a template of required environment variables.
