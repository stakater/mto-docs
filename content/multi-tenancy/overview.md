# Multi-Tenancy

**How do I safely share Kubernetes?**

Running a cluster per team is the easy answer and the expensive one: every cluster multiplies the control planes, monitoring stacks and upgrade cycles a platform team has to operate. Sharing one cluster is cheaper, but only if the boundaries between teams are real — and hand-written RBAC, per-namespace quota and a wiki page of conventions do not make them real for long.

MTO makes the boundary a first-class object. A `Tenant` names the people, the namespaces, the quota and the standards that belong to one team, department or customer, and MTO reconciles the cluster to match it — continuously, so drift is corrected rather than merely detected.

## What it covers

| Area | What MTO does |
|---|---|
| Ownership | A `Tenant` is the unit that access, cost, lifecycle and external tools all agree on |
| Access control | Owners, editors and viewers bound to tenant namespaces automatically, from users or existing groups |
| Namespaces | Tenants declare the namespaces they own, plus per-user sandboxes, without an admin in the loop |
| Quota | One budget defined at the tenant scope and shared across all of its namespaces |
| Guardrails | Storage classes, ingress classes, priority classes, image registries, service accounts and hostnames enforced at admission |
| Isolation | Network isolation between tenants and workload pinning to a node pool |
| Metadata | Labels and annotations applied cluster-wide, per tenant or per namespace, with templated values |

## How the boundary is enforced

Two mechanisms do the work, and the distinction is worth keeping straight:

- **Controllers** create and continuously reconcile what the tenant owns — namespaces, role bindings, quota objects, metadata and templated resources.
- **The admission webhook** enforces the boundary at write time. A tenant user cannot exceed quota, pull from an unapproved registry, claim a storage class outside their allow-list, use a denied service account, escalate priority class, or claim a hostname belonging to another tenant.

Guardrails are set by the administrator; inside them, the tenant is self-service.

## Secure by default

The guardrails that grant permissions — storage classes, ingress classes and pod priority classes — are off until you configure them, and each has three states:

- Omitted entirely: the feature is disabled and MTO grants no RBAC for it.
- Present but empty: everything is allowed, and MTO creates the RBAC to use it.
- Present with an allow-list: only the listed values are permitted.

A tenant never gains a permission because someone forgot to restrict it.

## Concepts

- [Tenant](concepts/tenant.md) — the object everything else reads from
- [Quota](concepts/quota.md) — budgets at the tenant scope
- [Integration Config](concepts/integration-config.md) — cluster-wide policy, set once

## Guides

- [Create a Tenant](guides/create-tenant.md) — start with one object
- [Create Namespaces](guides/create-namespaces.md) and [Sandboxes](guides/create-sandbox.md)
- [Custom Roles](guides/custom-roles.md) and [Extending Default Roles](guides/extend-default-roles.md)
- [Storage Classes](guides/storage-classes.md), [Image Registries](guides/image-registries.md), [Pod Priority Classes](guides/pod-priority-classes.md), [Service Accounts](guides/service-accounts.md), [Host Validation](guides/host-validation.md)
- [Disable Intra-Tenant Networking](guides/disable-intra-tenant-networking.md) and [Restrict Node Pools](guides/restrict-nodepool-per-tenant.md)
