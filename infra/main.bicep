targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Resource group name')
param resourceGroupName string

@description('Tags to apply to all resources')
param tags object = {}

@description('Additional environment variables for stu-copilot-web')
param environment string = 'production'

@description('Additional environment variables for stu-copilot-crawlers')
param functionsExtensionVersion string = '~4'
param functionsWorkerRuntime string = 'python'

@secure()
@description('Azure AD OAuth Client ID for authentication')
param azureClientId string = ''

@secure()
@description('Azure AD OAuth Client Secret for authentication')
param azureClientSecret string = ''

// Resource token for unique naming
var resourceToken = toLower(uniqueString(subscription().id, location, environmentName))

// Resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: resourceGroupName
  location: location
  tags: union(tags, { 'azd-env-name': environmentName })
}

// Core infrastructure modules
module logAnalytics 'modules/log-analytics.bicep' = {
  name: 'logAnalytics'
  scope: rg
  params: {
    name: 'az-log-${resourceToken}'
    location: location
    tags: tags
  }
}

module applicationInsights 'modules/application-insights.bicep' = {
  name: 'applicationInsights'
  scope: rg
  params: {
    name: 'az-ai-${resourceToken}'
    location: location
    logAnalyticsId: logAnalytics.outputs.logAnalyticsId
    tags: tags
  }
}

module storageAccount 'modules/storage-account.bicep' = {
  name: 'storageAccount'
  scope: rg
  params: {
    name: 'azst${resourceToken}'
    location: location
    tags: tags
  }
}

module keyVault 'modules/key-vault.bicep' = {
  name: 'keyVault'
  scope: rg
  params: {
    name: 'az-kv-${resourceToken}'
    location: location
    tags: tags
  }
}

module containerRegistry 'modules/container-registry.bicep' = {
  name: 'containerRegistry'
  scope: rg
  params: {
    name: 'azcr${resourceToken}'
    location: location
    tags: tags
  }
}

module aiSearch 'modules/ai-search.bicep' = {
  name: 'aiSearch'
  scope: rg
  params: {
    name: 'az-srch-${resourceToken}'
    location: location
    tags: tags
  }
}

module cosmosDB 'modules/cosmos-db.bicep' = {
  name: 'cosmosDB'
  scope: rg
  params: {
    name: 'az-cosmos-${resourceToken}'
    location: location
    tags: tags
  }
}

module aiFoundry 'modules/ai-foundry.bicep' = {
  name: 'aiFoundry'
  scope: rg
  params: {
    name: 'az-aif-${resourceToken}'
    projectName: 'az-proj-${resourceToken}'
    location: location
    tags: tags
  }
}

// User-assigned managed identity
module managedIdentity 'modules/managed-identity.bicep' = {
  name: 'managedIdentity'
  scope: rg
  params: {
    name: 'az-id-${resourceToken}'
    location: location
    tags: tags
  }
}

// Key Vault access for managed identity
module keyVaultAccess 'modules/keyvault-access.bicep' = {
  name: 'keyVaultAccess'
  scope: rg
  params: {
    keyVaultName: keyVault.outputs.keyVaultName
    principalId: managedIdentity.outputs.managedIdentityPrincipalId
  }
}

// Container Apps Environment
module containerAppsEnvironment 'modules/container-apps-environment.bicep' = {
  name: 'containerAppsEnvironment'
  scope: rg
  params: {
    name: 'az-cae-${resourceToken}'
    location: location
    tags: tags
    logAnalyticsWorkspaceId: logAnalytics.outputs.logAnalyticsId
  }
}

// Container App for stu-copilot-web
module webContainerApp 'modules/container-app-web.bicep' = {
  name: 'webContainerApp'
  scope: rg
  params: {
    name: 'az-ca-${resourceToken}'
    location: location
    tags: tags
    containerAppsEnvironmentId: containerAppsEnvironment.outputs.containerAppsEnvironmentId
    containerRegistryLoginServer: containerRegistry.outputs.containerRegistryLoginServer
    managedIdentityId: managedIdentity.outputs.managedIdentityId
    environment: environment
    cosmosDbEndpoint: cosmosDB.outputs.cosmosDBDocumentEndpoint
    cosmosDbPrimaryKey: cosmosDB.outputs.cosmosDBPrimaryKey
    aiFoundryEndpoint: aiFoundry.outputs.aiFoundryEndpoint
    aiFoundryApiKey: aiFoundry.outputs.aiFoundryApiKey
    applicationInsightsConnectionString: applicationInsights.outputs.applicationInsightsConnectionString
    azureClientId: azureClientId
    azureClientSecret: azureClientSecret
  }
  dependsOn: [
    roleAssignments
  ]
}

// Function App for stu-copilot-crawlers
module functionApp 'modules/function-app.bicep' = {
  name: 'functionApp'
  scope: rg
  params: {
    name: 'az-func-${resourceToken}'
    location: location
    tags: tags
    managedIdentityId: managedIdentity.outputs.managedIdentityId
    storageAccountName: storageAccount.outputs.storageAccountName
    storageAccountKey: storageAccount.outputs.storageAccountKey
    functionsExtensionVersion: functionsExtensionVersion
    functionsWorkerRuntime: functionsWorkerRuntime
    applicationInsightsConnectionString: applicationInsights.outputs.applicationInsightsConnectionString
    cosmosDbEndpoint: cosmosDB.outputs.cosmosDBDocumentEndpoint
    cosmosDbPrimaryKey: cosmosDB.outputs.cosmosDBPrimaryKey
    aiFoundryEndpoint: aiFoundry.outputs.aiFoundryEndpoint
    aiFoundryApiKey: aiFoundry.outputs.aiFoundryApiKey
    logAnalyticsWorkspaceId: logAnalytics.outputs.logAnalyticsId
  }
  dependsOn: [
    roleAssignments
  ]
}

// Role assignments for managed identity
module roleAssignments 'modules/role-assignments.bicep' = {
  name: 'roleAssignments'
  scope: rg
  params: {
    managedIdentityPrincipalId: managedIdentity.outputs.managedIdentityPrincipalId
    storageAccountName: storageAccount.outputs.storageAccountName
    containerRegistryName: containerRegistry.outputs.containerRegistryName
  }
}

// Outputs
output RESOURCE_GROUP_ID string = rg.id
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.outputs.containerRegistryLoginServer
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_SUBSCRIPTION_ID string = subscription().subscriptionId
output AZURE_KEY_VAULT_ENDPOINT string = keyVault.outputs.keyVaultUri
output AZURE_KEY_VAULT_NAME string = keyVault.outputs.keyVaultName
output WEB_BASE_URL string = 'https://${webContainerApp.outputs.containerAppFqdn}'
output FUNCTION_APP_NAME string = functionApp.outputs.functionAppName
output COSMOS_DB_ENDPOINT string = cosmosDB.outputs.cosmosDBDocumentEndpoint
output AI_FOUNDRY_ENDPOINT string = aiFoundry.outputs.aiFoundryEndpoint
