param location string
param storageAccountName string

resource storageAccount 'Microsoft.Storage/storageAccounts@2025-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: false
    isHnsEnabled: true
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

resource lakeContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2025-01-01' = {
  name: '${storageAccount.name}/default/chicago-taxi'
  properties: {
    publicAccess: 'None'
  }
}

output name string = storageAccount.name
output storageAccountResourceId string = storageAccount.id
output lakeContainerName string = lakeContainer.name

