# Namespace-Based Multi-Tenancy in Kubernetes

## Introduction

Namespace-based multi-tenancy is the most widely used way to share a Kubernetes cluster: each tenant owns one or more namespaces, and the boundary between tenants is enforced with RBAC, resource quota, network policy and admission control.

It is the most efficient model available, and the one most platform teams should start from. It also has real limits, and knowing exactly where they are is what makes it a deliberate choice rather than a default nobody examined.

---

## TL;DR

| Aspect | Namespace-based multi-tenancy |
|--------|-----|
| Isolation boundary | Namespace, enforced by RBAC, quota, network policy, admission |
| Control plane | Shared |
| Nodes | Shared, optionally partitioned by node pool |
| Efficiency | Highest of any model |
| Suits | Any tenant that does not need its own API server — including external customers served through a product layer |
| Does not suit | Hostile tenants, or tenants needing their own CRDs |

---

## What a namespace actually isolates

A namespace scopes names and provides an attachment point for policy. What separates tenants is the policy you attach to it.

- **RBAC** — Roles and ClusterRoles bound within the namespace decide who can do what.
- **ResourceQuota and LimitRange** — cap total consumption and constrain individual objects.
- **NetworkPolicy** — restrict which pods may talk to which, since the pod network is flat by default.
- **Admission control** — validating and mutating webhooks reject or adjust what is being created, at write time.
- **Pod security standards** — constrain what workloads may ask of the node.
- **Node selection and taints** — steer or confine a tenant's workloads to particular nodes.

Each is opt-in. A namespace with none of them applied isolates almost nothing beyond object names.

---

## What a namespace does not isolate

This is the part that decides whether the model fits.

**The control plane is shared.** Every tenant talks to the same API server and the same etcd. A tenant that generates enormous API load affects everyone.

**Cluster-scoped resources are shared.** CRDs, ClusterRoles, IngressClasses, StorageClasses, PriorityClasses, admission webhook configurations — one global set. Two tenants needing different versions of the same CRD cannot both be satisfied.

**Nodes are shared by default.** Without node pools or taints, tenants' pods land on the same machines, sharing a kernel.

**The default network is flat.** Absent NetworkPolicy, any pod can reach any other pod in the cluster.

**Escalation paths exist if RBAC is loose.** Granting a tenant broad permissions — the ability to create ClusterRoleBindings, mount arbitrary host paths, or run privileged pods — breaks the boundary regardless of namespaces.

---

## Where it works well

- Development teams inside one organization
- Departments and business units on a shared enterprise platform
- Customers of a product where the vendor runs the workloads and the customer has no cluster access
- Development, test and demo environments, where efficiency matters most
- Any platform where infrastructure efficiency and a single operational surface are the priority

---

## Where it stops being enough

- A tenant **holds cluster credentials** and is untrusted or adversarial
- A tenant needs its own CRDs, or a conflicting version of a shared one
- A tenant needs cluster-admin-like autonomy inside its own boundary
- A regulatory or contractual requirement demands infrastructure separation
- A tenant's scale or lifecycle justifies its own cluster

The first point carries a condition that is easy to miss. If tenants never reach the Kubernetes API — because a portal, an API or a logical control plane sits in front — then how much you trust them says nothing about whether the cluster may be shared. Service providers and telecommunications platforms commonly serve entirely external customers from one shared cluster for exactly this reason. See [Deployment Models](../overview/deployment-models.md#when-tenants-never-touch-the-cluster-api).

For these, see [Deployment Models](../overview/deployment-models.md), which covers virtual clusters, hosted control planes and dedicated clusters, and where each fits.

---

## The operational problem nobody expects

The technical limits above are usually not what causes namespace-based multi-tenancy to fail. What causes it to fail is that the model is correct and the operation of it is manual.

A namespace is created for a team. Someone applies labels. Someone else writes the role bindings. Quota is set once. A network policy is copied from another namespace. Six months later, membership has changed, the labels are inconsistent, the quota is wrong, and nobody can say what this team costs.

Nothing here is a Kubernetes limitation. It is the absence of an object that says *this namespace belongs to this tenant, and here is what that implies* — and of a controller that keeps making it true.

---

## Making the model work

- **Give the tenant an identity.** One declarative object that owns the namespaces, the membership, the quota and the standards — so the boundary is defined once rather than reassembled per namespace.
- **Derive RBAC, do not write it.** Bind roles from tenant membership, and let membership come from your existing identity provider groups.
- **Put quota at the tenant scope.** A per-namespace quota means a tenant can multiply its budget by creating namespaces. A tenant-scoped budget shared across its namespaces does not have that hole.
- **Enforce guardrails at admission.** Which storage classes, ingress classes, priority classes, registries and hostnames a tenant may use should be rejected at write time, not reviewed later.
- **Default-deny the network.** Then open the paths that are genuinely needed.
- **Label every namespace with its tenant, automatically.** This is what makes cost attribution, monitoring and policy selection reliable, and it must not depend on anyone remembering.
- **Reconcile continuously.** Drift corrected is worth more than drift detected.

[Multi-Tenant Operator](../index.md) implements exactly this list: a `Tenant` object that owns namespaces, membership, quota and standards, controllers that keep the cluster matching it, and an admission webhook that enforces the boundary at write time.

---

## Frequently Asked Questions (FAQ)

### Is a namespace a security boundary?

Partially. It is a boundary for authorization and, with the right policy attached, for network traffic and resource consumption. It is not a boundary for the API server, the kernel, or cluster-scoped resources.

### Can two tenants use different versions of the same CRD?

No. CRDs are cluster-scoped, so all tenants share one version. This is one of the clearest signals that a tenant needs a virtual cluster or its own cluster.

### How do I stop one tenant exhausting the cluster?

Quota at the tenant scope, enforced across all of its namespaces, plus LimitRange for individual objects. Per-namespace quota alone is insufficient if tenants can create namespaces.

### Do I still need network policies?

Yes. The Kubernetes pod network is flat by default: without policy, any pod can reach any other pod regardless of namespace.

### Is namespace-based multi-tenancy cheaper than virtual clusters?

Materially, yes. There is one control plane, one monitoring stack and one upgrade cycle regardless of tenant count, and no per-tenant control-plane overhead.

---

## Keywords

namespace-based multi-tenancy
Kubernetes namespace isolation
Kubernetes RBAC multi-tenancy
Kubernetes resource quota per tenant
soft multi-tenancy Kubernetes
shared Kubernetes cluster
Kubernetes tenant boundary
