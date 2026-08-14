# MTO vs Capsule

## Introduction

Multi-Tenant Operator (MTO) and Capsule are the two most directly comparable tools in this space. Both add a `Tenant` abstraction to Kubernetes, both group namespaces under it, and both enforce policy on the tenant boundary within a shared cluster.

They sit at the same layer, which makes this a genuine comparison rather than a category mix-up. The differences are scope and delivery model.

---

## TL;DR

| Aspect | MTO | Capsule |
|--------|-----|----------|
| Model | Namespace-based tenancy in a shared cluster | Namespace-based tenancy in a shared cluster |
| Tenant abstraction | `Tenant` custom resource | `Tenant` custom resource |
| Licence | Commercial | Open source, CNCF Sandbox |
| Cost visibility | Included | Not included |
| Hibernation | Included | Not included |
| Standardization tooling | Templates, reconciled | Not included |
| Console | Included, for both personas | Not included |
| External integrations | ArgoCD, OpenBao/Vault, developer tooling | Not included |
| Best for | Platform teams wanting a complete platform | Teams wanting open-source tenant governance |

---

## What is Capsule?

Capsule is a CNCF Sandbox project from Clastix that implements namespace-based multi-tenancy through a `Tenant` custom resource. Namespaces belong to a tenant, and Capsule enforces the tenant's policies on them — resource quota, network policies, admission constraints and access.

It also ships a proxy component that lets tenant users list cluster-scoped resources filtered to what their tenant owns, which addresses a real gap in namespace-based tenancy: a tenant user running `kubectl get namespaces` would otherwise see nothing or need cluster-wide read access.

### Key Characteristics

- Open source, Apache-licensed, CNCF Sandbox
- Tenant custom resource owning namespaces
- Policy enforcement through admission control
- Self-service namespace creation within tenant limits
- A proxy for tenant-scoped views of cluster-scoped resources

### Best For

- Teams that require open-source tooling
- Platforms where tenant governance is the whole requirement
- Organizations comfortable assembling the surrounding capabilities themselves

---

## What is MTO?

MTO is a commercial platform from Stakater built on a single `Tenant` definition that drives six capability areas: **multi-tenancy**, **templates**, **FinOps**, **hibernation**, **extensions** into the surrounding ecosystem, and a **console** for both administrators and tenant users. Tenancy is the foundation the other five stand on, not the extent of the product.

Capsule is comparable on the first of those six. The comparison below is therefore narrow where the products overlap and wide where they do not.

### Key Characteristics

- `Tenant` custom resource owning namespaces, membership, quota and standards
- RBAC derived from existing identity provider groups
- Quota at the tenant scope, shared across the tenant's namespaces
- Admission guardrails for storage classes, ingress classes, priority classes, registries, service accounts and hostnames
- Templates that standardize environments and are reconciled continuously
- Cost attribution to the tenant boundary, with capacity planning
- Hibernation of idle environments
- Tenant boundary extended into ArgoCD and OpenBao or Vault
- A console for platform administrators and tenant users over the same objects

### Best For

- Platform teams operating Kubernetes for many internal teams
- Vendors and service providers serving many customers from shared infrastructure
- Organizations where cost accountability and standardization matter as much as isolation

---

## Core Architectural Difference

There isn't one at the isolation layer. Both are namespace-based multi-tenancy on a shared cluster, both use a tenant custom resource, and both enforce the boundary with controllers and admission control.

The difference is **scope**. Capsule governs the tenant boundary inside Kubernetes. MTO governs the tenant boundary and the operational concerns that follow from it — what environments contain, what they cost, whether they should be running, and what the tenant means in the tools around the cluster.

Put another way: Capsule answers *who owns this namespace and what may it do*. MTO answers that plus *what is in it, what does it cost, is it needed right now, and what does this tenant look like in ArgoCD and the secrets platform*.

---

## Detailed Comparison

### Tenant governance

Comparable. Both provide a tenant custom resource, namespace ownership, quota, access control and admission-enforced policy. This is the ground where a straight feature comparison is closest, and where either tool will serve.

### Access control

Both derive tenant access from users and groups. MTO's model is fixed at three levels — owners, editors and viewers — with the ability to substitute custom roles and extend the defaults, and binds directly from existing Kubernetes or OpenShift groups including those synced from an identity provider.

### Standardization

MTO includes templates: Kubernetes manifests, Helm charts or references to existing resources, rendered into tenant namespaces, optionally enforced across every namespace of one tenant or of all tenants, and kept in sync as they change.

Capsule does not provide this. Teams typically use their GitOps controller or a separate operator to distribute baseline resources.

### Cost and capacity

MTO attributes consumption to the tenant boundary, prices it — using provider pricing on public cloud — stores the history, and presents cost and capacity views.

Capsule does not address cost. Attribution is left to whatever cost tooling you run, with the labelling that implies.

### Idle environments

MTO includes hibernation: workloads scaled down on a schedule or on demand and restored on wake, targeted by label so one schedule covers a whole tenant.

Capsule does not address this.

### Beyond Kubernetes

MTO projects the tenant into ArgoCD as an `AppProject` scoped to the tenant's repositories and namespaces, and into OpenBao or Vault as a path with the policies and login roles for the tenant's people and workloads.

Capsule's scope is the cluster. GitOps and secrets tenancy are configured separately.

### Interface

