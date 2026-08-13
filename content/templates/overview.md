# Templates

**How do I standardize environments?**

Every platform team has a list of things that should exist in every namespace: a network policy, an image pull secret, a monitoring configuration, a set of default limits. Documenting that list produces a baseline people follow inconsistently. Templates turn it into one that is applied and kept applied.

Templates are delivered by the **Template Operator**, installed alongside MTO. A template describes what a namespace should contain — Kubernetes manifests, a Helm chart, or references to existing resources — and is parameterized, so one definition serves many namespaces.

## What it covers

| Area | What it does |
|---|---|
| Reusable environments | One parameterized definition rendered into many namespaces |
| Enforced baselines | Templates applied to every namespace of one tenant, or of all tenants, and kept in sync |
| Resource distribution | Secrets and ConfigMaps cloned from a source namespace into namespaces selected by label |
| Self-service | Tenant users instantiate approved templates themselves, from the CLI or the Console |

## The resources

- **`Template`** — the definition: manifests, a Helm chart, or resource mappings.
- **`TemplateInstance`** — renders a template into a single namespace, inside one tenant.
- **`TemplateGroupInstance`** — renders a template into every namespace matching a label selector, including across tenants when that is intended.
- **`ClusterTemplateInstance`** — a cluster-scoped instance for resources that are not namespace-bound.

Because MTO stamps `stakater.com/tenant: <tenant-name>` on every namespace it manages, a `TemplateGroupInstance` selecting on that label covers a whole tenant — including namespaces created after the template was written.

## Common uses

- Network policies that isolate a tenant's namespaces
- Image pull secrets and other credentials injected at namespace creation
- Development tooling present in every namespace
- Pre-populated databases with test data for sandbox environments

## Where it fits

A Tenant can name the templates that apply to its namespaces, so a namespace arrives complete rather than empty. That is what makes sandboxes useful: a per-user namespace that already contains everything a developer needs.

See [Create a Tenant](../multi-tenancy/guides/create-tenant.md) for the tenant side, and the [Templates console](../console/templates.md) for the UI.
