param location string
param staticWebAppName string

resource staticWebApp 'Microsoft.Web/staticSites@2024-04-01' = {
  name: staticWebAppName
  location: location
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    allowConfigFileUpdates: true
  }
}

output defaultHostname string = staticWebApp.properties.defaultHostname
output name string = staticWebApp.name

