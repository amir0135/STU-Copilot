param location string = resourceGroup().location
param name string
param tags object
param databaseName string = 'stu-copilot-db'
param chatsContainerName string = 'chats'
param totalThroughputLimit int = 400

resource cosmosDB 'Microsoft.DocumentDB/databaseAccounts@2024-12-01-preview' = {
  name: name
  location: location
  tags: tags
  kind: 'GlobalDocumentDB'
  identity: {
    type: 'None'
  }
  properties: {
    publicNetworkAccess: 'Enabled'
    enableAutomaticFailover: true
    enableMultipleWriteLocations: false
    isVirtualNetworkFilterEnabled: false
    virtualNetworkRules: []
    disableKeyBasedMetadataWriteAccess: false
    enableFreeTier: false
    enableAnalyticalStorage: false
    analyticalStorageConfiguration: {
      schemaType: 'WellDefined'
    }
    databaseAccountOfferType: 'Standard'
    enableMaterializedViews: false
    capacityMode: 'Serverless'
    networkAclBypass: 'None'
    disableLocalAuth: false
    enablePartitionMerge: false
    enablePerRegionPerPartitionAutoscale: false
    enableBurstCapacity: false
    enablePriorityBasedExecution: false
    defaultPriorityLevel: 'High'
    minimalTlsVersion: 'Tls12'
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
      maxIntervalInSeconds: 5
      maxStalenessPrefix: 100
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    cors: []
    capabilities: []
    ipRules: []
    backupPolicy: {
      type: 'Periodic'
      periodicModeProperties: {
        backupIntervalInMinutes: 240
        backupRetentionIntervalInHours: 8
        backupStorageRedundancy: 'Local'
      }
    }
    networkAclBypassResourceIds: []
    diagnosticLogSettings: {
      enableFullTextQuery: 'None'
    }
    capacity: {
      totalThroughputLimit: totalThroughputLimit
    }
  }

  resource sqlDatabase 'sqlDatabases@2024-12-01-preview' = {
    name: databaseName
    properties: {
      resource: {
        id: databaseName
      }
    }

    resource chatsContainer 'containers@2024-12-01-preview' = {
      name: chatsContainerName
      properties: {
        resource: {
          id: chatsContainerName
          indexingPolicy: {
            indexingMode: 'consistent'
            automatic: true
            includedPaths: [
              {
                path: '/*'
              }
            ]
            excludedPaths: [
              {
                path: '/"_etag"/?'
              }
            ]
          }
          partitionKey: {
            paths: [
              '/Id'
              '/ThreadId'
              '/UserId'
            ]
            kind: 'MultiHash'
            version: 2
          }
          uniqueKeyPolicy: {
            uniqueKeys: []
          }
          conflictResolutionPolicy: {
            mode: 'LastWriterWins'
            conflictResolutionPath: '/_ts'
          }
          computedProperties: []
        }
      }
    }
  }
}

output cosmosDBId string = cosmosDB.id
output cosmosDBName string = cosmosDB.name
output cosmosDBDocumentEndpoint string = cosmosDB.properties.documentEndpoint
