# Phase 8 - Bicep Pre-deployment Validation

## Purpose

Phase 8 prepared and audited the Bicep infrastructure before any real Azure deployment.

This phase is now complete. It covered Bicep parameter readiness, regional compatibility, final local validation, Azure `what-if`, and read-only analysis of nested deployment diagnostics.

## Azure Context

| Item | Value |
| --- | --- |
| Resource Group | `rg-chicago-taxi-dev` |
| Location | `eastus` |
| Environment | `dev` |

No passwords, tokens, access keys, or other secrets are documented here.

## Resource Provider Registration

The required Azure resource providers were initially not all registered. They were later registered and validated as `Registered`:

- `Microsoft.Storage`
- `Microsoft.Sql`
- `Microsoft.App`
- `Microsoft.Web`
- `Microsoft.OperationalInsights`
- `Microsoft.Insights`
- `Microsoft.Authorization`

`Microsoft.Authorization` was already registered.

Registering resource providers is not the same as deploying the project resources. No application infrastructure was created by this provider registration step.

## Resource Name Validation

Read-only Azure name availability checks were performed before replacing deployment placeholders.

Azure returned positive availability for:

| Resource Purpose | Name | Availability |
| --- | --- | --- |
| Storage ADLS | `stchicagotaxidev73e29256` | Available |
| Functions Storage | `stchitaxifuncdev73e29256` | Available |
| SQL Server | `sql-chicago-taxi-dev-73e29256` | Available |
| Function App | `func-chicago-taxi-dev-73e29256` | Available |

These checks only validated name availability. They did not create any of these resources.

## Bicep Parameter Changes

The file `infra/bicep/parameters/dev.bicepparam` was updated to replace deployment placeholders with concrete development values.

| Parameter | Previous Value | Current Value |
| --- | --- | --- |
| `storageAccountName` | `REPLACE_WITH_UNIQUE_STORAGE_NAME` | `stchicagotaxidev73e29256` |
| `sqlServerName` | `REPLACE_WITH_SQL_SERVER_NAME` | `sql-chicago-taxi-dev-73e29256` |
| `sqlAdministratorLogin` | `REPLACE_WITH_ADMIN_LOGIN` | `chicagotaxiadmin` |
| `processingImage` | `REPLACE_WITH_CONTAINER_IMAGE` | `mcr.microsoft.com/k8se/quickstart-jobs:latest` |
| `staticWebAppName` | `swa-chicago-taxi-dev` | `swa-chicago-taxi-dev-73e29256` |
| `functionAppName` | `func-chicago-taxi-dev` | `func-chicago-taxi-dev-73e29256` |
| `functionStorageAccountName` | `REPLACE_WITH_FUNCTIONS_STORAGE_NAME` | `stchitaxifuncdev73e29256` |

No secrets were added to the parameter file.

## Static Web App Region Fix

The first Azure `what-if` detected a regional incompatibility:

```text
LocationNotAvailableForResourceType
```

Affected resource type:

```text
Microsoft.Web/staticSites
```

The service was not available in the primary project region:

```text
eastus
```

Azure reported valid Static Web App regions including:

```text
eastus2
```

The project kept the main deployment region as `eastus` and moved only Static Web App to `eastus2`.

Implemented Bicep change:

- `infra/bicep/main.bicep` now declares `staticWebAppLocation`.
- The Static Web App module now receives `location: staticWebAppLocation`.
- `infra/bicep/parameters/dev.bicepparam` sets `staticWebAppLocation = 'eastus2'`.

Final location strategy:

| Resource Group / Resource Area | Location |
| --- | --- |
| Main deployment location | `eastus` |
| Static Web App | `eastus2` |

These resources continue to use the main `eastus` location:

- Storage / ADLS
- SQL Server
- SQL Database
- Container Apps Environment
- Container Apps Job
- Functions Storage Account
- Function App
- Log Analytics Workspace
- Application Insights

## Bootstrap Container Image

The current development parameter file uses this temporary bootstrap image:

```text
mcr.microsoft.com/k8se/quickstart-jobs:latest
```

This is only a bootstrap image to allow initial creation of the Container Apps Job before the real processor image exists in GHCR.

Current safety notes:

- The Container Apps Job uses `triggerType = Manual`.
- The Job was not executed.
- No cloud processing was performed.
- The real processor image will be configured in a later phase.

This document does not claim that the bootstrap image was executed.

## SQL Secret Strategy

The SQL administrator password is still externalized with:

```bicep
readEnvironmentVariable('SQL_ADMINISTRATOR_PASSWORD')
```

