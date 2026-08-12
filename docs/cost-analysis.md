# Cost Analysis

Target cost: as close to USD 0 as possible while using Azure services required by the assignment.

Low-cost choices:

- Azure Static Web Apps Free.
- Azure SQL Basic for academic aggregate tables.
- Standard LRS storage for ADLS Gen2.
- Azure Functions consumption-style hosting.
- Container Apps Job manual trigger so the processor runs only on demand.
- 30-day Log Analytics retention.

Cost risks:

- Large ADLS storage or repeated uploads.
- Long-running Container Apps Job executions.
- Azure SQL running after the project is no longer needed.
- Log Analytics ingestion from verbose logs.
- Static Web Apps or Functions usage beyond free grants.

Controls:

- Process a bounded dataset subset for the academic demo.
- Keep Container Apps Job manual.
- Delete `rg-chicago-taxi-dev` after evaluation if no longer needed.
- Review Cost Management in Azure Portal during testing.
