param location string = resourceGroup().location
param name string
param tags object
param databaseName string = 'stu-copilot-db'
param chatsContainerName string = 'chats'

resource cosmosDb 'Microsoft.DocumentDB/databaseAccounts@2024-12-01-preview' = {
  name: name
  location: location
  tags: tags
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
      maxStalenessPrefix: 100
      maxIntervalInSeconds: 5
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
      }
    ]
    capabilities: [
      {
        name: 'EnableServerless'
      }
    ]
  }

  resource sqlDatabase 'sqlDatabases@2024-12-01-preview' = {
    name: databaseName
    properties: {
      resource: {
        id: databaseName
      }
      options: {}
    }

    resource sqlContainer 'containers@2024-12-01-preview' = {
      name: chatsContainerName
      properties: {
        resource: {
          id: chatsContainerName
          partitionKey: {
            paths: ['/id']
            kind: 'Hash'
          }
        }
        options: {
          throughput: 50
        }
      }
    }
  }
}
