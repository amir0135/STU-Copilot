param location string = resourceGroup().location
param name string
param tags object
param storageAccountId string
param keyVaultId string
param applicationInsightsId string
param containerRegistryId string
param aiServicesId string
param aiServicesTarget string
//param logAnalyticsId string

resource aiHub 'Microsoft.MachineLearningServices/workspaces@2025-01-01-preview' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  kind: 'hub'
  properties: {
    friendlyName: name
    description: 'AI Hub for ${name}'
    storageAccount: storageAccountId
    keyVault: keyVaultId
    applicationInsights: applicationInsightsId
    containerRegistry: containerRegistryId
    //workspaceId: logAnalyticsId
  }

  resource aiServicesConnection 'connections@2024-01-01-preview' = {
    name: '${name}-connection-AzureOpenAI'
    properties: {
      category: 'AzureOpenAI'
      target: aiServicesTarget
      authType: 'ApiKey'
      isSharedToAll: true
      credentials: {
        key: '${listKeys(aiServicesId, '2021-10-01').key1}'
      }
      metadata: {
        ApiType: 'Azure'
        ResourceId: aiServicesId
      }
    }
  }
}
