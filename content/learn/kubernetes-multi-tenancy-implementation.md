# How to Implement Kubernetes Multi-Tenancy

## Introduction

This is the practical counterpart to [Multi-Tenant Kubernetes Architecture](multi-tenant-kubernetes-architecture.md): the order to do things in, what to enforce at each step, and the decisions that are expensive to reverse later.

It assumes the common case: tenants sharing a cluster, either as internal teams using `kubectl` directly, or as external customers reached through a product layer that holds the cluster credentials on their behalf. If tenants hold cluster credentials *and* need a boundary a shared API server cannot provide, start at [Deployment Models](../overview/deployment-models.md) instead.

---

## TL;DR

| Step | Decision | Expensive to change later? |
|--------|-----|----------|
| 1 | What a tenant is | Yes |
| 2 | Where membership comes from | Yes |
| 3 | Namespace naming and ownership | Yes |
| 4 | Where quota lives | Yes |
| 5 | Which guardrails are enforced | No |
| 6 | Network default | Moderately |
| 7 | Standard metadata | Yes, if retrofitted |
| 8 | Standardization mechanism | No |
| 9 | Cost attribution | Yes, if retrofitted |
| 10 | Boundaries outside Kubernetes | No |

---

## 1. Define what a tenant is

Before choosing any tool, decide which organizational unit owns resources on your platform: a team, a department, a product, or a customer.

Get this wrong and everything downstream is wrong with it — access, allocation, cost attribution and the conversations you have about all three. The test is whether the unit you pick is the one that has a budget and an owner in your organization.

## 2. Decide where membership comes from

Bind tenant membership to your existing identity provider groups rather than maintaining lists inside the platform.

This is the difference between access that stays correct and access that is correct on the day it is written. Most platforms converge on three levels — owners, editors, viewers — which map onto accountability, doing the work, and read-only.

## 3. Establish namespace naming and ownership

Decide how namespaces are named and, more importantly, how the cluster knows which tenant owns each one.

A convention that a human applies is not enough: cost attribution, monitoring, policy selection and template distribution all depend on that label being present on every namespace, always. It should be applied by the platform, not by whoever created the namespace.

## 4. Put quota at the tenant scope

If tenants can create namespaces — and they should be able to — a per-namespace quota is not a budget, because a tenant can multiply it by creating namespaces.

Define one allocation for the tenant, shared across all of its namespaces. On OpenShift this maps to `ClusterResourceQuota`; elsewhere it requires aggregating per-namespace quota at admission.

Pair it with `LimitRange` so individual objects have sensible defaults and ceilings.

## 5. Enforce guardrails at admission

Decide what a tenant may use, and reject the rest at write time rather than reviewing it afterwards:

- Which **storage classes** it may claim
- Which **ingress classes** it may use, and which **hostnames** it may claim
- Which **image registries** it may pull from
- Which **priority classes** it may set
- Which **service accounts** are denied

Each should be off by default and grant nothing until configured — a tenant must never gain a permission because someone forgot to restrict it.

## 6. Default-deny the network

The Kubernetes pod network is flat: without policy, any pod can reach any other pod in the cluster.

Start from deny between tenants and open the paths that are genuinely needed. Retrofitting this onto a cluster full of workloads that assume flat networking is considerably harder than starting from it.

## 7. Standardize metadata

Decide the labels and annotations every managed namespace carries — tenant name at minimum, plus whatever your monitoring, network policy and cost tooling select on.

Apply them automatically. Metadata that depends on people remembering is metadata you cannot build on.

## 8. Choose a standardization mechanism

Every environment needs a baseline: network policies, image pull secrets, monitoring configuration, application scaffolding.

Whatever mechanism you choose, the requirement is that it applies to namespaces created *after* the standard was written, and corrects drift rather than only detecting it. Templates that render at creation time and are never reconciled produce a baseline that slowly stops being true.

## 9. Attribute cost from the start

Retrofitting cost attribution means retrofitting a labelling convention onto everything already running.

If every namespace carries its tenant from creation, attribution is a property of the model. Then measure rather than estimate: sample actual usage and requests per namespace, roll up to the tenant, price it, and store the history so periods can be compared.

## 10. Extend the boundary beyond Kubernetes

The cluster is rarely the whole platform. Decide early how the tenant boundary reaches:

- **GitOps** — a project per tenant, scoped to the repositories it may deploy from and the namespaces it may deploy into
- **Secrets management** — a path, roles and policies per tenant
- **Developer tooling** — workspaces and collaboration spaces that follow tenant membership

Each of these configured by hand is another system that drifts from the tenant the moment membership changes.

---

## Build or adopt

Everything above can be assembled from Kubernetes primitives plus controllers you write. Teams regularly start down that path, because a first version arrives quickly and convincingly.

The cost is never in getting it working. It is in the continuous reconciliation, the admission webhook sitting in the write path of every workload, the identity provider integration, the cost pipeline with storage and history, and keeping all of it correct across Kubernetes upgrades. For scale: MTO has been in continuous development since December 2020 — more than five years, across eight major version series — and tenancy is one of its six capability areas.

The question is therefore not whether you could build it. It is whether a multi-year commitment to platform tenancy is the best use of a team whose product is something else.

[Multi-Tenant Operator](../index.md) implements this list as a product: a `Tenant` custom resource, controllers that reconcile namespaces, RBAC, quota, metadata and templates, an admission webhook enforcing the guardrails, cost attribution to the tenant boundary, hibernation for idle environments, and extension into ArgoCD and OpenBao or Vault — with a console over the same objects.

---

## A minimal starting point

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

That covers steps 1 through 5 for one tenant. See [Create a Tenant](../guides/create-tenant.md) to run it, and [Integration Config](../concepts/integration-config.md) for the cluster-wide policy that steps 6 through 10 configure once.

---

## Frequently Asked Questions (FAQ)

### What is the first thing to get right?

What a tenant is. Access, allocation and cost attribution all derive from it, and changing it later means changing all three.

### Can I implement multi-tenancy with plain Kubernetes?

Yes, with namespaces, RBAC, quota, network policy and admission control. The primitives are sufficient; the work is in operating them consistently as teams, namespaces and standards multiply.

### Where do most implementations go wrong?

Governance by convention — namespaces created by hand, labels applied when someone remembers, quota set once. Nothing is enforced, so the environment drifts from the day it is created.

### Do I need an admission webhook?

If you want guardrails that actually hold, yes. Controllers reconcile what a tenant owns; only admission can reject a request that falls outside the boundary at the moment it is made.

### How long does this take to build?

The first working version is quick. Reconciliation, identity integration, cost attribution and keeping it correct across upgrades are where the time goes — which is the case for adopting rather than building, unless tenancy is your product.

---

## Keywords

how to implement Kubernetes multi-tenancy
Kubernetes multi-tenancy setup
Kubernetes RBAC per tenant
Kubernetes quota per tenant
multi-tenant cluster configuration
Kubernetes admission control multi-tenancy
