# Kubernetes Multi-Tenancy and MTO Comparisons

This section explores Kubernetes multi-tenancy concepts, architecture patterns, and comparisons between **Multi-Tenant Operator (MTO)** and other approaches or tools used to implement multi-tenant platforms.

The goal is to help platform engineers understand the design options and when each one makes sense — including where MTO is not the right answer.

---

## Understanding Kubernetes Multi-Tenancy

Before evaluating tools, it is worth being precise about the concepts.

- [Kubernetes Multi-Tenancy](kubernetes-multi-tenancy.md)
  Multi-tenancy models, soft against hard tenancy, and the failure modes that show up in practice.

- [Namespace-Based Multi-Tenancy](namespace-based-multi-tenancy.md)
  What a namespace actually isolates, what it does not, and how to make the model hold.

- [What is a Tenant in Kubernetes?](kubernetes-tenants.md)
  Why Kubernetes has no tenant concept, and what a tenant must own to be useful.

- [Tenant Lifecycle Management](tenant-lifecycle-management.md)
  Onboarding, membership changes, growth, dormancy and offboarding.

---

## Multi-Tenant Kubernetes Architecture

Designing a platform for multiple teams or customers needs clear architectural patterns.

- [Multi-Tenant Kubernetes Architecture](multi-tenant-kubernetes-architecture.md)
  The layers a complete platform needs, a reference architecture, and the common anti-patterns.

- [How to Implement Kubernetes Multi-Tenancy](kubernetes-multi-tenancy-implementation.md)
  A practical order of work, and which decisions are expensive to reverse.

---

## Kubernetes Multi-Tenancy Tools

- [Kubernetes Multi-Tenancy Tools](kubernetes-multi-tenancy-tools.md)
  The landscape, sorted by the layer each tool addresses rather than by name.

The distinction that matters throughout: **isolation** decides how separated tenants are, while the **operating model** decides who owns what, what they may consume, what standards apply and what it costs. Most tools do one or the other.

---

## Comparisons at the same layer

These tools govern tenancy within a cluster, as MTO does, so they are directly comparable.

- [MTO vs Capsule](mto-vs-capsule.md)
- [MTO vs Hierarchical Namespace Controller (HNC)](mto-vs-hnc.md)
- [Capsule Alternatives](capsule-alternatives.md)

---

## Comparisons at the isolation layer

These technologies isolate control planes. They are frequently described as alternatives to MTO and are better understood as complements — they answer a different question, and the governance question survives whichever one you choose.

- [MTO vs vCluster](mto-vs-vcluster.md)
- [MTO vs Loft (vCluster Platform)](mto-vs-loft.md)
- [MTO vs Kamaji](mto-vs-kamaji.md)
- [MTO vs HyperShift](mto-vs-hypershift.md)
- [MTO vs KCP](mto-vs-kcp.md)

---

## Choosing the Right Approach

The factors that usually decide it:

- platform scale, and how many tenants there will be
- isolation requirements, and whether tenants are trusted
- operational complexity you are willing to carry
- governance and policy enforcement
- cost accountability
- tenant lifecycle automation

[Deployment Models](../overview/deployment-models.md) covers the same ground from the product side: shared clusters, virtual clusters, dedicated clusters, and how to combine them.
