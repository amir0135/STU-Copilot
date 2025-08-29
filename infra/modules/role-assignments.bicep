param managedIdentityPrincipalId string
param storageAccountName string
param containerRegistryName string = ''

// Storage Account reference
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: storageAccountName
}

// Container Registry reference (optional)
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2025-04-01' existing = if (!empty(containerRegistryName)) {
  name: containerRegistryName
}

// Storage Blob Data Contributor role assignment for managed identity
resource storageBlobDataContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, managedIdentityPrincipalId, 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// Storage Blob Data Owner role assignment for managed identity
resource storageBlobDataOwnerRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, managedIdentityPrincipalId, 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b')
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b')
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// Storage Queue Data Contributor role assignment for managed identity
resource storageQueueDataContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, managedIdentityPrincipalId, '974c5e8b-45b9-4653-ba55-5f855dd0fb88')
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '974c5e8b-45b9-4653-ba55-5f855dd0fb88')
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// Storage Table Data Contributor role assignment for managed identity
resource storageTableDataContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, managedIdentityPrincipalId, '0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3')
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3')
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// Storage File Data SMB Share Contributor role assignment for managed identity (needed for Function Apps)
resource storageFileDataSMBShareContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, managedIdentityPrincipalId, '0c867c2a-1d8c-454a-a3db-ab2ea1bdc8bb')
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '0c867c2a-1d8c-454a-a3db-ab2ea1bdc8bb')
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// ACR Pull role assignment for managed identity (if container registry is provided)
resource acrPullRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(containerRegistryName)) {
  name: guid(containerRegistry.id, managedIdentityPrincipalId, '7f951dda-4ed3-4680-a7ca-43fe172d538d')
  scope: containerRegistry
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// Monitoring Metrics Publisher role assignment for managed identity at resource group scope
resource monitoringMetricsPublisherRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, managedIdentityPrincipalId, '3913510d-42f4-4e42-8a64-420c390055eb')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '3913510d-42f4-4e42-8a64-420c390055eb')
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}
