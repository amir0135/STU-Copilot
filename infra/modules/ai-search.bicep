param location string = resourceGroup().location
param name string
param tags object

resource aiSearch 'Microsoft.Search/searchServices@2025-02-01-preview' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: 'basic'
  }
  properties:{
    semanticSearch: 'free'    
    disableLocalAuth: false
    encryptionWithCmk: {
      enforcement: 'Unspecified'
    }
    endpoint: 'https://${name}.search.windows.net'
    networkRuleSet: {
      bypass: 'None'
    }
    replicaCount: 1
    partitionCount: 1
  }  
}

output aiSearchId string = aiSearch.id
output aiSearchTarget string = aiSearch.properties.endpoint
