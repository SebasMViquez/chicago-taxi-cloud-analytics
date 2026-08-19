# Phase 9 - Azure Infrastructure Deployment

## Context

Phase 9 deployed the Azure infrastructure that had been validated during Phase 8.

The deployment was executed with Bicep at resource group scope against:

```text
Resource Group: rg-chicago-taxi-dev
```

General command shape:

```text
az deployment group create
  --resource-group rg-chicago-taxi-dev
  --parameters infra/bicep/parameters/dev.bicepparam
  --mode Incremental
  --validation-level Provider
```

No SQL administrator password, token, connection string, or secret value is documented here.

## Deployment #1

Deployment name:

```text
chicago-taxi-initial
```

Result:

```text
FAILED
```

Root cause:

Azure SQL did not allow provisioning a new logical server in the initial SQL region:

```text
RegionDoesNotAllowProvisioning
```

Initial attempted SQL region:

```text
eastus
```

Regional capability checks for this subscription showed:

| Region | SQL Provisioning Status |
| --- | --- |
| `centralus` | Available |
| `westus3` | Available |

Decision:

```text
Use centralus only for Azure SQL.
```

The Bicep configuration was updated to add an independent SQL region parameter:

```text
sqlLocation = centralus
```

The previous SQL Server name:

```text
sql-chicago-taxi-dev-73e29256
```

remained associated with the failed eastus attempt in Azure what-if behavior. It was not reused.

Azure SQL `checkNameAvailability` confirmed the replacement name was available:

```text
sql-chicago-taxi-dev-cu-73e29256
```

The SQL Server name was then updated to that new value.

## Deployment #2

Deployment name:

```text
chicago-taxi-initial-02
```

Result:

```text
PARTIAL / FAILED
```

Succeeded modules:

- `storage`
- `monitoring`
- `static-web-app`
- `sql`
- `container-apps`

SQL was created successfully:

| Item | Value |
| --- | --- |
| Server | `sql-chicago-taxi-dev-cu-73e29256` |
| Location | `centralus` |
| Database | `ChicagoTaxiAnalytics` |
| Database status | `Online` |

The Container Apps Environment and Container Apps Job were also created successfully.

Failed modules:

- `rbac`
- `functions`

## RBAC Problem And Fix

Real RBAC error:

```text
ResourceNotFound
```

ARM attempted to resolve:

```text
Microsoft.Storage/storageAccounts/storage
```

The real Storage Account was:

```text
stchicagotaxidev73e29256
```

Root cause:

`main.bicep` passed this value into the RBAC module:

```bicep
storageAccountName: storage.name
```

In that context, `storage.name` referred to the Bicep module or nested deployment name:

```text
storage
```

It did not refer to the real Storage Account name.

Correction:

```bicep
storageAccountName: storage.outputs.name
```

The `storage.bicep` module exposes:

```bicep
output name string = storageAccount.name
```

After this correction, RBAC correctly targets:

```text
stchicagotaxidev73e29256
```

The role remains:

```text
Storage Blob Data Contributor
```

The principal is the System Assigned Managed Identity of the Container Apps Job.

## Functions Problem And Fix

Deployment #2 also failed in Azure Functions with:

```text
SubscriptionIsOverQuotaForSku
```

Details:

```text
Current Limit (Total VMs): 0
Amount required: 1
```

The error occurred while Functions Consumption `Y1` was attempted in:

```text
eastus
```

A region was not selected blindly. A temporary Bicep validation file outside the repository was used only to validate an isolated Azure Functions Consumption Plan:

```text
Resource type: Microsoft.Web/serverfarms
SKU: Y1
Tier: Dynamic
Linux reserved: true
```

The isolated validation was run in:

```text
centralus
```

using:

```text
az deployment group validate
  --validation-level Provider
```

Validation result:

| Item | Value |
| --- | --- |
| provisioningState | `Succeeded` |
| validationLevel | `Provider` |
| exit code | `0` |

Therefore, Bicep was updated to add an independent Functions region:

```text
functionsLocation = centralus
```

The Functions module changed from:

```bicep
location: location
```

to:

```bicep
location: functionsLocation
```

No Functions SKU, runtime, identity, storage architecture, or application settings were changed for this fix.

## Final Region Matrix

The final regional strategy is:

| Resource Area | Region |
| --- | --- |
| Resource Group | `eastus` |
| Primary / main resources | `eastus` |
| Storage / ADLS | `eastus` |
| Log Analytics | `eastus` |
| Application Insights | `eastus` |
| Container Apps Environment | `eastus` |
| Container Apps Job | `eastus` |
| Static Web App | `eastus2` |
| Azure SQL Server | `centralus` |
| Azure SQL Database | `centralus` |
| Azure Functions | `centralus` |
| Functions Storage | `centralus` |
| Functions Consumption Plan | `centralus` |