`SQL_ADMINISTRATOR_PASSWORD` remains outside Git. Its value is not documented, printed, hashed, or otherwise represented here.

Before `what-if`, a valid secure SQL administrator password must be configured in the local PowerShell session.

## Optional SQL Configuration

The following optional settings may remain empty for this stage:

- `DEVELOPER_PUBLIC_IP`
- `ENTRA_SQL_ADMINISTRATOR_LOGIN`
- `ENTRA_SQL_ADMINISTRATOR_OBJECT_ID`

Not configured yet:

- Developer SQL firewall rule.
- Microsoft Entra SQL administrator.

These tasks remain for later phases.

## SQL Cost Configuration

`infra/bicep/modules/sql.bicep` was updated from the previous `Basic` database SKU to Azure SQL Database General Purpose serverless with Free Offer enabled.

Previous configuration:

```text
SKU: Basic / Basic
```

Current configuration:

```bicep
sku: {
  name: 'GP_S_Gen5'
  tier: 'GeneralPurpose'
  family: 'Gen5'
  capacity: 2
}

properties: {
  collation: 'SQL_Latin1_General_CP1_CI_AS'
  useFreeLimit: true
  freeLimitExhaustionBehavior: 'AutoPause'
  autoPauseDelay: 60
  minCapacity: json('0.5')
  maxSizeBytes: 34359738368
  requestedBackupStorageRedundancy: 'Local'
}
```

Configuration notes:

- `GP_S_Gen5` corresponds to the General Purpose serverless model used by this configuration.
- `capacity = 2` configures the maximum capacity for this development database.
- `minCapacity: json('0.5')` compiles to numeric `0.5`.
- `maxSizeBytes = 34359738368` corresponds to 32 GiB.
- `useFreeLimit = true` enables the Azure SQL Database Free Offer.
- `freeLimitExhaustionBehavior = AutoPause` is intended to avoid continuing usage after the free limit is reached.
- `autoPauseDelay = 60` allows auto-pause after the configured inactivity period.
- `requestedBackupStorageRedundancy = Local` uses local backup redundancy.

No monetary cost estimates are documented here.

The database API version remained:

```bicep
Microsoft.Sql/servers/databases@2024-05-01-preview
```

Codex verified property compatibility for this API version before modifying `infra/bicep/modules/sql.bicep`.

Azure SQL Database has not been deployed or created yet.

## Final Bicep Validation

Final validation results after the SQL Free Offer configuration and Static Web App region fix:

| Validation | Result |
| --- | --- |
| Branch | `Integraciones_CLOUD` |
| Bicep lint | PASS |
| Bicep lint exit code | 0 |
| Bicep lint errors | 0 |
| Bicep lint warnings | 1 |
| Bicep build | PASS |
| Bicep build exit code | 0 |
| Bicep build errors | 0 |
| Bicep build warnings | 1 |
| Bicep build-params | PASS |
| Bicep build-params exit code | 0 |
| Placeholder validation | PASS: no `REPLACE_WITH_` placeholders remain |
| Location validation | `location = eastus`, `staticWebAppLocation = eastus2` |
| `git diff --check` | PASS |
| `git diff --check` exit code | 0 |

Known non-blocking warning:

```text
Parameter "environmentName" is declared but never used.
```

The same warning appeared in both lint and build.

No ARM JSON file was generated inside the repository.

This task did not read, print, or write `SQL_ADMINISTRATOR_PASSWORD`, and no secrets or passwords were added to the repository.

The LF/CRLF Git warnings observed in the working tree did not cause `git diff --check` to fail.

## What-if #2

The final Phase 8 `what-if` was executed conceptually as:

```text
az deployment group what-if
  --resource-group rg-chicago-taxi-dev
  --parameters infra/bicep/parameters/dev.bicepparam
  --validation-level Provider
  --result-format ResourceIdOnly
```

No secret values are documented.

Result:

| Item | Value |
| --- | --- |
| Exit code | 0 |
| Scope | `rg-chicago-taxi-dev` |
| Resource changes | 7 to create |

Visible resources reported as Create:

1. `Microsoft.Insights/components/appi-chicago-taxi-dev`
2. `Microsoft.OperationalInsights/workspaces/law-chicago-taxi-dev`
3. `Microsoft.Sql/servers/sql-chicago-taxi-dev-73e29256`
4. `Microsoft.Sql/servers/sql-chicago-taxi-dev-73e29256/databases/ChicagoTaxiAnalytics`
5. `Microsoft.Storage/storageAccounts/stchicagotaxidev73e29256`
6. `Microsoft.Storage/storageAccounts/stchicagotaxidev73e29256/blobServices/default/containers/chicago-taxi`
7. `Microsoft.Web/staticSites/swa-chicago-taxi-dev-73e29256`

