# Azure Deployment Guide

This project assumes an empty Azure account, one Azure for Students subscription and one academic development resource group.

## 1. External values to collect

- Tenant ID: from Microsoft Entra ID.
- Subscription ID: from the Azure subscription page.
- Resource group: `rg-chicago-taxi-dev`.
- Region: `eastus`.
- Developer public IP: only for temporary SQL migrations/testing.

Do not hardcode Tenant ID or Subscription ID in source files. Store deployment values as GitHub Actions variables.

## 2. Azure resources

Deploy `infra/bicep/main.bicep` after configuring GitHub OIDC or from a local Azure CLI session.

The Bicep deployment creates:

- ADLS Gen2 Storage Account with container `chicago-taxi`.
- Azure SQL logical server and database `ChicagoTaxiAnalytics`.
- Azure Static Web App Free.
- Log Analytics Workspace.
- Application Insights.
- Azure Container Apps Environment.
- Azure Container Apps Job for the processor.
- Azure Functions app with system-assigned Managed Identity.
- Storage Blob Data Contributor assignment for the processor job identity.

External/manual steps still required:

- Register resource providers if the subscription has not used them before.
- Configure Microsoft Entra administrator for Azure SQL if not supplied as Bicep parameters.
- Run `database/migrations/001_initial_schema.sql`.
- Create contained Azure SQL users for Managed Identities:
  - processor job identity: write permissions.
  - function app identity: read-only permissions.
- Upload the real dataset to ADLS.
- Configure Static Web Apps deployment token for the GitHub workflow.

## 3. GitHub variables

Configure these as repository or environment variables:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_STORAGE_ACCOUNT_NAME`
- `SQL_SERVER_NAME`
- `SQL_DATABASE_NAME`
- `SQL_ADMINISTRATOR_LOGIN`
- `DEVELOPER_PUBLIC_IP`
- `ENTRA_SQL_ADMINISTRATOR_LOGIN`
- `ENTRA_SQL_ADMINISTRATOR_OBJECT_ID`
- `CONTAINER_APPS_ENVIRONMENT_NAME`
- `PROCESSING_JOB_NAME`
- `STATIC_WEB_APP_NAME`
- `FUNCTION_APP_NAME`
- `FUNCTION_STORAGE_ACCOUNT_NAME`
- `LOG_ANALYTICS_WORKSPACE_NAME`
- `APPLICATION_INSIGHTS_NAME`

Configure these as GitHub secrets:

- `SQL_ADMINISTRATOR_PASSWORD`
- `AZURE_STATIC_WEB_APPS_API_TOKEN`

Do not configure `AZURE_CLIENT_SECRET`; the deployment workflow is designed for OIDC.

## 4. GHCR

The CD workflow publishes:

`ghcr.io/<owner>/<repo>/chicago-taxi-processing:<sha>`

For the simplest academic setup, make the GHCR package public. If the package is private, Azure Container Apps needs registry credentials, which adds a secret and should be documented as an exception.

## 5. Dataset

Download the Chicago Taxi Trips CSV from Kaggle outside the repository. Choose a real subset of at least 100 MB, calculate a checksum, and upload it to:

`chicago-taxi/raw/chicago-taxi/2023/taxi_trips.csv`

Document:

- source URL,
- file size,
- checksum,
- selected date range,
- upload date.

## 6. SQL migration and Managed Identity users

After SQL exists and the developer firewall rule is active, run:

```sql
:r database/migrations/001_initial_schema.sql
```

Then create Entra-contained users for the Function App and Container Apps Job identities. Grant the Function App read-only access and the processor job write access to the analytics tables. This cannot be fully completed from Git before the identities exist.

## 7. Running the cloud pipeline

1. Push to `main` or run the `cd` workflow manually.
2. Confirm the processor image exists in GHCR.
3. Confirm infrastructure deployment succeeded.
4. Upload the dataset to ADLS raw.
5. Start the Container Apps Job manually from Azure Portal or Azure CLI.
6. Verify outputs in ADLS:
   - `processed/chicago-taxi/year=2023/processed_trips.parquet`
   - `results/chicago-taxi/latest/*.parquet`
   - `results/chicago-taxi/latest/data_quality_summary.json`
7. Verify rows in Azure SQL.
8. Open the Static Web App dashboard.

## 8. Cost posture

The project avoids AKS, Databricks, Synapse, Data Factory, Service Bus, Redis, Key Vault and API Management. Use Free or low-cost SKUs where possible and delete the resource group after the academic evaluation if it is no longer needed.
