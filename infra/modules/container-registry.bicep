param location string = resourceGroup().location
param name string
param tags object

@allowed([
  'Basic'
  'Standard'
  'Premium'
])
param skuName string = 'Premium'

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2025-04-01' = {
  name: replace(name, '-', '')
  location: location
  tags: tags
  sku: {
    name: skuName
  }
  properties: {
    adminUserEnabled: true
    dataEndpointEnabled: false
    networkRuleBypassOptions: 'AzureServices'
    networkRuleSet: {
      defaultAction: 'Deny'
    }
    policies: {
      quarantinePolicy: {
        status: 'enabled'
      }
      retentionPolicy: {
        status: 'enabled'
        days: 7
      }
      trustPolicy: {
        status: 'disabled'
        type: 'Notary'
      }
    }
    publicNetworkAccess: 'Disabled'
    zoneRedundancy: 'Disabled'
    encryption: {
      status: 'disabled'
    }
  }
}

output containerRegistryId string = containerRegistry.id
output containerRegistryName string = containerRegistry.name