An Azure Resource Group can contain resources deployed in multiple Azure regions. This separation was necessary because real provisioning restrictions were encountered for specific services in the subscription.

## Final What-if

Before deployment #3, a final what-if was executed.

Result:

```text
exit code = 0
```

Prediction:

```text
3 resources to create
9 resources to deploy
2 resources to ignore
1 unsupported
```

The three resources predicted as Create were:

- Functions Storage Account
- Functions Consumption Plan
- Function App

The only Unsupported item corresponded to the RBAC role assignment.

What-if could not calculate the role assignment resource ID because it depended on the runtime `principalId` of the Container Apps Job Managed Identity.

The final what-if did not report:

- `Delete`
- `SubscriptionIsOverQuotaForSku`
- `ResourceNotFound`
- `InvalidResourceLocation`
- `RegionDoesNotAllowProvisioning`

## Deployment #3 - Success

Deployment name:

```text
chicago-taxi-initial-03
```

Final result:

```text
SUCCEEDED
```

Observed deployment output:

| Item | Value |
| --- | --- |
| `error` | `null` |
| `mode` | `Incremental` |
| `provisioningState` | `Succeeded` |
| `validationLevel` | `Provider` |
| approximate duration | `1m53s` |

The final deployment output resources included:

- `Microsoft.App/jobs/job-chicago-taxi-processing-dev`
- `Microsoft.App/managedEnvironments/cae-chicago-taxi-dev`
- `Microsoft.Insights/components/appi-chicago-taxi-dev`
- `Microsoft.OperationalInsights/workspaces/law-chicago-taxi-dev`
- `Microsoft.Sql/servers/sql-chicago-taxi-dev-cu-73e29256`
- `Microsoft.Sql/servers/sql-chicago-taxi-dev-cu-73e29256/databases/ChicagoTaxiAnalytics`
- `Microsoft.Storage/storageAccounts/stchicagotaxidev73e29256`
- Blob container: `chicago-taxi`
- `Microsoft.Authorization/roleAssignments` over the Storage Account
- Functions Storage: `stchitaxifuncdev73e29256`
- Functions Consumption Plan: `func-chicago-taxi-dev-73e29256-plan`
- Function App: `func-chicago-taxi-dev-73e29256`
- Static Web App: `swa-chicago-taxi-dev-73e29256`

## Managed Identities

The final deployment returned:

- Function App principal ID created successfully.
- Processing Job principal ID created successfully.

The concrete GUID values are not documented here.

This confirms that the System Assigned Managed Identities required for later security and integration phases exist.

## Security

Security notes:

- SQL administrator password is a `SecureString`.
- The SQL administrator password is not hardcoded in the repository.
- It was loaded through a local environment variable during deployment.
- Its value must never be written, printed, committed, or documented.
- Container Apps Job uses a System Assigned Managed Identity.
- Function App uses a System Assigned Managed Identity.
- The Job received `Storage Blob Data Contributor` over ADLS through Bicep.
- The real Container Apps Job has not been executed yet.
- The real dataset has not been uploaded to Azure yet.
- SQL migrations have not been executed yet.

## Known Warning

Known Bicep warning:

```text
Parameter "environmentName" is declared but never used.
```

This warning was non-blocking:

- `lint` completed successfully.
- `build` completed successfully.
- `build-params` completed successfully.
- The final deployment completed with `Succeeded`.

## Evidence / Suggested Screenshots

Suggested evidence files:

| Suggested File | Purpose |
| --- | --- |
| `33-phase-9-deployment-succeeded.png` | Shows the successful `chicago-taxi-initial-03` deployment result. |
| `34-phase-9-resource-inventory.png` | Shows the created Azure resources in the resource group. |
| `35-phase-9-function-app-created.png` | Shows the Function App and related Functions resources. |
| `36-phase-9-storage-rbac-job.png` | Shows Storage RBAC assignment for the Container Apps Job identity. |
| `37-phase-9-sql-online.png` | Shows the Azure SQL Server and online database. |

These names are suggestions only. This document does not state that the images are stored in the repository.

## Lessons Learned

1. Azure service availability depends on both region and subscription.
2. What-if cannot always evaluate resources whose IDs depend on runtime values.
3. A failed incremental deployment can still leave correctly created resources.
4. It is better to diagnose and continue incrementally than to delete all infrastructure by default.
5. Bicep module outputs should be used when another module needs the real resource name.
6. Regions can be separated by service when real provisioning restrictions require it.

## Phase Result

PHASE 9 RESULT: PASS

Final deployment:

```text
chicago-taxi-initial-03
```

Final provisioning state:

```text
Succeeded
```

Project status:

```text
READY_FOR_PHASE_10_AZURE_SQL_CONFIGURATION
```
