targetScope = 'subscription'

@description('The location to deploy the resources.')
param location string = 'swedencentral'

@description('The name of the environment.')
param environmentName string = 'dev'

@description('The name of the prefix to use for the resources.')
param prefix string = 'stu-copilot'

@description('Tags to apply to the resources.')
param tags object = {
  Environment: environmentName
}

@description('The name of the resource group.')
var resourceGroupName = 'rg-${environmentName}-${prefix}'

resource resourceGroup 'Microsoft.Resources/resourceGroups@2025-03-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

module logAnalytics 'modules/log-analytics.bicep' = {
  name: 'logAnalytics'
  scope: resourceGroup
  params: {
    name: 'log-${environmentName}-${prefix}'
    tags: tags
  }
}

module applicationInsights 'modules/application-insights.bicep' = {
  name: 'applicationInsights'
  scope: resourceGroup
  params: {
    name: 'appi-${environmentName}-${prefix}'
    logAnalyticsId: logAnalytics.outputs.logAnalyticsId
    tags: tags
  }
}

module storageAccount 'modules/storage-account.bicep' = {
  name: 'storageAccount'
  scope: resourceGroup
  params: {
    name: 'st${environmentName}${prefix}'
    tags: tags
  }
}

module keyVault 'modules/key-vault.bicep' = {
  name: 'keyVault'
  scope: resourceGroup
  params: {
    name: 'kv-${environmentName}-${prefix}'
    tags: tags
  }
}

module containerRegistry 'modules/container-registry.bicep' = {
  name: 'containerRegistry'
  scope: resourceGroup
  params: {
    name: 'acr${environmentName}${prefix}'
    tags: tags
  }
}

module aiServices 'modules/ai-services.bicep' = {
  name: 'aiServices'
  scope: resourceGroup
  params: {
    name: 'ais-${environmentName}-${prefix}'
    tags: tags
  }
}

module aiSearch 'modules/ai-search.bicep' = {
  name: 'aiSearch'
  scope: resourceGroup
  params: {
    name: 'srch-${environmentName}-${prefix}'
    tags: tags
  }
}
