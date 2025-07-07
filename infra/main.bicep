targetScope = 'subscription'

@description('The location to deploy the resources.')
param location string = 'swedencentral'

@description('The name of the environment.')
param environmentName string = 'dev'

@description('The name of the postfix to use for the resources.')
param postfix string = 'stu-copilot'

@description('Tags to apply to the resources.')
param tags object = {
  Environment: environmentName
}

@description('The name of the resource group.')
var resourceGroupName = 'rg-${environmentName}-${postfix}'

resource resourceGroup 'Microsoft.Resources/resourceGroups@2025-03-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

module logAnalytics 'modules/log-analytics.bicep' = {
  name: 'logAnalytics'
  scope: resourceGroup
  params: {
    name: 'log-${environmentName}-${postfix}'
    tags: tags
  }
}

module applicationInsights 'modules/application-insights.bicep' = {
  name: 'applicationInsights'
  scope: resourceGroup
  params: {
    name: 'appi-${environmentName}-${postfix}'
    logAnalyticsId: logAnalytics.outputs.logAnalyticsId
    tags: tags
  }
}

module storageAccount 'modules/storage-account.bicep' = {
  name: 'storageAccount'
  scope: resourceGroup
  params: {
    name: 'st${environmentName}${postfix}'
    tags: tags
  }
}

module keyVault 'modules/key-vault.bicep' = {
  name: 'keyVault'
  scope: resourceGroup
  params: {
    name: 'kv-${environmentName}-${postfix}'
    tags: tags
  }
}

// module containerRegistry 'modules/container-registry.bicep' = {
//   name: 'containerRegistry'
//   scope: resourceGroup
//   params: {
//     name: 'acr${environmentName}${postfix}'
//     tags: tags
//   }
// }

module aiSearch 'modules/ai-search.bicep' = {
  name: 'aiSearch'
  scope: resourceGroup
  params: {
    name: 'srch-${environmentName}-${postfix}'
    tags: tags
  }
}
module cosmosDB 'modules/cosmos-db.bicep' = {
  name: 'cosmosDB'
  scope: resourceGroup
  params: {
    name: 'cosmos-${environmentName}-${postfix}'
    tags: tags
  }
}

module aiFoundry 'modules/ai-foundry.bicep' = {
  name: 'aiFoundry'
  scope: resourceGroup
  params: {
    name: 'aif-${environmentName}-${postfix}'
    projectName: 'proj-${environmentName}-${postfix}'
    tags: tags
  }
}

output resourceGroupId string = resourceGroup.id
output resourceGroupName string = resourceGroup.name
output logAnalyticsId string = logAnalytics.outputs.logAnalyticsId
output logAnalyticsName string = logAnalytics.outputs.logAnalyticsName
output applicationInsightsId string = applicationInsights.outputs.applicationInsightsId
output applicationInsightsName string = applicationInsights.outputs.applicationInsightsName
output storageAccountId string = storageAccount.outputs.storageAccountId
output storageAccountName string = storageAccount.outputs.storageAccountName
output keyVaultId string = keyVault.outputs.keyVaultId
output keyVaultName string = keyVault.outputs.keyVaultName
//output containerRegistryId string = containerRegistry.outputs.containerRegistryId
//output containerRegistryName string = containerRegistry.outputs.containerRegistryName
output aiSearchId string = aiSearch.outputs.aiSearchId
output aiSearchName string = aiSearch.outputs.aiSearchName
output cosmosDBId string = cosmosDB.outputs.cosmosDBId
output cosmosDBName string = cosmosDB.outputs.cosmosDBName
output cosmosDBDocumentEndpoint string = cosmosDB.outputs.cosmosDBDocumentEndpoint
output aiFoundryId string = aiFoundry.outputs.aiFoundryId
output aiFoundryName string = aiFoundry.outputs.aiFoundryName
output aiFoundryEndpoint string = aiFoundry.outputs.aiFoundryEndpoint
output aiFoundryProjectId string = aiFoundry.outputs.aiFoundryProjectId
output aiFoundryProjectName string = aiFoundry.outputs.aiFoundryProjectName
