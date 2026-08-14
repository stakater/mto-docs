# Kubernetes Multi-Tenancy: Concepts, Models and Best Practices

## Introduction

Kubernetes multi-tenancy means running workloads that belong to different teams, departments or customers on shared Kubernetes infrastructure, with boundaries between them that actually hold.

Kubernetes ships the primitives — namespaces, RBAC, ResourceQuota, NetworkPolicy, admission control — but it does not ship a tenancy model. Deciding what a tenant *is*, how strongly tenants must be separated, and who operates the boundary is left to the platform team.

This page covers the models, where each one is appropriate, and the failure modes that show up in practice.

---

## TL;DR

| Model | Isolation boundary | Efficiency | Typical use |
|--------|-----|----------|----------|
| Namespace-based | Namespace, RBAC, quota, network policy | Highest | Internal teams, and external customers served through a product layer |
| Virtual clusters | Separate API server per tenant | High | Teams needing CRD or cluster-scoped autonomy |
| Hosted control planes | Control plane per tenant, shared infrastructure | Medium | Cluster-as-a-service platforms |
| Cluster per tenant | Whole cluster | Lowest | Regulatory separation, or adversarial tenants holding cluster credentials |

Most organizations do not pick one. They pick a default and make exceptions.

---

## What is a tenant?

A tenant is the unit of ownership on your platform — the answer to "whose is this, and what may it consume?"

In practice a tenant is usually one of:

- A **development team** inside one organization
- A **department or business unit** with its own budget
- A **customer** of a product you run on Kubernetes
- An **environment family** belonging to one of the above

The important property is that a tenant owns more than one thing. It has people, namespaces, a resource allocation, standards its environments must meet, a cost, and usually access to platform services outside Kubernetes. See [What is a Tenant in Kubernetes?](kubernetes-tenants.md) for the full concept.

---

## Soft and hard multi-tenancy

For tenants who can reach the Kubernetes API, the distinction that drives every other decision is how much you trust them.

**Soft multi-tenancy** assumes tenants are not actively hostile. Teams inside one company, departments, or customers under contract. Tenants share a control plane and nodes; the boundary is enforced by RBAC, quota, network policy and admission control. This is the common case, and it is where namespace-based multi-tenancy belongs.

**Hard multi-tenancy** assumes a tenant may actively try to escape its boundary. Here a shared API server is a shared attack surface, and the answer is separate control planes or separate clusters — accepting the cost that comes with them.

### The question before that one

Trust only decides the answer for tenants who can reach the Kubernetes API. Before asking how much you trust a tenant, ask whether the tenant talks to the cluster at all:

- **Tenants use `kubectl`** — the cluster boundary is the boundary the tenant experiences, and their trustworthiness decides the model. Typical of internal platforms.
- **Tenants use a product** — a portal, an API or a logical control plane in front, with no cluster credentials issued. The shared cluster is then an implementation detail behind your product, and the trust question moves to the product layer.

The second shape is how most service providers, SaaS vendors and telecommunications platforms serve external customers, and it is why "our tenants are external" does not by itself require hard multi-tenancy.

Being honest about which situation you are in is the single most useful thing you can do early. Most platforms need soft multi-tenancy and buy hard multi-tenancy by accident, through cluster sprawl.

---

## The models

### Namespace-based multi-tenancy

Tenants share one cluster. Each tenant owns namespaces; RBAC scopes access, quota caps consumption, network policy restricts traffic, and admission control rejects what falls outside the boundary.

- **Strengths** — highest infrastructure efficiency, one control plane to operate, one upgrade cycle, native Kubernetes experience for users.
- **Limits** — tenants share an API server and nodes. Cluster-scoped resources, including CRDs, are shared.

See [Namespace-Based Multi-Tenancy](namespace-based-multi-tenancy.md).

### Virtual clusters

Each tenant gets a virtual Kubernetes control plane running inside a host cluster, with workloads scheduled onto the host's nodes.

- **Strengths** — API-level isolation, per-tenant CRDs, cluster-admin-like autonomy inside the tenant's own boundary.
- **Limits** — another control plane per tenant to run and upgrade, and the underlying nodes are still shared.

See [MTO vs vCluster](mto-vs-vcluster.md).

### Hosted control planes

The control plane for each tenant cluster runs as workloads on a management cluster, with dedicated worker nodes attached.

