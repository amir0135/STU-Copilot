
import os
from azure.cosmos import CosmosClient, ContainerProxy, CosmosDict, exceptions

class CosmosDBService:
    """Service to interact with Azure CosmosDB"""

    def __init__(self):

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

    def upsert_item(self, item: dict, container_name: str) -> CosmosDict:
        container = self.get_container(container_name=container_name)
        return container.upsert_item(body=item)
    
    def check_item_exists(self, item_id: str, container_name: str) -> bool:
        container = self.get_container(container_name=container_name)
        try:
            container.read_item(item=item_id, partition_key=item_id)
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False
    