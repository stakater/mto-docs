# Overview

MTO can extend tenancy into the tools you run alongside the cluster, so each tenant reaches only its own resources there. Every extension is optional. Each page below covers one:

- [ArgoCD](argocd.md) – An `AppProject` per tenant, scoped to that tenant's namespaces.
- [Vault](vault/vault.md) – A KV path per tenant, with the policies, identity groups and login roles to reach it.
- [OpenBao](openbao/overview.md) – An OpenBao namespace per tenant, holding its own secrets store, encryption keys and certificate authority, with the policies and login roles to reach them.
- [Grafana stack](grafana-stack/overview.md) – Per-tenant logs, metrics, traces and dashboards in one shared Loki/Mimir/Tempo/Grafana stack, behind gateways that authorise every request.
- [DevWorkspace](devworkspace.md) – Sandbox namespaces that arrive carrying the metadata a workspace needs.

Each extension is configured once for the cluster; everything per tenant is derived from your [`Tenant`](../concepts/tenant.md) resources, so a new tenant needs no setup step in the tool.

To integrate a tool that is not listed here, see [Build your own extension](build-your-own/overview.md).
