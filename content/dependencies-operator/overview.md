# MTO Dependencies Operator

The MTO Dependencies Operator is a Kubernetes Helm-based operator that manages infrastructure dependencies for the Multi-Tenant Operator (MTO) ecosystem. It enables cluster administrators to deploy and manage common infrastructure components — such as identity providers, databases, and monitoring tools — through declarative Custom Resources (CRs).

The operator is built using the [Operator SDK Helm plugin](https://sdk.operatorframework.io/docs/building-operators/helm/) and comes **bundled with MTO** — no separate installation is required.

## Managed Components

The operator defines 7 Custom Resource Definitions (CRDs) under the API group `dependencies.tenantoperator.stakater.com/v1alpha1`:

| Component | Kind | Purpose |
|-----------|------|---------|
| Dex | `Dex` | OpenID Connect identity provider |
| PostgreSQL | `Postgres` | Production-ready PostgreSQL database |
| Prometheus | `Prometheus` | Metrics collection, storage, and alerting |
| Kube State Metrics | `KubeStateMetrics` | Exports Kubernetes object metrics for Prometheus |
| OpenCost | `OpenCost` | Kubernetes cost monitoring and FinOps visibility |
| Dex Config Operator | `DexConfigOperator` | Dynamically manages Dex connectors and OAuth client configs |
| FinOps Operator | `FinOpsOperator` | MTO-specific cost management platform |

## How It Works

Each CRD maps to an embedded Helm chart. When you create a CR, the operator deploys the corresponding Helm chart using the CR's `.spec` as chart values. This is enabled by `x-kubernetes-preserve-unknown-fields: true`, which allows the CR spec to accept any values supported by the underlying chart.

The workflow is straightforward:

1. Create a CR with the desired `kind` (e.g. `Dex`, `Postgres`).
1. Populate `.spec` with the Helm chart values you want to customize.
1. Apply the CR — the operator reconciles and deploys the component.

For the full list of configurable values for each component, refer to the [CR Reference](cr-reference.md) and individual [Deployment Guides](guides/deploying-dex.md).