What-if interpretation:

- 7 resources were visible as `Create`.
- No `Delete` operations were reported.
- No unexpected `Modify` operations were reported.
- The previous Static Web App location error no longer appeared.

`what-if` is not a deployment. These resources were not created during Phase 8.

## Nested Deployment Diagnostics

The final `what-if` reported:

| Nested Deployment | Diagnostic |
| --- | --- |
| `container-apps` | `NestedDeploymentShortCircuited` |
| `functions` | `NestedDeploymentShortCircuited` |
| `rbac` | `NestedDeploymentShortCircuited` |

A read-only Bicep audit was performed after the `what-if`.

## Container Apps Diagnostic

Classification:

```text
EXPECTED_WHAT_IF_LIMITATION
```

Cause:

```bicep
monitoring.outputs.workspaceSharedKey
```

This output comes from:

```bicep
workspace.listKeys().primarySharedKey
```

It is a runtime value that `what-if` cannot fully evaluate before the Log Analytics Workspace exists.

Expected resources hidden by the short-circuit:

- `Microsoft.App/managedEnvironments/cae-chicago-taxi-dev`
- `Microsoft.App/jobs/job-chicago-taxi-processing-dev`

No deployment blocker was found.

## Functions Diagnostic

Classification:

```text
EXPECTED_WHAT_IF_LIMITATION
```

Runtime dependencies identified:

- `monitoring.outputs.appInsightsConnectionString`
- `staticWebApp.outputs.defaultHostname`
- `functionStorage.listKeys().keys[0].value`

Expected resources hidden by the short-circuit:

- `Microsoft.Storage/storageAccounts/stchitaxifuncdev73e29256`
- `Microsoft.Web/serverfarms/func-chicago-taxi-dev-73e29256-plan`
- `Microsoft.Web/sites/func-chicago-taxi-dev-73e29256`

No deployment blocker was found.

## RBAC Diagnostic

Classification:

```text
EXPECTED_WHAT_IF_LIMITATION
```

Cause:

```bicep
containerApps.outputs.jobPrincipalId
```

This output comes from:

```bicep
job.identity.principalId
```

The `principalId` of a system-assigned Managed Identity is produced at runtime when Azure creates or evaluates the Container Apps Job.

Expected resource hidden by the short-circuit:

- `Microsoft.Authorization/roleAssignments/<generated-guid>`

Expected role:

```text
Storage Blob Data Contributor
```

No deployment blocker was found.

## Complete Expected Inventory

The complete deployment is expected to create:

- ADLS Gen2 Storage Account
- `chicago-taxi` blob container
- Azure SQL Server
- Azure SQL Database
- Static Web App
- Log Analytics Workspace
- Application Insights
- Container Apps Environment
- Container Apps Job
- Functions Storage Account
- Functions Consumption Plan
- Function App
- Storage Blob Data Contributor role assignment

Conditional SQL resources that are not expected to be created yet because their parameters remain empty:

- Developer firewall rule
- Microsoft Entra SQL administrator

None of these application resources were deployed during Phase 8.

## Deployment Status

- No `az deployment group create` was executed.
- `az deployment group what-if` was executed and completed with exit code 0.
- No application infrastructure has been deployed yet.
- Azure SQL Database has not been created yet.
- The only Azure resource created previously is the Resource Group from Phase 7.
- Phase 8 result is PASS.

## Suggested Evidence

Suggested screenshots or evidence files:

- `30-phase-8-final-validation.png`
- `31-phase-8-what-if-pass.png`
- `32-phase-8-short-circuit-audit.png`

These are suggested evidence names only. No images are created by this document.

## Final Phase 8 Conclusion

PHASE 8 RESULT: PASS

Reasons:

- Bicep compiles successfully.
- Parameters compile successfully.
- No placeholders remain.
- Resource names were validated.
- Required providers are registered.
- SQL Free Offer configuration is prepared.
- Static Web App regional incompatibility was found and corrected.
- Final `what-if` completed with exit code 0.
- The three nested deployment diagnostics were audited and classified as expected `what-if` limitations caused by runtime dependencies.
- No deployment blocker was identified.
- No application infrastructure was deployed during Phase 8.

Project status:

```text
READY_FOR_PHASE_9_DEPLOYMENT
```

Phase 9 has not been executed by this document.
