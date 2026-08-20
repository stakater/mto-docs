# What is a Tenant in Kubernetes?

## Introduction

Kubernetes has no built-in concept of a tenant. It has namespaces, service accounts, roles and quotas — resources that a tenant *uses*, but nothing that represents the tenant itself.

That gap is why multi-tenant platforms are hard to operate. The platform team knows which team owns which namespaces, but the cluster does not, so every relationship between a team and its resources has to be maintained by hand.

This page defines what a tenant is, what it must own to be useful, and what changes when the cluster knows about it.

---

## TL;DR

| Question | Kubernetes alone | With a tenant abstraction |
|--------|-----|----------|
| Who owns this namespace? | A label, if someone applied one | A declared relationship |
| Who may access it? | Role bindings, written per namespace | Derived from tenant membership |
| What may it consume? | Quota per namespace | One budget at the tenant scope |
| What standards apply? | Whatever was applied at creation | Reconciled continuously |
| What does it cost? | Requires a tagging convention | Attributed by construction |
| What happens outside the cluster? | Configured separately per tool | Derived from the same definition |

---

## A definition

A tenant is the **unit of ownership** on a shared platform: a group of people, the resources allocated to them, and the boundaries that apply to both.

Concretely, a tenant is usually one of:

- A **development team** — the most common case on internal platforms
- A **department or business unit** — often the unit that holds the budget
- A **customer** — for vendors and service providers running workloads on behalf of others
- A **project or product** — where teams are fluid but the thing being built is not

The distinguishing property is that a tenant is *organizational*, not technical. It exists in your company before it exists in your cluster.

---

## What a tenant must own

A tenant abstraction that only groups namespaces does not earn its place. To be useful it has to carry everything that follows from ownership:

- **Membership** — the users and groups that belong to it, and at what level of access
- **Namespaces** — the ones it owns today, and the right to create more within its allocation
- **Resource allocation** — a budget, defined once for the tenant rather than per namespace
- **Policies** — network isolation, node placement, and the guardrails on what it may use
- **Standards** — the templates and metadata every one of its environments carries
- **Cost** — its share of consumption, attributed without a separate tagging scheme
- **Lifecycle** — what happens when it is created, changed, and deleted
- **External context** — its project in the GitOps tool, its path in the secrets platform

If any of these live somewhere else, they will drift from the tenant the first time membership changes.

---

## Tenant, namespace and cluster

These are three different boundaries and confusing them causes most of the argument in this area.

**A namespace** is a Kubernetes isolation boundary. It scopes names and anchors policy. It is not an organization.

**A tenant** is an organizational boundary. It owns namespaces — usually several, often across environments — plus the people, allocation and standards that go with them.

**A cluster** is an infrastructure boundary. It may host many tenants, or one.

A tenant with one namespace is common at the start and rarely stays that way: teams want `dev`, `staging` and `prod`, and developers want their own space to work in. As soon as a tenant owns more than one namespace, the difference between the two boundaries becomes operationally significant.

---

## Tenant roles

Most platforms converge on three levels of membership, because they map onto how teams actually work:

- **Owners** — accountable for the tenant. They manage its namespaces and its membership within the limits the platform team set.
- **Editors** — do the work. They deploy and manage resources inside the tenant's namespaces.
- **Viewers** — read-only. Support staff, adjacent teams, auditors.

The critical property is that membership should come from your existing identity provider groups. A tenant whose membership is maintained separately from your directory is a tenant whose access is wrong within a quarter.

---

## What changes when the cluster knows about tenants

**Onboarding becomes one object.** A new team is a tenant definition committed to Git, reviewed like any other change, applied by whatever GitOps tool you run — not a runbook.

**Access follows membership.** Someone joins a group; they get access to the tenant's namespaces. Someone leaves; they lose it. Nobody edits role bindings.

**Quota stops leaking.** A tenant-scoped budget shared across its namespaces means self-service namespace creation does not multiply the allocation.

**Standards are reconciled.** The templates and metadata a tenant's environments must carry are applied to new namespaces automatically, and corrected when they drift.

**Cost is attributable without a convention.** A namespace exists because a tenant declared it, so there is no unattributed remainder and no separate tagging scheme to maintain.

**Offboarding is a deletion.** Remove the tenant and — if you asked for it — its namespaces and external identities go with it, rather than lingering for a year.

---

## How MTO models a tenant

In [Multi-Tenant Operator](../index.md) the tenant is a Kubernetes custom resource, so it lives in Git and is reconciled continuously:

```yaml
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: bluesky
spec:
  quota: small
  accessControl:
    owners:
      users:
        - anna@aurora.org
    editors:
      groups:
        - bluesky-developers
  namespaces:
    withTenantPrefix:
      - dev
      - staging
    sandboxes:
      enabled: true
  storageClasses:
    allowed:
      - standard
```

From that one object MTO creates and maintains the namespaces, the role bindings, the quota, the network isolation, the standard metadata and the templated resources — and projects the same boundary into ArgoCD and the secrets platform. See [Tenant](../concepts/tenant.md) for the full model, and [Tenant Lifecycle Management](tenant-lifecycle-management.md) for what happens over time.

---

## Frequently Asked Questions (FAQ)

### Is a tenant the same as a namespace?

No. A namespace is a Kubernetes isolation boundary; a tenant is an organizational one that usually owns several namespaces along with membership, allocation, standards and cost.

### Can a tenant span multiple clusters?

The organizational concept does. Implementations are usually per cluster: MTO, for example, installs into one cluster and governs that cluster, so the same tenant definitions are applied to each cluster through GitOps rather than federated.

### Should a customer be a tenant, or a namespace?

A tenant. Customers accumulate namespaces, need their own allocation and standards, and are the unit you want cost attributed to — all of which are tenant properties.

### How is tenant membership usually managed?

From existing identity provider groups, mapped to tenant roles. Maintaining membership separately from your directory is the most common source of stale access.

### Does a tenant have to own more than one namespace?

No, but most end up doing so. Environments and per-developer sandboxes are the usual reasons.

---

## Keywords

Kubernetes tenant
what is a tenant in Kubernetes
tenant vs namespace
Kubernetes tenant model
multi-tenant Kubernetes platform
Kubernetes tenant abstraction
tenant RBAC Kubernetes
