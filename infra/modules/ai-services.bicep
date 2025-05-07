param location string = resourceGroup().location
param name string
param tags object

resource aiServices 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: 'S0'
  }
  kind: 'AIServices' // or 'OpenAI'
  properties: {
    publicNetworkAccess: 'Enabled'
  }
}

output aiServicesId string = aiServices.id
output aiServicesTarget string = aiServices.properties.endpoint
