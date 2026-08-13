# Kubernetes Multi-Tenancy and MTO Comparisons

This section explores Kubernetes multi-tenancy concepts, architecture patterns, and comparisons between **Multi-Tenant Operator (MTO)** and other approaches or tools used to implement multi-tenant platforms.

The goal is to help platform engineers understand different design options and when each approach makes sense.

---

## Understanding Kubernetes Multi-Tenancy

Before evaluating tools, it is important to understand the core concepts behind multi-tenancy in Kubernetes.

- [Kubernetes Multi-Tenancy](kubernetes-multi-tenancy.md)  
  Overview of multi-tenancy models and common approaches.

- [Namespace-Based Multi-Tenancy](namespace-based-multi-tenancy.md)  
  How namespace isolation works and its limitations.

- [What is a Tenant in Kubernetes?](kubernetes-tenants.md)  
  Explanation of the tenant concept in Kubernetes platforms.

- [Tenant Lifecycle Management](tenant-lifecycle-management.md)  
  How tenant provisioning, governance, and lifecycle automation work.

---

## Multi-Tenant Kubernetes Architecture

Designing a platform that supports multiple teams or customers requires clear architectural patterns.

- [Multi-Tenant Kubernetes Architecture](multi-tenant-kubernetes-architecture.md)

- [How to Implement Kubernetes Multi-Tenancy](kubernetes-multi-tenancy-implementation.md)

---

## Kubernetes Multi-Tenancy Tools

Several tools exist to help implement multi-tenant platforms.

- [Kubernetes Multi-Tenancy Tools](kubernetes-multi-tenancy-tools.md)

This page compares common solutions such as:

- Multi-Tenant Operator (MTO)
- Capsule
- Loft
- vCluster
- Hierarchical Namespace Controller (HNC)

---

## MTO Comparisons

The following pages compare **Multi-Tenant Operator (MTO)** with other multi-tenancy approaches and tools.

- [MTO vs Capsule](mto-vs-capsule.md)

- [MTO vs Loft](mto-vs-loft.md)

- [MTO vs vCluster](mto-vs-vcluster.md)

- [MTO vs Hierarchical Namespace Controller (HNC)](mto-vs-hnc.md)

- [MTO vs KCP](mto-vs-kcp.md)

These comparisons explain differences in architecture, isolation models, operational complexity, and platform capabilities.

---

## Choosing the Right Approach

Different organizations adopt different multi-tenancy strategies depending on their platform requirements.

Some common factors that influence the choice include:

- platform scale
- isolation requirements
- operational complexity
- governance and policy enforcement
- tenant lifecycle automation
