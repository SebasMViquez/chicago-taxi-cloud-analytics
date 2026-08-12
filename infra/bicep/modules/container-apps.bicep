param location string
param environmentName string
param jobName string
param image string
param storageAccountName string
param storageContainerName string
param sqlServerName string
param sqlDatabaseName string
param logAnalyticsCustomerId string
@secure()
param logAnalyticsSharedKey string

resource environment 'Microsoft.App/managedEnvironments@2025-01-01' = {
  name: environmentName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsCustomerId
        sharedKey: logAnalyticsSharedKey
      }
    }
  }
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
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            {
              name: 'PROCESSING_MODE'
              value: 'adls'
            }
            {
              name: 'PROCESSING_INPUT_PATH'
              value: 'raw/chicago-taxi/2023/taxi_trips.csv'
            }
            {
              name: 'PROCESSING_PROCESSED_PATH'
              value: 'processed/chicago-taxi/year=2023/processed_trips.parquet'
            }
            {
              name: 'PROCESSING_RESULTS_PREFIX'
              value: 'results/chicago-taxi/latest'
            }
            {
              name: 'PROCESSING_LOAD_SQL'
              value: 'true'
            }
            {
              name: 'AZURE_STORAGE_ACCOUNT_NAME'
              value: storageAccountName
            }
            {
              name: 'AZURE_STORAGE_CONTAINER_NAME'
              value: storageContainerName
            }
            {
              name: 'SQL_SERVER_NAME'
              value: sqlServerName
            }
            {
              name: 'SQL_DATABASE_NAME'
              value: sqlDatabaseName
            }
            {
              name: 'SQL_AUTH_MODE'
              value: 'ManagedIdentity'
            }
          ]
        }
      ]
    }
  }
}

output jobPrincipalId string = job.identity.principalId
output environmentId string = environment.id

