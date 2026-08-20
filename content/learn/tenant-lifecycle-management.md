# Tenant Lifecycle Management in Kubernetes

## Introduction

Most multi-tenancy discussions stop at onboarding: how a new team gets a namespace and some permissions. The harder part is everything after that — membership changing, environments multiplying, quota being outgrown, standards evolving, and eventually the tenant going away.

Tenant lifecycle management is the practice of handling all of it declaratively, so a tenant's footprint stays correct without anyone maintaining it by hand.

---

## TL;DR

| Stage | Done manually | Managed declaratively |
|--------|-----|----------|
| Onboarding | A ticket and a runbook | One reviewed change in Git |
| Access changes | Role bindings edited per namespace | Derived from identity provider groups |
| Growth | New namespace, configured from memory | Self-service inside the tenant's allocation |
| Standards | Applied at creation, drift afterwards | Reconciled continuously |
| Offboarding | Partial, and often forgotten | Deletion, with a declared retention policy |

---

## The stages

### 1. Onboarding

A new team, department or customer arrives. It needs namespaces, access, an allocation, standard configuration, and usually a GitOps project and a secrets path.

Done as a ticket, this is a runbook that produces a slightly different result every time. Done declaratively, it is one object committed to Git, reviewed like any other change, and applied by the GitOps tool you already run.

The test of a good onboarding process is whether the thirtieth tenant looks identical to the first.

### 2. Access changes

Membership changes constantly — people join, move between teams and leave — and it is the most common source of stale permissions on a shared platform.

The durable answer is to bind access from your existing identity provider groups rather than from lists maintained inside the platform. Then joining the group grants access to the tenant's namespaces, and leaving it removes access, without anyone touching RBAC.

### 3. Growth

Tenants accumulate environments. A team that started with one namespace wants `dev`, `staging` and `prod`, then a namespace per developer to work in.

If every new namespace is a request to the platform team, the platform team becomes the bottleneck. If namespaces are unrestricted, the allocation means nothing. The resolution is a budget at the tenant scope, shared across all of the tenant's namespaces, so the tenant can self-serve while the total stays capped.

### 4. Standards evolving

Platform standards change: a new network policy, a different monitoring configuration, an added label every namespace must carry.

Applied at creation only, changes reach new namespaces and never reach existing ones. Reconciled continuously, they reach everything the tenant owns — including namespaces created after the standard was written.

### 5. Quota and cost review

An allocation set at onboarding is a guess. Reviewing it requires knowing what the tenant actually consumes, which is why cost attribution belongs to the tenant model rather than to a separate reporting exercise.

The useful comparison is requests against actual usage: a tenant whose cost is driven by capacity it reserved and never used is the cheapest saving available.

### 6. Dormancy

Environments go quiet — between projects, overnight, at weekends — and keep consuming capacity. Hibernation scales workloads down and restores them on wake, so dormancy stops being expensive without anyone deleting anything.

### 7. Offboarding

A team is dissolved or a customer leaves. Their namespaces, role bindings, quota, GitOps project and secrets paths should go with them.

Done by hand, this is the stage most often left incomplete: the namespaces are deleted and the external identities linger. Managed declaratively, deleting the tenant removes its footprint according to a retention policy you decided in advance — including whether namespaces and GitOps projects are purged or kept.

---

## Why manual lifecycle management fails

It is not that any single step is difficult. It is that each one is easy to do and easy to skip, and the cost of skipping is invisible for months.

- Access grows. Nobody ever removes a role binding "just in case".
- Namespaces accumulate without owners.
- Quota reflects a decision made once, under different conditions.
- Standards are met by whichever namespaces happened to be created after the standard was written.
- Cost cannot be attributed because attribution depended on labels applied inconsistently.
- Deleted tenants leave residue in every system except the cluster.

Each is a governance failure rather than a Kubernetes failure, which is why more Kubernetes does not fix it.

---

## Declarative tenant lifecycle with MTO

[Multi-Tenant Operator](../index.md) makes the tenant a Kubernetes custom resource and reconciles the cluster to match it continuously:

- **Onboarding** — a `Tenant` in Git; MTO creates the namespaces, role bindings, quota objects, network isolation and templated resources. See [Create a Tenant](../guides/create-tenant.md).
- **Access** — owners, editors and viewers bound from users or existing groups, kept current as membership changes.
- **Growth** — the tenant declares the namespaces it owns and can add more within a quota defined at the tenant scope. Sandboxes give each member a personal namespace. See [Create Namespaces](../guides/create-namespaces.md).
- **Standards** — labels, annotations and templates applied to every namespace the tenant owns, including new ones, and corrected when they drift.
- **Guardrails** — storage classes, ingress classes, priority classes, registries, service accounts and hostnames enforced at admission rather than reviewed afterwards.
- **Cost** — every managed namespace carries `stakater.com/tenant`, so consumption is attributed by construction. See [Cost Analysis](../console/showback.md).
- **Dormancy** — hibernation sleeps a tenant's workloads on a schedule and restores them on wake. See [Hibernate a Tenant](../guides/hibernate-tenant.md).
- **Offboarding** — deleting the tenant removes its footprint according to the retention policy you declared. See [Delete a Tenant](../guides/delete-tenant.md).

Drift is corrected rather than merely detected, which is the property that makes the lifecycle survive contact with a real organization.

---

## Frequently Asked Questions (FAQ)

### What is tenant lifecycle management?

Managing a tenant from onboarding through membership changes, growth, standards, cost review and dormancy to offboarding — declaratively, so the tenant's footprint stays correct without manual maintenance.

### Why not just script tenant onboarding?

Scripts handle creation. Lifecycle management is mostly about what happens afterwards: membership changing, standards evolving and drift accumulating. A script that runs once cannot correct a cluster that has moved since.

### How should tenant offboarding work?

As a deletion with a retention policy decided in advance: whether namespaces are purged or kept, and whether external resources such as GitOps projects are removed with the tenant.

### How does GitOps fit?

Well, and by design. If the tenant is an ordinary Kubernetes object, it lives in Git, goes through review, and is applied by the GitOps tool you already run — with the operator reconciling everything that follows from it.

### What is the most common lifecycle failure?

Stale access. Membership maintained inside the platform rather than derived from identity provider groups drifts from reality within a quarter.

---

## Keywords

tenant lifecycle management
Kubernetes tenant provisioning
tenant onboarding Kubernetes
tenant offboarding
declarative tenant management
GitOps multi-tenancy
Kubernetes tenant governance
