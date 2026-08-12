param location string
param logAnalyticsWorkspaceName string
param applicationInsightsName string

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsWorkspaceName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: applicationInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: workspace.id
  }
}

output workspaceId string = workspace.id
output workspaceCustomerId string = workspace.properties.customerId
@secure()
output workspaceSharedKey string = workspace.listKeys().primarySharedKey
output appInsightsConnectionString string = appInsights.properties.ConnectionString
