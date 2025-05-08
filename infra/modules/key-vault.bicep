param location string = resourceGroup().location
param name string
param tags object

resource keyVault 'Microsoft.KeyVault/vaults@2024-12-01-preview' = {
  name: name
  location: location
  tags: tags
  properties: {
    createMode: 'default'
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: false
    enableSoftDelete: true
    enableRbacAuthorization: true
    enablePurgeProtection: true
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Deny'
    }
    sku: {
      family: 'A'
      name: 'standard'
    }
    // accessPolicies: [
    //   {
    //     tenantId: subscription().tenantId
    //     objectId: ''
    //     permissions: {
    //       keys: [
    //         'all'
    //       ]
    //       secrets: [
    //         'all'
    //       ]
    //       certificates: [
    //         'all'
    //       ]
    //     }
    //   }
    // ]     
    softDeleteRetentionInDays: 7
    tenantId: subscription().tenantId
  }
}

output keyVaultId string = keyVault.id
