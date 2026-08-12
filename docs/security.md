# Security

Security defaults:

- No dataset files, generated Parquet, `.env`, `local.settings.json` or secrets in Git.
- GitHub deploys to Azure with OIDC, not a long-lived Azure client secret.
- Azure workloads use Managed Identity.
- Processor identity writes to ADLS and Azure SQL.
- Function App identity reads from Azure SQL.
- Azure SQL uses public network access with restricted firewall rules for this academic version.
- Storage Account public blob access is disabled.

Secrets still required externally:

- SQL administrator password for initial provisioning only.
- Static Web Apps deployment token for the GitHub upload action.

Avoid:

- Storage Account keys in application runtime.
- SQL usernames/passwords in Azure workloads.
- Permanent `AZURE_CLIENT_SECRET` in GitHub Actions.
