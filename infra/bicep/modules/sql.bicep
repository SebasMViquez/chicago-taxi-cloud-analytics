param location string
param sqlServerName string
param sqlDatabaseName string
param administratorLogin string
@secure()
param administratorPassword string
param developerIpAddress string = ''
param entraAdministratorLogin string = ''
param entraAdministratorObjectId string = ''

resource sqlServer 'Microsoft.Sql/servers@2024-05-01-preview' = {
  name: sqlServerName
  location: location
  properties: {
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorPassword
    minimalTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
  }
}

resource entraAdministrator 'Microsoft.Sql/servers/administrators@2024-05-01-preview' = if (!empty(entraAdministratorLogin) && !empty(entraAdministratorObjectId)) {
  name: 'ActiveDirectory'
  parent: sqlServer
  properties: {
    administratorType: 'ActiveDirectory'
    login: entraAdministratorLogin
    sid: entraAdministratorObjectId
    tenantId: subscription().tenantId
  }
}

resource developerFirewallRule 'Microsoft.Sql/servers/firewallRules@2024-05-01-preview' = if (!empty(developerIpAddress)) {
  name: 'developer-temporary'
  parent: sqlServer
  properties: {
    startIpAddress: developerIpAddress
    endIpAddress: developerIpAddress
  }
}

resource database 'Microsoft.Sql/servers/databases@2024-05-01-preview' = {
  name: sqlDatabaseName
  parent: sqlServer
  location: location
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
  }
}

output sqlDatabaseResourceId string = database.id
output sqlServerName string = sqlServer.name
output sqlDatabaseName string = database.name