MTO ships a console covering tenants, namespaces, quota, cost, capacity, templates and hibernation, permission-aware so tenant users see their own scope. It reads and writes the same objects as the API, so there is no second source of truth.

For the command line, both products solve the same RBAC limitation — a tenant user granted `list` on a cluster-scoped resource sees every instance of it, not only their own. Capsule solves it with a proxy in the request path; MTO solves it with the [`kubectl-tenant` plugin](../cli/overview.md), which reads the Tenant status and filters results client-side. No proxy to run, and ordinary `kubectl` everywhere else.

Capsule has no console.

### Licence and support

Capsule is open source with community support and commercial support available from Clastix. MTO is a commercial product with vendor support. For some organizations this decides the question before any feature comparison starts.

---

## What you assemble instead

On tenancy the two are close, and either will serve. That is why the comparison is decided almost entirely by the five pillars above — each of which is a product in its own right.

| Capability | MTO | With Capsule you would add |
|--------|-----|----------|
| Standardization | Templates, optionally enforced, reconciled continuously | GitOps conventions or a templating operator, plus a way to reach namespaces created later |
| Cost | Sampled per namespace, aggregated to the tenant, priced, stored as history | A cost tool, a metrics stack, a database, dashboards, and a labelling convention everything depends on |
| Idle environments | Hibernation on a schedule or on demand, label-targeted | Controllers or scheduled jobs that scale down and can restore what was running |
| GitOps tenancy | An ArgoCD `AppProject` per tenant, from the same definition | ArgoCD projects and RBAC maintained by hand, kept in step with membership |
| Secrets tenancy | A path, policies and login roles per tenant in OpenBao or Vault | Secrets-platform policy written and revised per tenant and per access change |
| Interface | A permission-aware console for both personas | A UI you build, or tenant users on `kubectl` and YAML |

None of that is impossible to assemble. The cost is rarely the first integration — it is the seventh, and keeping all of them agreeing about who a tenant is after two years of membership changes. [What you assemble instead](kubernetes-multi-tenancy-tools.md#what-you-assemble-instead) sets the same trade out across every tool on the market.

---

## Operational questions buyers ask

Both products are installed into an existing cluster, so the practical questions are about fit rather than features.

- **Brownfield adoption** — existing namespaces join a tenant by carrying its label, so a cluster already in production can be brought under management incrementally rather than rebuilt. See [Create Namespaces](../guides/create-namespaces.md).
- **Bring your own stack** — MTO installs a supporting stack, and each component can be pointed at one you already run instead. PostgreSQL, Prometheus, OpenCost and Dex each take `mode: Managed` or `mode: External`, so an existing Prometheus or an existing identity broker is used rather than duplicated. See [Integration Config](../concepts/integration-config.md).
- **Existing ArgoCD and secrets setup** — every extension is optional and inert until configured. If you already maintain ArgoCD `AppProjects` or Vault policies in Git, leave the integration unset and MTO does not touch them; enable it for one tenant when you want to. See [Extensions](../concepts/extensions.md).
- **Licensing** — MTO has a free Basic tier limited to two tenants and a commercial Enterprise tier. See [Pricing](../pricing.md).

---

## How to Decide

### Choose Capsule when

- Open-source licensing is a requirement or a strong preference
- Tenant governance inside the cluster is the whole problem
- You already run cost tooling, standardization and GitOps tenancy separately and are happy with them
- You have the platform engineering capacity to assemble and maintain the surrounding pieces

### Choose MTO when

- You want the tenant boundary, standardization, cost accountability and hibernation from one product
- Cost attribution per team or per customer is a requirement rather than a nice-to-have
- The tenant boundary needs to reach ArgoCD and the secrets platform
- Tenant users need self-service through an interface, not only YAML
- You are running OpenShift and want `ClusterResourceQuota`-based enforcement handled natively
- Vendor support matters

---

## Key Takeaways

- Capsule and MTO address the same layer, which makes this a real comparison rather than a category error.
- On core tenant governance they are close, and either will serve.
- MTO's scope extends past governance into standardization, cost, hibernation, external integrations and a console.
- Capsule's advantage is open-source licensing and a smaller, more focused surface.
- The decision usually comes down to licensing model and how much of the surrounding platform you want to assemble yourself.

---

## Frequently Asked Questions (FAQ)

### Is MTO a fork of Capsule?

No. They are independent implementations that arrived at a similar abstraction because it is the natural one for namespace-based multi-tenancy.

### Can Capsule and MTO run in the same cluster?

It is not advisable. Both manage tenant ownership of namespaces and enforce policy through admission control, so running them together means two controllers with overlapping claims on the same resources.

### Does Capsule support cost showback?

No. Cost attribution is outside its scope; you would pair it with separate cost tooling and maintain the labelling that tooling requires.

### Is Capsule good enough for an internal developer platform?

For the tenancy layer, often yes. An IDP usually also needs standardization, cost visibility and self-service, which you would assemble around it.

### Which is easier to operate?

Capsule has a smaller surface, which is genuinely simpler. MTO installs more — including a console, an identity broker and a cost pipeline — but installs them for you rather than leaving them as integration projects.

---

## Keywords

MTO vs Capsule
Capsule Kubernetes multi-tenancy
Capsule alternative
open source Kubernetes multi-tenancy
Kubernetes tenant operator
namespace-based multi-tenancy tools
