# Overview

The MTO Console is the visual interface over everything MTO manages — tenants, namespaces, quotas, costs, templates and hibernation schedules. It serves two audiences from the same data.

Everything the Console shows is read from the same Kubernetes resources you manage in Git, and everything it writes goes back to those resources. There is no second source of truth to reconcile.

![The MTO Console dashboard after sign-in]({{ screenshot: dashboard }})

## Two personas, one model

**Platform administrators** see the whole cluster: every tenant and the namespaces underneath it, quota consumption across the fleet, what each tenant costs, which templates exist and where they are applied, hibernation schedules, and how much capacity the cluster has left. This is where you onboard a tenant, adjust a quota, or find out which team is responsible for last month's increase.

**Tenant users** see only what their tenant owns. They create namespaces within the boundary they were given, check how much of their quota is left, instantiate templates, inspect their own costs, and wake a hibernated environment when they need it back — without filing a ticket, and without being able to step outside the guardrails the administrator set.

Which pages and actions a given user sees is decided by their role on the tenant — owner, editor or viewer. See [Configuration](configuration.md) for the role-to-permission mapping.

## Pages

| Page | What it is for | Primarily |
|---|---|---|
| [Dashboard](dashboard.md) | A snapshot of tenants, namespaces and quotas, plus a seven-day cost trend | Both |
| [Tenants](tenants.md) | Create, update and inspect tenants; quota utilization, YAML and a relationship graph | Administrators |
| [Namespaces](namespaces.md) | The namespaces a tenant owns, and their detail views | Both |
| [Quotas](quotas.md) | The quotas assigned to each tenant and how much is consumed | Administrators |
| [Cost Analysis](showback.md) | Cost by tenant, namespace and workload over a chosen period | Both |
| [Capacity Planning](capacity-planning.md) | What the nodes provide, what is committed, and what remains | Administrators |
| [Hibernation](hibernation.md) | Sleep and wake schedules, and manual sleep or wake by name or label | Both |
| [Templates](templates.md) | The catalogue of reusable manifests and Helm charts | Administrators |
| [Template Instances](template-instances.md) | Deploying a template into a specific namespace | Both |
| [Cluster Template Instances](cluster-template-instances.md) | Deploying a template into every namespace matching a label selector | Administrators |
| [Configuration](configuration.md) | Console roles, permissions and settings | Administrators |

## Getting the Console running

The Console is disabled by default and is enabled through the IntegrationConfig, along with the Gateway and Dex components it depends on. The [Dashboard](dashboard.md) page has the configuration; [IntegrationConfig](../concepts/integration-config.md) has the full reference.
