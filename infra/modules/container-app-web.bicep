param location string = resourceGroup().location
param name string
param tags object
param containerAppsEnvironmentId string
param containerRegistryLoginServer string
param managedIdentityId string
param environment string
param cosmosDbEndpoint string
@secure()
param cosmosDbPrimaryKey string
param aiFoundryEndpoint string
@secure()
param aiFoundryApiKey string
param applicationInsightsConnectionString string
@secure()
param azureClientId string = ''
@secure()
param azureClientSecret string = ''

resource webContainerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: name
  location: location
  tags: union(tags, { 'azd-service-name': 'stu-copilot-web' })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        allowInsecure: false
        corsPolicy: {
          allowCredentials: true
          allowedOrigins: ['*']
          allowedMethods: ['*']
          allowedHeaders: ['*']
        }
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
      registries: [
        {
          server: containerRegistryLoginServer
          identity: managedIdentityId
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'stu-copilot-web'
          image: '${containerRegistryLoginServer}/stu-copilot-web:latest'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            {
              name: 'ENVIRONMENT'
              value: environment
            }
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: aiFoundryEndpoint
            }
            {
              name: 'AI_FOUNDRY_KEY'
              value: aiFoundryApiKey
            }
            {
              name: 'AI_FOUNDRY_PROJECT_ENDPOINT'
              value: aiFoundryEndpoint
            }
            {
              name: 'APP_INSIGHTS_CONNECTION_STRING'
              value: applicationInsightsConnectionString
            }
            {
              name: 'COSMOSDB_ENDPOINT'
              value: cosmosDbEndpoint
            }
            {
              name: 'COSMOSDB_KEY'
              value: cosmosDbPrimaryKey
            }
            {
              name: 'COSMOSDB_DATABASE'
              value: 'stu-copilot'
            }
            {
              name: 'AZURE_CLIENT_ID'
              value: azureClientId
            }
            {
              name: 'AZURE_CLIENT_SECRET'
              value: azureClientSecret
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
}

output containerAppId string = webContainerApp.id
output containerAppName string = webContainerApp.name
output containerAppFqdn string = webContainerApp.properties.configuration.ingress.fqdn
