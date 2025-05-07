param location string = resourceGroup().location
param name string
param tags object

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2025-02-01' = {
  name: name 
  location: location
  tags: tags
}

output logAnalyticsId string = logAnalytics.id
