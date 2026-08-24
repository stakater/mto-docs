# Kubernetes Multi-Tenancy Tools

## Introduction

Search for Kubernetes multi-tenancy tooling and you get a list that mixes categories: namespace governance operators, virtual cluster technologies, hosted control planes and commercial platforms, all described as "multi-tenancy".

They are not alternatives to each other. They operate at different layers, and choosing between them only makes sense once you know which layer your problem is at.

This page sorts the landscape.

---

## TL;DR

| Tool | Category | Layer it addresses |
|--------|-----|----------|
| Multi-Tenant Operator (MTO) | Multi-pillar platform | Governance within a cluster, plus templates, FinOps, hibernation, ecosystem integrations and a console |
| Capsule | Tenant operating model | Governance within a cluster |
| Hierarchical Namespace Controller (HNC) | Namespace organization | Policy propagation within a cluster |
| vCluster | Virtual clusters | Control-plane isolation |
| vCluster Platform / Loft | Commercial platform | Management over virtual clusters and namespaces |
| Kamaji | Hosted control planes | Control-plane isolation |
| Hypershift | Hosted control planes | Control-plane isolation, OpenShift |
| KCP | Logical control planes | API multi-tenancy, not workload isolation |

---

## The two layers

Almost every disagreement about these tools comes from mixing up two questions.

**Isolation** — how separated are tenants? Namespaces, virtual clusters, hosted control planes and dedicated clusters answer this, in increasing order of strength and cost.

**Operating model** — who owns what, who may access it, what may it consume, what standards does it meet, what does it cost, and what happens in the tools around the cluster? This applies whichever isolation model you chose.

A platform with thirty virtual clusters has exactly the same operating-model problem as one with thirty namespaces. Isolation tooling does not answer it, and governance tooling does not provide control-plane isolation.

---

## Governance within a cluster

### Multi-Tenant Operator (MTO)

MTO is a commercial platform from Stakater built on a single `Tenant` definition that drives six capability areas: **multi-tenancy**, **templates**, **FinOps**, **hibernation**, **extensions** into the surrounding ecosystem, and a **console** for both administrators and tenant users. Tenancy is the foundation the other five stand on, not the extent of the product.

- **Multi-tenancy** — namespaces, RBAC from identity provider groups, quota at the tenant scope, admission guardrails and network isolation, reconciled continuously
- **Templates** — parameterized environments, optionally enforced across a tenant or the whole cluster
- **FinOps** — usage sampled per namespace, aggregated to the tenant, priced, stored as history, with capacity planning
- **Hibernation** — idle workloads slept and woken on a schedule or on demand
- **Extensions** — the tenant boundary carried into ArgoCD, OpenBao or Vault, and developer tooling
- **Console** — a permission-aware interface over the same objects the API exposes

It appears in this section because of the first item. It is listed here only once, but it is the only entry on this page that addresses more than one layer.

Best suited to organizations running Kubernetes as an internal platform for many teams, or as a shared platform for many customers, where governance and cost accountability matter as much as isolation.

### Capsule

A CNCF Sandbox project, and the closest open-source comparison to MTO's core. Capsule introduces a `Tenant` custom resource, groups namespaces under it, and enforces per-tenant policy on namespaces, quota, network policy and admission. A proxy component lets tenant users list resources scoped to their tenant.

Best suited to teams that want namespace-based tenant governance from an open-source project and are prepared to assemble cost visibility, standardization and platform integrations separately.

See [MTO vs Capsule](mto-vs-capsule.md).

### Hierarchical Namespace Controller (HNC)

A Kubernetes SIG Multi-Tenancy project. HNC lets namespaces have parents, creates child namespaces beneath them, and propagates policy objects — RBAC, network policies, and other configured types — down the hierarchy.

It solves one specific and real problem: keeping policy consistent across a group of related namespaces. It is not a tenant model — there is no membership, allocation, cost or lifecycle concept — and it is usually a component of a platform rather than the platform.

See [MTO vs HNC](mto-vs-hnc.md).

---

## Control-plane isolation

### vCluster

An open-source project from Loft Labs that runs a virtual Kubernetes control plane inside a namespace of a host cluster. Each virtual cluster has its own API server and its own CRDs; workloads are synced down to the host's nodes.

Genuinely stronger isolation than namespaces, and a per-tenant control plane to run. It provides no tenant governance model of its own.

See [MTO vs vCluster](mto-vs-vcluster.md).

### vCluster Platform (formerly Loft)

The commercial platform from Loft Labs around virtual clusters and namespaces: self-service provisioning, templates, access management and sleep mode for idle environments.

The nearest commercial comparison to MTO, though built on a different isolation primitive — virtual clusters first, where MTO governs a shared cluster.

See [MTO vs Loft](mto-vs-loft.md).

### Kamaji

An open-source project, from the same maintainers as Capsule, that runs tenant Kubernetes control planes as pods on a management cluster, with worker nodes joining each tenant control plane. The result is real, separate clusters without dedicated control-plane machines.

