using '../main.bicep'

param environmentName = 'dev'
param location = 'eastus'
param storageAccountName = 'REPLACE_WITH_UNIQUE_STORAGE_NAME'
param sqlServerName = 'REPLACE_WITH_SQL_SERVER_NAME'
param sqlDatabaseName = 'ChicagoTaxiAnalytics'
param sqlAdministratorLogin = 'REPLACE_WITH_ADMIN_LOGIN'
param sqlAdministratorPassword = readEnvironmentVariable('SQL_ADMINISTRATOR_PASSWORD')
param developerIpAddress = readEnvironmentVariable('DEVELOPER_PUBLIC_IP', '')
param entraSqlAdministratorLogin = readEnvironmentVariable('ENTRA_SQL_ADMINISTRATOR_LOGIN', '')
param entraSqlAdministratorObjectId = readEnvironmentVariable('ENTRA_SQL_ADMINISTRATOR_OBJECT_ID', '')
param containerAppsEnvironmentName = 'cae-chicago-taxi-dev'
param processingJobName = 'job-chicago-taxi-processing-dev'
param processingImage = 'REPLACE_WITH_CONTAINER_IMAGE'
param staticWebAppName = 'swa-chicago-taxi-dev'
param functionAppName = 'func-chicago-taxi-dev'
param functionStorageAccountName = 'REPLACE_WITH_FUNCTIONS_STORAGE_NAME'
param logAnalyticsWorkspaceName = 'law-chicago-taxi-dev'
param applicationInsightsName = 'appi-chicago-taxi-dev'
