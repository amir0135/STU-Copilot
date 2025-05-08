param location string = resourceGroup().location
param name string
param tags object
param storageAccountId string
param keyVaultId string
param applicationInsightsId string
param containerRegistryId string
param aiServicesId string
param aiServicesTarget string
param aiSearchId string
param aiSearchTarget string

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
  }

  resource aiServicesConnection 'connections@2024-10-01' = {
    name: '${name}-connection-AzureOpenAI'
    properties: {
      category: 'AzureOpenAI'
      target: aiServicesTarget
      authType: 'ApiKey'
      isSharedToAll: true
      credentials: {
        key: '${listKeys(aiServicesId, '2024-10-01').key1}'
      }
      metadata: {
        ApiType: 'Azure'
        ResourceId: aiServicesId
      }
    }
  }  
}

resource aiSearchConnection 'Microsoft.MachineLearningServices/workspaces/connections@2025-01-01-preview' = {
  parent: aiHub
  name: '${name}-connection-AISearch'
  properties: {
    authType: 'ApiKey'
    category: 'CognitiveSearch'
    target: aiSearchTarget
    useWorkspaceManagedIdentity: false
    credentials: {
      key: '${listKeys(aiServicesId, '2024-10-01').key1}'
    }
    isSharedToAll: true
    sharedUserList: []
    peRequirement: 'NotRequired'
    peStatus: 'NotApplicable'
    metadata: {
      type: 'azure_ai_search'
      ApiType: 'Azure'
      ResourceId: aiSearchId
      ApiVersion: '2024-05-01-preview'
      DeploymentApiVersion: '2023-11-01'
    }
  }
}

output aiHubId string = aiHub.id
output aiHubName string = aiHub.name
