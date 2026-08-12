targetScope = 'resourceGroup'

@description('Short environment name, for example dev or prod.')
param environmentName string

@description('Azure region for regional resources.')
param location string = resourceGroup().location

@description('Globally unique Storage Account name.')
param storageAccountName string

@description('Azure SQL logical server name.')
param sqlServerName string

@description('Azure SQL database name.')
param sqlDatabaseName string

@description('Azure SQL administrator login. Prefer Entra ID/Managed Identity for application access.')
param sqlAdministratorLogin string

@secure()
@description('Azure SQL administrator password for provisioning only. Do not commit parameter values.')
param sqlAdministratorPassword string

@description('Temporary developer public IP allowed through Azure SQL firewall. Leave empty for no rule.')
param developerIpAddress string = ''

@description('Optional Microsoft Entra SQL administrator display/login name.')
param entraSqlAdministratorLogin string = ''

@description('Optional Microsoft Entra SQL administrator object ID.')
param entraSqlAdministratorObjectId string = ''

@description('Container Apps Environment name.')
param containerAppsEnvironmentName string

@description('Container Apps Job name.')
param processingJobName string

@description('Container image for the future processing job.')
param processingImage string

@description('Static Web App name.')
param staticWebAppName string

@description('Azure Functions app name.')
param functionAppName string

@description('Storage Account name for Azure Functions runtime state.')
param functionStorageAccountName string

@description('Log Analytics Workspace name.')
param logAnalyticsWorkspaceName string

@description('Application Insights component name.')
param applicationInsightsName string

var storageContainerName = 'chicago-taxi'

module storage 'modules/storage.bicep' = {
  name: 'storage'
  params: {
    location: location
    storageAccountName: storageAccountName
  }
}

module sql 'modules/sql.bicep' = {
  name: 'sql'
  params: {
    location: location
    sqlServerName: sqlServerName
    sqlDatabaseName: sqlDatabaseName
    administratorLogin: sqlAdministratorLogin
    administratorPassword: sqlAdministratorPassword
    developerIpAddress: developerIpAddress
    entraAdministratorLogin: entraSqlAdministratorLogin
    entraAdministratorObjectId: entraSqlAdministratorObjectId
  }
}

module staticWebApp 'modules/static-web-app.bicep' = {
  name: 'static-web-app'
  params: {
    location: location
    staticWebAppName: staticWebAppName
  }
}

module monitoring 'modules/monitoring.bicep' = {
  name: 'monitoring'
  params: {
    location: location
    logAnalyticsWorkspaceName: logAnalyticsWorkspaceName
    applicationInsightsName: applicationInsightsName
  }
}

module containerApps 'modules/container-apps.bicep' = {
  name: 'container-apps'
  params: {
    location: location
    environmentName: containerAppsEnvironmentName
    jobName: processingJobName
    image: processingImage
    storageAccountName: storage.name
    storageContainerName: storageContainerName
    sqlServerName: sql.outputs.sqlServerName
    sqlDatabaseName: sql.outputs.sqlDatabaseName
    logAnalyticsCustomerId: monitoring.outputs.workspaceCustomerId
    logAnalyticsSharedKey: monitoring.outputs.workspaceSharedKey
  }
}

module functions 'modules/functions.bicep' = {
  name: 'functions'
  params: {
    location: location
    functionAppName: functionAppName
    functionStorageAccountName: functionStorageAccountName
    sqlServerName: sql.outputs.sqlServerName
    sqlDatabaseName: sql.outputs.sqlDatabaseName
    appInsightsConnectionString: monitoring.outputs.appInsightsConnectionString
    allowedCorsOrigins: [
      'https://${staticWebApp.outputs.defaultHostname}'
      'http://localhost:5173'
    ]
  }
}

module rbac 'modules/rbac.bicep' = {
  name: 'rbac'
  params: {
    storageAccountResourceId: storage.outputs.storageAccountResourceId
    storageAccountName: storage.name
    principalIds: [
      containerApps.outputs.jobPrincipalId
    ]
  }
}

output storageAccountResourceId string = storage.outputs.storageAccountResourceId
output sqlDatabaseResourceId string = sql.outputs.sqlDatabaseResourceId
output staticWebAppDefaultHostname string = staticWebApp.outputs.defaultHostname
output functionAppName string = functions.outputs.functionAppName
output functionAppDefaultHostname string = functions.outputs.defaultHostname
output processingJobPrincipalId string = containerApps.outputs.jobPrincipalId
output functionAppPrincipalId string = functions.outputs.principalId

