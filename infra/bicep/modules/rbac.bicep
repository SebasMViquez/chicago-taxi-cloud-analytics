param storageAccountResourceId string
param storageAccountName string
param principalIds array

resource storageAccount 'Microsoft.Storage/storageAccounts@2025-01-01' existing = {
  name: storageAccountName
}

var storageBlobDataContributorRoleId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
)

resource storageBlobContributors 'Microsoft.Authorization/roleAssignments@2022-04-01' = [
  for principalId in principalIds: {
    name: guid(storageAccountResourceId, principalId, storageBlobDataContributorRoleId)
    scope: storageAccount
    properties: {
      roleDefinitionId: storageBlobDataContributorRoleId
      principalId: principalId
      principalType: 'ServicePrincipal'
    }
  }
]
