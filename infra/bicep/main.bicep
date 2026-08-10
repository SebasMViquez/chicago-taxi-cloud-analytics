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

@description('Container Apps Environment name.')
param containerAppsEnvironmentName string

@description('Container Apps Job name.')
param processingJobName string

@description('Container image for the future processing job.')
param processingImage string

@description('Static Web App name.')
param staticWebAppName string

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
  }
}

module staticWebApp 'modules/static-web-app.bicep' = {
  name: 'static-web-app'
  params: {
    location: location
    staticWebAppName: staticWebAppName
  }
}

output storageAccountResourceId string = storage.outputs.storageAccountResourceId
output sqlDatabaseResourceId string = sql.outputs.sqlDatabaseResourceId
output staticWebAppDefaultHostname string = staticWebApp.outputs.defaultHostname

