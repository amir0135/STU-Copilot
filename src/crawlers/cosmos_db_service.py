import os
from azure.cosmos import CosmosClient, PartitionKey, exceptions, ContainerProxy, CosmosDict
from azure.core.paging import ItemPaged
from typing import Dict, Any


class CosmosDBService:

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

    def create_item(self, item: dict, container_name: str) -> CosmosDict:
        container = self.get_container(container_name)
        return container.create_item(body=item)

    def upsert_item(self, item: dict, container_name: str) -> CosmosDict:
        container = self.get_container(container_name)
        return container.upsert_item(body=item)

    def read_item(self, item_id: str, partition_key: PartitionKey, container_name: str) -> CosmosDict:
        container = self.get_container(container_name)
        try:
            return container.read_item(item=item_id, partition_key=partition_key)
        except exceptions.CosmosResourceNotFoundError:
            return None

    def update_item(self, item_id: str, partition_key: PartitionKey, updated_fields: dict, container_name: str) -> CosmosDict:
        container = self.get_container(container_name)
        item = self.read_item(item_id, partition_key, container_name)
        if not item:
            return None
        item.update(updated_fields)
        return container.replace_item(item=item_id, body=item)

    def delete_item(self, item_id: str, partition_key: PartitionKey, container_name: str) -> bool:
        container = self.get_container(container_name)
        try:
            container.delete_item(item=item_id, partition_key=partition_key)
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False

    def query_items(self, query: str, container_name: str, parameters: list = None) -> ItemPaged[Dict[str, Any]]:
        container = self.get_container(container_name)
        return list(container.query_items(
            query=query,
            parameters=parameters or [],
            enable_cross_partition_query=True
        ))
