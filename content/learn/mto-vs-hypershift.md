# MTO vs Hypershift

## Introduction

Hypershift is Red Hat's hosted control planes project for OpenShift: the control plane of a hosted cluster runs as workloads on a management cluster, with worker nodes attached to it. It is the technology behind hosted-control-plane offerings in the OpenShift ecosystem.

Both Hypershift and Multi-Tenant Operator appear in OpenShift multi-tenancy discussions. They answer different questions, and OpenShift teams often end up using both.

---

## TL;DR

| Aspect | MTO | Hypershift |
|--------|-----|----------|
| Unit given to a tenant | Namespaces within a cluster | A whole OpenShift cluster |
| Isolation | Namespace, policy-enforced | Full cluster, separate control plane |
| Control plane | Shared | One per hosted cluster, running on a management cluster |
| Nodes | Shared, optionally partitioned | Dedicated per hosted cluster |
| Efficiency | Highest | Higher than standalone clusters, lower than shared |
| Governance model | Tenant ownership, access, quota, standards, cost | Cluster provisioning and lifecycle |
| Ecosystem | Kubernetes and OpenShift | OpenShift |

---

## What is Hypershift?

Hypershift decouples an OpenShift cluster's control plane from its data plane. Instead of dedicating three control-plane machines to every cluster, the control plane runs as pods on a shared management cluster, and worker nodes join it.

The result is a real, separate OpenShift cluster per tenant, at meaningfully lower cost and faster provisioning than standalone clusters — while keeping the strongest isolation boundary available short of separate infrastructure.

### Key Characteristics

- Control planes as workloads on a management cluster
- Dedicated worker nodes per hosted cluster
- Fast cluster provisioning
- Full cluster-admin autonomy for the tenant
- Strong isolation, including separate CRDs and cluster-scoped resources

### Best For

- Tenants requiring their own OpenShift cluster
- Regulatory or contractual isolation requirements
- Cluster-as-a-service platforms
- Tenants needing cluster-admin rights

---

## Core Architectural Difference

**Hypershift gives a tenant a cluster. MTO gives a tenant a governed part of one.**

That is the whole comparison, and it is a decision about isolation, not about governance.

Hypershift makes per-tenant clusters affordable enough to be a realistic default in a way standalone clusters never were. What it does not do is answer the questions that arrive once a tenant has its cluster: who belongs to this tenant, what may they consume, what standards must their environments meet, what does this cost, and what happens inside that cluster when three teams share it.

Those are operating-model questions, and they persist regardless of how the isolation was achieved.

---

## Detailed Comparison

### Isolation

Hypershift is decisively stronger. A hosted cluster has its own API server, its own CRDs, its own cluster-scoped resources and its own nodes. A tenant can be cluster-admin without affecting anyone else.

MTO's boundary is namespace-based and policy-enforced: sufficient wherever tenants do not hold cluster credentials of their own, or hold them without needing their own CRDs or cluster-admin rights; insufficient where they do.

### Cost and density

MTO is the more efficient model by a wide margin: one control plane, one monitoring stack and one upgrade cycle for all tenants.

Hypershift reduces the cost of per-tenant clusters substantially compared with standalone clusters, but each hosted cluster still has a control plane consuming management-cluster capacity and dedicated worker nodes.

### Operational surface

With MTO you operate one cluster. With Hypershift you operate a management cluster plus a fleet of hosted clusters — each with its own upgrades, monitoring and configuration drift.

### Governance

This is where they stop competing. MTO models tenants, derives RBAC from identity provider groups, allocates quota at the tenant scope, enforces guardrails at admission, standardizes environments, attributes cost, hibernates idle workloads and extends the tenant boundary into ArgoCD and OpenBao or Vault.

Hypershift provisions and manages the lifecycle of clusters. What happens inside one is not its concern.

### Inside a hosted cluster

If a hosted cluster serves a single small team, it may need no further tenancy model. If it serves several teams — which is common, since the hosted cluster is usually given to a department rather than an individual — the shared-cluster governance problem reappears inside it, and MTO is installable there like in any other OpenShift cluster.

---

## What the isolation layer leaves you to assemble

Hypershift hands a tenant a cluster. Everything that makes that cluster a governed platform is still to be built, and built again for each hosted cluster shared by more than one team:

- **Tenancy** — who owns this environment, who may access it, and what it may consume
- **Standardization** — the baseline every environment carries, applied to the ones created later and corrected when it drifts
- **Cost** — consumption attributed to an organizational owner, priced and kept as history
- **Idle environments** — scheduled sleep and wake, with previous replica counts restored
- **GitOps tenancy** — a scoped project per tenant rather than hand-maintained ArgoCD RBAC
- **Secrets tenancy** — a path, policies and login roles per tenant, kept in step with membership
- **Interface** — something for tenant users that is not `kubectl` and YAML

MTO includes all of these, built on the same tenant definition, which is why they agree with each other. Assembled separately they are six or seven products to source, integrate and keep aligned about who a tenant is. See [what you assemble instead](kubernetes-multi-tenancy-tools.md#what-you-assemble-instead).

---

## How to Decide

### Choose MTO when

- Tenants do not need their own API server — including external customers reached through a product layer
- Infrastructure efficiency matters
- The requirement is governance, standardization and cost accountability
- You want one cluster to operate rather than a fleet

### Choose Hypershift when

- Tenants require their own OpenShift cluster
- A tenant needs cluster-admin rights or its own CRDs
- Regulatory or contractual requirements demand cluster-level separation
- You are building a cluster-as-a-service platform

---

## Using Them Together

This is the common outcome on larger OpenShift estates, and the two layers compose cleanly:

- Hypershift provides clusters to the tenants whose isolation requirement justifies one.
- MTO governs tenancy inside the clusters that serve more than one team — including hosted ones.

The result is a consistent tenant operating model across both, rather than one governance model for the shared cluster and none for the hosted ones.

---

## Key Takeaways

- Hypershift is an isolation technology; MTO is an operating model. Different layers.
- Hypershift makes per-tenant clusters affordable; it does not make governance unnecessary.
- A hosted cluster shared by several teams has the same governance problem as any shared cluster.
- MTO remains the more efficient answer where tenants do not need their own control plane.
- On OpenShift estates the two are frequently deployed together.

---

## Frequently Asked Questions (FAQ)

### Is Hypershift a multi-tenancy solution?

It is an isolation solution. It gives each tenant a cluster; it does not model tenants, their membership, allocation, standards or cost.

### Can MTO run inside a Hypershift hosted cluster?

A hosted cluster is an OpenShift cluster, so the usual installation applies. If the hosted cluster serves more than one team, governing it is the same problem as governing any shared cluster.

### Which is cheaper?

MTO, materially — there is no per-tenant control plane and no per-tenant node pool. Hypershift is cheaper than standalone clusters, not cheaper than sharing one.

### When is a hosted cluster the right answer?

When a tenant genuinely needs cluster-admin rights, its own CRDs, or separation that a shared API server cannot provide.

### Is Hypershift OpenShift-only?

It is an OpenShift project. Kamaji addresses the same architectural idea for upstream Kubernetes — see [MTO vs Kamaji](mto-vs-kamaji.md).

---

## Keywords

MTO vs Hypershift
hosted control planes OpenShift
hosted control planes Kubernetes
OpenShift multi-tenancy
OpenShift tenant isolation
cluster as a service OpenShift
