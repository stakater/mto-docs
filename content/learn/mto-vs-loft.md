# MTO vs Loft (vCluster Platform)

## Introduction

Loft — now branded vCluster Platform — is the commercial platform from Loft Labs built around virtual clusters and namespaces. It is the nearest commercial comparison to Multi-Tenant Operator: both are products rather than components, both give platform teams self-service with guardrails, and both address idle-environment cost.

They start from different primitives, and that starting point shapes everything else.

---

## TL;DR

| Aspect | MTO | vCluster Platform (Loft) |
|--------|-----|----------|
| Primary primitive | Tenant in a shared cluster | Virtual cluster, and namespaces |
| Isolation | Namespace-based, policy-enforced | Virtual control plane per environment |
| Efficiency | Highest — no per-tenant control plane | Lower — a control plane per virtual cluster |
| Tenant abstraction | `Tenant` custom resource | Projects and spaces in the platform |
| Idle-environment cost | Hibernation, scheduled or on demand | Sleep mode |
| Cost attribution | Tenant and namespace showback | Platform reporting |
| Ecosystem | Kubernetes and OpenShift | Kubernetes |
| Both commercial | Yes | Yes |

---

## What is vCluster Platform?

vCluster Platform is a management layer over Loft Labs' vCluster technology. vCluster runs a virtual Kubernetes control plane inside a namespace of a host cluster; each virtual cluster has its own API server and its own CRDs, and workloads are synced down to the host's nodes.

The platform adds what a virtual cluster on its own does not have: self-service provisioning, templates for what a new environment contains, access management, and sleep mode that pauses idle environments.

### Key Characteristics

- Virtual clusters as the unit of environment
- Self-service provisioning from templates
- Sleep mode for idle environments
- Central management across clusters
- Strong fit for per-developer and per-branch environments

### Best For

- Teams that need cluster-level autonomy, including their own CRDs
- Ephemeral environments — per developer, per pull request
- Platforms where virtual clusters are already the chosen primitive

---

## What is MTO?

MTO adds a `Tenant` abstraction to a shared Kubernetes or OpenShift cluster and reconciles the cluster to match it: namespaces, RBAC from identity provider groups, quota at the tenant scope, admission guardrails, network isolation, standard metadata and templates — plus cost attribution, hibernation, and extension of the tenant boundary into ArgoCD and OpenBao or Vault.

### Key Characteristics

- One shared control plane, no per-tenant control-plane overhead
- Tenant as an organizational boundary owning many namespaces
- Guardrails enforced at admission
- Cost attributed to the tenant by construction
- Console for administrators and tenant users over the same objects
- Native OpenShift support

### Best For

- Internal platforms serving many teams
- Vendors and service providers serving many customers
- Environments where infrastructure efficiency and cost accountability are priorities
- OpenShift estates

---

## Core Architectural Difference

**vCluster Platform gives each environment its own control plane. MTO gives each tenant a governed slice of one.**

Everything else follows from that.

A virtual cluster is a stronger isolation boundary: separate API server, separate CRDs, room for a tenant to behave like a cluster administrator inside its own space. It also costs more — every virtual cluster is another control plane to run, upgrade and observe — and it does not, by itself, tell you who owns it or what it may consume.

MTO's boundary is namespace-based and enforced by policy. It is a weaker isolation boundary, and a considerably cheaper one, and the tenant model is the point rather than an addition.

---

## Detailed Comparison

### Isolation

vCluster Platform is stronger: separate API server per environment, per-environment CRDs, cluster-scoped resources that do not collide.

MTO is namespace-based. Cluster-scoped resources, including CRDs, are shared. Where tenants do not need their own CRDs — including external customers reached through a product layer, who never touch the API at all — this is usually the right trade. For a tenant that does need its own CRDs, it is not.

### Efficiency

MTO is materially more efficient. One control plane serves every tenant, so per-tenant overhead is the workloads themselves.

Each virtual cluster runs its own control plane. At a handful of environments this is negligible; at hundreds it is a real line in the budget and a real operational surface.

### The organizational model

MTO's `Tenant` is explicitly organizational: membership from identity provider groups, an allocation for the whole tenant, standards its environments carry, a cost figure, and a lifecycle from onboarding to offboarding.

vCluster Platform organizes around environments and the projects that contain them. If your unit of ownership is "a team that owns several long-lived environments", MTO's model maps onto it more directly. If it is "a developer who needs a cluster for two days", vCluster Platform's does.