- **Strengths** — genuine per-tenant clusters without dedicated control-plane hardware.
- **Limits** — a fleet to operate, and the tenant model still has to be built on top.

See [MTO vs HyperShift](mto-vs-hypershift.md) and [MTO vs Kamaji](mto-vs-kamaji.md).

### Cluster per tenant

Complete separation, and complete duplication of operational cost — every cluster is another control plane, monitoring stack, upgrade cycle and on-call surface.

Appropriate for regulatory boundaries, adversarial workloads holding cluster credentials, or tenants whose scale justifies it. Expensive as a default.

---

## Isolation is not the whole problem

Choosing an isolation model answers *how separated are tenants*. It does not answer:

- Who belongs to this tenant, and what happens when someone joins or leaves?
- Which namespaces does it own, and who creates the next one?
- What may it consume, and what happens when it asks for more?
- What standards must its environments meet, and who enforces them?
- What does it cost?
- What happens in ArgoCD, in the secrets platform, and in the tools around the cluster?

These are questions about the **tenant operating model**, and they arrive whether you chose namespaces, virtual clusters or dedicated clusters. A platform with thirty virtual clusters has exactly the same governance problem as one with thirty namespaces — it has simply spent more on isolation first.

This is the layer [Multi-Tenant Operator](../index.md) addresses.

---

## Common failure modes

**Governance by convention.** Namespaces are created by hand, labels are applied when someone remembers, quota is set once and never revisited. The environment drifts from the day it is created.

**RBAC written by hand.** Role bindings are copied between namespaces, membership changes are missed, and nobody can say with confidence who has access to what.

**Cluster sprawl as a substitute for governance.** Giving each team its own cluster looks like isolation. It is usually a way of avoiding the governance problem at considerable expense.

**Unattributable cost.** Cost allocation depends on a labelling convention nobody applies consistently, so the bill stays one number and the conversation stays generic.

**Boundaries that stop at the API server.** The cluster is properly divided while the GitOps controller and the secrets platform remain shared and separately administered.

---

## Best practices

- **Decide what a tenant is before choosing a tool.** The tool follows the model, not the reverse.
- **Establish who holds cluster credentials before debating trust.** Tenants reached through a product layer never touch the API server, so their trustworthiness does not decide the isolation model. Do not pay for hard multi-tenancy you do not need — or assume soft multi-tenancy is enough when a tenant with API access is genuinely adversarial.
- **Make the tenant a declarative object.** If the boundary lives in Git and is continuously reconciled, drift is corrected rather than discovered.
- **Enforce at admission, not in documentation.** A standard that is only written down is a standard that is only sometimes met.
- **Attribute cost from the start.** Retrofitting attribution onto an established cluster means retrofitting a labelling convention onto everything already running.
- **Extend the boundary to the tools around the cluster.** One tenant definition, not four systems kept in sync by hand.

---

## Frequently Asked Questions (FAQ)

### Is namespace-based multi-tenancy secure enough?

For tenants who hold cluster credentials, it is sufficient when they are not adversarial — teams, departments, contracted customers — provided RBAC, quota, network policy and admission control are actually enforced rather than documented. For adversarial tenants with API access, a shared API server is a shared attack surface and you want separate control planes.

For tenants who never receive cluster credentials, the question does not arise in the same form: they cannot reach the API server, so the boundary that matters is the one your product layer enforces.

### What is the difference between soft and hard multi-tenancy?

Soft multi-tenancy assumes tenants are not adversarial and separates them with Kubernetes policy. Hard multi-tenancy assumes they might be, and separates them at the control plane or cluster level.

### Do virtual clusters replace namespace-based multi-tenancy?

No. They provide stronger API isolation, and they leave the tenant operating model — ownership, access, quota, standards, cost — entirely unsolved. The two operate at different layers.

### How many tenants can one cluster support?

There is no single number: it depends on workload density, node capacity, API server load and how many objects each tenant creates. The practical limit is usually operational rather than technical — how well the platform team can govern what is there.

### Does Kubernetes have a built-in tenant concept?

No. Kubernetes has namespaces and RBAC. The tenant abstraction — one object that owns namespaces, membership, quota, standards and cost — has to be added.

---

## Keywords

Kubernetes multi-tenancy
multi-tenant Kubernetes
soft multi-tenancy
hard multi-tenancy
Kubernetes tenant isolation
namespace isolation Kubernetes
platform engineering Kubernetes
multi-tenant Kubernetes architecture
