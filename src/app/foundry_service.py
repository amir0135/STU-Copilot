import os
import logging
from openai import AzureOpenAI
from openai.types import CreateEmbeddingResponse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


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