### Idle environments

Both address this, and it is one of the closest comparisons between them. MTO hibernates workloads on a cron schedule or on demand, targeting namespaces by label so one schedule covers a whole tenant, and restores previous replica counts on wake. Loft's sleep mode pauses idle virtual clusters.

### Cost visibility

MTO samples usage per namespace, rolls it up to the tenant, prices it — with provider pricing on public cloud — and stores the history so periods can be compared. Because every managed namespace carries its tenant label, attribution needs no separate convention.

vCluster Platform provides platform-level reporting over its virtual clusters.

### Ecosystem

MTO supports Kubernetes and OpenShift, and on OpenShift uses `ClusterResourceQuota` natively. If you run OpenShift, that matters.

### Extending beyond the cluster

MTO projects the tenant into ArgoCD as a scoped `AppProject` and into OpenBao or Vault as a tenant path with its policies and login roles, from the same definition.

---

## What you would still assemble

vCluster Platform covers more of this ground than vCluster alone: self-service provisioning, templates and sleep mode are part of the product, so standardization and idle-environment cost are genuinely addressed. The gaps that remain against MTO are narrower and worth naming precisely:

- **An organizational tenant** — a boundary that owns several long-lived environments, its membership, its allocation and its cost, rather than the environments themselves
- **Cost attributed to that boundary** — priced and kept as history, without a labelling convention to maintain
- **GitOps tenancy** — a scoped project per tenant rather than hand-maintained ArgoCD RBAC
- **Secrets tenancy** — a path, policies and login roles per tenant, kept in step with membership
- **Interface** — something for tenant users that is not `kubectl` and YAML

MTO includes all of these, built on the same tenant definition, which is why they agree with each other. Assembled separately they are six or seven products to source, integrate and keep aligned about who a tenant is. See [what you assemble instead](kubernetes-multi-tenancy-tools.md#what-you-assemble-instead).

---

## How to Decide

### Choose vCluster Platform when

- Tenants need their own CRDs or conflicting cluster-scoped configuration
- Environments are ephemeral — per developer, per pull request
- Tenants need cluster-admin-like autonomy inside their own boundary
- Virtual clusters are already your platform primitive

### Choose MTO when

- Tenants are long-lived teams, departments or customers
- Infrastructure efficiency matters and per-tenant control planes are hard to justify
- Cost attribution per team or per customer is a requirement
- The tenant boundary must reach ArgoCD and the secrets platform
- You run OpenShift
- You want one governed cluster rather than a fleet of virtual ones

---

## Using Them Together

These are different layers, so combining them is coherent: MTO governs tenancy on the shared cluster for the majority of teams, and virtual clusters serve the minority that need control-plane autonomy. See [Deployment Models](../overview/deployment-models.md).

---

## Key Takeaways

- The comparison is commercial platform to commercial platform, but the primitives differ: virtual clusters against a governed shared cluster.
- vCluster Platform buys isolation; MTO buys efficiency and an organizational model.
- Both solve idle-environment cost — sleep mode and hibernation.
- MTO's tenant is an organizational unit; Loft's unit is closer to an environment.
- OpenShift support and cost attribution to the tenant are the clearest MTO-specific advantages; per-tenant CRDs and control-plane autonomy are the clearest Loft-specific ones.

---

## Frequently Asked Questions (FAQ)

### Is Loft the same as vCluster?

vCluster is the open-source virtual cluster technology. Loft — now vCluster Platform — is the commercial management layer around it.

### Is MTO cheaper to run than vCluster Platform?

On infrastructure, generally yes: there is no per-tenant control plane. Licensing is a separate conversation with each vendor.

### Can MTO manage virtual clusters?

No. MTO governs tenancy within a cluster. Virtual clusters are a different isolation layer, and the two are complementary rather than overlapping.

### Which is better for ephemeral environments?

Virtual clusters, generally — they are designed for environments that appear and disappear. MTO's sandboxes cover the per-developer namespace case within a tenant's boundary.

### Which is better for cost accountability?

MTO attributes consumption to a tenant by construction, because every namespace it manages carries the tenant label and cost is aggregated to that boundary.

---

## Keywords

MTO vs Loft
vCluster Platform alternative
Loft Labs Kubernetes
virtual clusters vs namespaces
Kubernetes self-service platform
multi-tenant Kubernetes platform
