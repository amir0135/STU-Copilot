from cosmos_db_service import CosmosDBService
from services.foundry_service import FoundryService
import logging
from dotenv import load_dotenv
import json

load_dotenv(override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_service = CosmosDBService()
foundry_service = FoundryService()
logger.info("CosmosDBService initialized successfully.")

search_terms = "ios app"

# search_embedding = foundry_service.generate_embedding(search_terms)
# print(search_embedding)

results = db_service.hybrid_search(search_terms=search_terms, container_name="github-repos", top_count=1)

#Show result items
# for item in list(results):
#     print(json.dumps(item, indent=2))

print(results)
