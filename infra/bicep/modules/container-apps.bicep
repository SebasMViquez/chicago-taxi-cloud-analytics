param location string
param environmentName string
param jobName string
param image string
param storageAccountName string

resource environment 'Microsoft.App/managedEnvironments@2025-01-01' = {
  name: environmentName
  location: location
}

resource job 'Microsoft.App/jobs@2025-01-01' = {
  name: jobName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    environmentId: environment.id
    configuration: {
      triggerType: 'Manual'
      replicaTimeout: 1800
      replicaRetryLimit: 1
    }
    template: {
      containers: [
        {
          name: 'processor'
          image: image
          env: [
            {
              name: 'AZURE_STORAGE_ACCOUNT_NAME'
              value: storageAccountName
            }
          ]
        }
      ]
    }
  }
}

output jobPrincipalId string = job.identity.principalId