See [MTO vs Kamaji](mto-vs-kamaji.md).

### Hypershift

Red Hat's hosted control planes for OpenShift: control planes run as workloads on a management cluster with worker nodes attached per hosted cluster. Same architectural idea as Kamaji, in the OpenShift ecosystem.

See [MTO vs Hypershift](mto-vs-hypershift.md).

---

## A different problem entirely

### KCP

KCP is not a Kubernetes cluster and does not schedule workloads. It provides logical control planes — workspaces — that serve Kubernetes-style APIs, aimed at multi-tenant API services and control-plane-as-a-service scenarios.

It appears in multi-tenancy searches because it is genuinely multi-tenant, but it addresses API multi-tenancy rather than workload isolation on a shared cluster. For most platform teams it is not a candidate for the same decision.

See [MTO vs KCP](mto-vs-kcp.md).

---

## What you assemble instead

Tool comparisons usually stop at tenancy, because tenancy is the feature everyone lists. That understates the decision. Tenancy is the foundation MTO's other capabilities are built on, and each of them is a product in its own right that a customer choosing differently has to source, integrate and then keep working.

| Capability | What MTO includes | What you assemble otherwise |
|--------|-----|----------|
| Tenancy | `Tenant` owning namespaces, RBAC from identity provider groups, quota at the tenant scope, admission guardrails, network isolation | A tenancy operator, or your own controllers, plus a policy engine for the guardrails |
| Standardization | Parameterized templates — manifests, Helm charts or resource references — rendered into tenant namespaces, optionally enforced, and reconciled continuously | GitOps conventions or a templating operator, plus a way to reach namespaces created after the standard was written |
| Cost | Usage sampled per namespace, aggregated to the tenant, priced with provider rates, stored so periods can be compared, with capacity planning | A cost tool, a metrics stack, a database for history, dashboards, and a labelling convention that everything depends on being applied correctly |
| Idle environments | Workloads slept and woken on a schedule or on demand, targeted by label, previous replica counts restored | Custom controllers or scheduled jobs that scale workloads down and can restore what was running |
| GitOps tenancy | An ArgoCD `AppProject` per tenant, scoped to its repositories and namespaces | ArgoCD projects and RBAC maintained by hand, kept in step with team membership |
| Secrets tenancy | A path, policies and login roles per tenant in OpenBao or Vault, derived from the tenant | Secrets-platform policy written and revised per tenant, application and access change |
| Developer tooling | Workspace and collaboration spaces that follow tenant membership | Separate configuration per tool, drifting whenever membership changes |
| Interface | A permission-aware console for administrators and tenant users over the same objects | A UI you build, or tenant users left on `kubectl` and YAML |

None of these is impossible to assemble. The cost is rarely in the first integration — it is in the seventh, and in keeping all of them agreeing with each other about who a tenant is after two years of membership changes. That is the comparison worth making, and it is the one a feature-by-feature tenancy table hides.

---

## Choosing

Work through the layers rather than the tool list.

1. **Does any tenant need its own API server or its own CRDs?** If yes, that tenant needs a virtual cluster, a hosted control plane or its own cluster. If no, namespace-based multi-tenancy is the efficient answer.
1. **Whichever you chose, who governs the tenant?** Ownership, membership, allocation, standards, lifecycle. This is where MTO and Capsule sit, and where isolation tooling has nothing to offer.
1. **Do you need cost attributed to the tenant?** Most governance tooling stops before this.
1. **Does the boundary need to reach GitOps and secrets management?** If it does, check whether the tool projects the tenant into those systems or leaves you to configure them separately.
1. **Who operates it day to day?** If tenant users need self-service without writing YAML, a console over the same objects matters.

Most platforms end up combining layers: a shared cluster governed by a tenant operating model for the majority of teams, plus stronger isolation for the few tenants that genuinely require it. See [Deployment Models](../overview/deployment-models.md).

---

## Frequently Asked Questions (FAQ)

### What is the best Kubernetes multi-tenancy tool?

There is no single best, because the tools address different layers. Decide first whether your problem is isolation or governance; the shortlist follows from that.

### Is Capsule an alternative to MTO?

It is the closest open-source comparison for namespace-based tenant governance. It covers less ground: cost attribution, hibernation, standardization tooling and a console are not part of it. See [Capsule Alternatives](capsule-alternatives.md).

### Is vCluster an alternative to MTO?

No — they operate at different layers. vCluster isolates control planes; MTO governs tenancy. They are frequently used together.

### Do I need more than one of these?

Often, yes. A governance layer plus an isolation layer is a common and sensible combination, particularly once one or two tenants need stronger isolation than the rest.

### Which of these are open source?

Capsule, HNC, vCluster, Kamaji, Hypershift and KCP are open source. MTO and vCluster Platform are commercial products.

---

## Keywords

Kubernetes multi-tenancy tools
multi-tenancy operators Kubernetes
Capsule vs MTO
vCluster alternatives
Kubernetes tenant management tools
open source Kubernetes multi-tenancy
