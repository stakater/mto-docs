# MTO vs Kamaji

## Introduction

Kamaji is an open-source project from Clastix that runs tenant Kubernetes control planes as pods on a management cluster, with worker nodes joining each tenant control plane. It is the upstream-Kubernetes counterpart to the hosted-control-plane idea.

Like every hosted-control-plane technology, Kamaji answers an isolation question. Multi-Tenant Operator answers a governance question. Comparing them directly only makes sense once that split is clear.

---

## TL;DR

| Aspect | MTO | Kamaji |
|--------|-----|----------|
| Unit given to a tenant | Namespaces within a cluster | A whole Kubernetes cluster |
| Isolation | Namespace, policy-enforced | Full cluster, separate control plane |
| Control plane | Shared | One per tenant, running as pods on a management cluster |
| Nodes | Shared, optionally partitioned | Dedicated per tenant cluster |
| Efficiency | Highest | Higher than standalone clusters, lower than shared |
| Governance model | Tenant ownership, access, quota, standards, cost | Cluster provisioning and lifecycle |
| Licence | Commercial | Open source |

---

## What is Kamaji?

Kamaji runs the control plane of each tenant cluster as ordinary pods on a management cluster, rather than on dedicated control-plane machines. Worker nodes join the tenant control plane, giving each tenant a real Kubernetes cluster that passes upstream conformance without the usual per-cluster control-plane cost.

It comes from Clastix, the same organization behind Capsule — which is a useful signal about how these layers relate. One product isolates control planes; the other governs tenancy within a cluster. They are deliberately separate things.

### Key Characteristics

- Tenant control planes as pods on a management cluster
- Dedicated worker nodes per tenant cluster
- Real Kubernetes clusters that pass upstream conformance
- Full cluster-admin autonomy for the tenant
- Open source

### Best For

- Tenants requiring their own Kubernetes cluster
- Cluster-as-a-service and managed Kubernetes platforms
- Tenants needing cluster-admin rights or their own CRDs
- Regulatory or contractual isolation requirements

---

## Core Architectural Difference

**Kamaji gives a tenant a cluster. MTO gives a tenant a governed part of one.**

Kamaji makes per-tenant clusters affordable enough to be a realistic default. What it does not do — and does not attempt — is model the tenant: who belongs to it, what it may consume, what standards its environments meet, what it costs, and what it means in the tools around the cluster.

Those questions arrive after the cluster exists, and they arrive again inside any tenant cluster that serves more than one team.

---

## Detailed Comparison

### Isolation

Kamaji is decisively stronger. A tenant cluster has its own API server, its own etcd or equivalent data store, its own CRDs and its own nodes. A tenant can be cluster-admin without affecting anyone else.

MTO's boundary is namespace-based and policy-enforced — appropriate for tenants inside one trust boundary, insufficient for a tenant that needs its own CRDs or genuine cluster-admin rights.

### Efficiency

MTO is the more efficient model: one control plane and one operational surface for every tenant.

Kamaji reduces per-cluster overhead substantially compared with standalone clusters, but each tenant still has a control plane consuming management-cluster capacity and dedicated worker nodes.

### Operational surface

With MTO you operate one cluster. With Kamaji you operate a management cluster and a fleet of tenant clusters, each with its own upgrade cycle and configuration.

### Governance

MTO models tenants, derives RBAC from identity provider groups, allocates quota at the tenant scope, enforces admission guardrails, standardizes environments with templates, attributes cost to the tenant, hibernates idle workloads and extends the tenant boundary into ArgoCD and OpenBao or Vault.

Kamaji provisions and manages control planes. What happens inside a tenant cluster is not its concern.

### When the tenant cluster is itself shared

A Kamaji tenant cluster is frequently handed to a department rather than an individual. The moment several teams share it, the shared-cluster governance problem reappears inside it — and MTO is installable there like in any other cluster.

---

## How to Decide

### Choose MTO when

- Tenants are teams, departments or customers inside one trust boundary
- Infrastructure efficiency matters and per-tenant control planes are hard to justify
- The requirement is governance, standardization and cost accountability
- You want one cluster to operate rather than a fleet

### Choose Kamaji when

- Tenants require their own Kubernetes cluster
- A tenant needs cluster-admin rights or its own CRDs
- You are building a managed Kubernetes or cluster-as-a-service offering
- Regulatory or contractual requirements demand cluster-level separation

---

## Using Them Together

The layers compose:

- Kamaji provides clusters to the tenants whose isolation requirement justifies one.
- MTO governs tenancy inside any cluster shared by more than one team, including tenant clusters.

That gives one tenant operating model across the estate rather than governance on the shared cluster and none on the provisioned ones.

---

## Key Takeaways

- Kamaji is an isolation technology; MTO is an operating model.
- Kamaji makes per-tenant clusters affordable; it does not make governance unnecessary.
- A tenant cluster shared by several teams has the same governance problem as any shared cluster.
- MTO is the more efficient answer where tenants do not need their own control plane.
- Kamaji and HyperShift address the same architectural idea — Kamaji for upstream Kubernetes, HyperShift for OpenShift.

---

## Frequently Asked Questions (FAQ)

### Is Kamaji a multi-tenancy solution?

It is an isolation solution: a cluster per tenant, run affordably. It does not model tenants, membership, allocation, standards or cost.

### How does Kamaji differ from HyperShift?

Same architectural idea — control planes as workloads on a management cluster. Kamaji targets upstream Kubernetes; HyperShift targets OpenShift. See [MTO vs HyperShift](mto-vs-hypershift.md).

### Kamaji and Capsule are both from Clastix. Do they compete?

No, and that is instructive: Kamaji isolates control planes, Capsule governs tenancy within a cluster. They are separate products because they address separate layers — the same split as Kamaji and MTO.

### Can MTO run inside a Kamaji tenant cluster?

A tenant cluster is an ordinary Kubernetes cluster, so the usual installation applies. Whether it is worth doing depends on whether that cluster is shared by more than one team.

### Which is cheaper?

MTO, materially — there is no per-tenant control plane and no per-tenant node pool. Kamaji is cheaper than standalone clusters, not cheaper than sharing one.

---

## Keywords

MTO vs Kamaji
Kamaji hosted control planes
Clastix Kamaji
cluster as a service Kubernetes
tenant control planes
managed Kubernetes multi-tenancy
