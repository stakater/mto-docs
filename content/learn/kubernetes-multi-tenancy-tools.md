# Kubernetes Multi-Tenancy Tools

## Introduction

Search for Kubernetes multi-tenancy tooling and you get a list that mixes categories: namespace governance operators, virtual cluster technologies, hosted control planes and commercial platforms, all described as "multi-tenancy".

They are not alternatives to each other. They operate at different layers, and choosing between them only makes sense once you know which layer your problem is at.

This page sorts the landscape.

---

## TL;DR

| Tool | Category | Layer it addresses |
|--------|-----|----------|
| Multi-Tenant Operator (MTO) | Tenant operating model | Governance within a cluster |
| Capsule | Tenant operating model | Governance within a cluster |
| Hierarchical Namespace Controller (HNC) | Namespace organization | Policy propagation within a cluster |
| vCluster | Virtual clusters | Control-plane isolation |
| vCluster Platform / Loft | Commercial platform | Management over virtual clusters and namespaces |
| Kamaji | Hosted control planes | Control-plane isolation |
| HyperShift | Hosted control planes | Control-plane isolation, OpenShift |
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

A commercial operator from Stakater that adds a `Tenant` abstraction to Kubernetes and OpenShift and reconciles the cluster to match it: namespaces, RBAC from identity provider groups, quota at the tenant scope, admission guardrails, network isolation, standard metadata and templates.

It also covers the layers most governance tooling leaves out — cost attribution to the tenant boundary, hibernation of idle environments, extension of the tenant boundary into ArgoCD and OpenBao or Vault, and a console for both administrators and tenant users over the same objects.

Best suited to organizations running Kubernetes as an internal platform for many teams, or as a shared platform for many customers, where governance and cost accountability matter as much as isolation.

### Capsule

A CNCF Sandbox project from Clastix, and the closest open-source comparison to MTO's core. Capsule introduces a `Tenant` custom resource, groups namespaces under it, and enforces per-tenant policy on namespaces, quota, network policy and admission. A proxy component lets tenant users list resources scoped to their tenant.

Best suited to teams that want namespace-based tenant governance from an open-source project and are prepared to assemble cost visibility, standardization and platform integrations separately.

See [MTO vs Capsule](mto-vs-capsule.md).

### Hierarchical Namespace Controller (HNC)

A Kubernetes SIG Multi-Tenancy project. HNC lets namespaces have parents, creates subnamespaces beneath them, and propagates policy objects — RBAC, network policies, and other configured types — down the hierarchy.

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

A Clastix project that runs tenant Kubernetes control planes as pods on a management cluster, with worker nodes joining each tenant control plane. The result is real, separate clusters without dedicated control-plane machines.

See [MTO vs Kamaji](mto-vs-kamaji.md).

### HyperShift

Red Hat's hosted control planes for OpenShift: control planes run as workloads on a management cluster with worker nodes attached per hosted cluster. Same architectural idea as Kamaji, in the OpenShift ecosystem.

See [MTO vs HyperShift](mto-vs-hypershift.md).

---

## A different problem entirely

### KCP

KCP is not a Kubernetes cluster and does not schedule workloads. It provides logical control planes — workspaces — that serve Kubernetes-style APIs, aimed at multi-tenant API services and control-plane-as-a-service scenarios.

It appears in multi-tenancy searches because it is genuinely multi-tenant, but it addresses API multi-tenancy rather than workload isolation on a shared cluster. For most platform teams it is not a candidate for the same decision.

See [MTO vs KCP](mto-vs-kcp.md).

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

Capsule, HNC, vCluster, Kamaji, HyperShift and KCP are open source. MTO and vCluster Platform are commercial products.

---

## Keywords

Kubernetes multi-tenancy tools
multi-tenancy operators Kubernetes
Capsule vs MTO
vCluster alternatives
Kubernetes tenant management tools
open source Kubernetes multi-tenancy
