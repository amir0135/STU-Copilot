param location string = resourceGroup().location
param name string
param tags object

resource aiService 'Microsoft.Search/searchServices@2025-02-01-preview' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: 'basic'
  }
  properties:{
    semanticSearch: 'free'
    replicaCount: 1
    partitionCount: 1
  }  
}

output aiSearchId string = aiService.id
