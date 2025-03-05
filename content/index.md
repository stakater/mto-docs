---
head:
  - - meta
    - name: keywords
      content: SEO plugin
---

# Welcome to the Docs

[//]: # ( introduction.md, features.md)

Sharing Kubernetes clusters can significantly reduce costs and streamline administration. It enables efficient resource utilization, reduces configuration overhead, and simplifies the sharing of internal cluster resources among tenants. However, achieving secure and functional multi-tenancy presents challenges such as ensuring security, maintaining fairness, and mitigating the impact of noisy neighbors.

Kubernetes is inherently designed as a single-tenant platform. Managed Kubernetes services like AKS, EKS, GKE, and OpenShift have improved security through "secure by default" concepts, but designing and orchestrating all the moving parts required for a secure multi-tenant platform remains a complex task. This complexity makes it challenging for cluster administrators to host multiple tenants effectively within a single cluster.

Clusters can be shared in various ways:

* Different applications might run in the same cluster.
* Multiple instances of the same application could operate within a single cluster, one for each end user.

These scenarios are collectively referred to as multi-tenancy. While Kubernetes and many managed applications provide foundational resources to achieve multi-tenancy, leveraging these primitives requires professional expertise and deep knowledge of the platform.

The Multi-Tenant Operator (MTO) builds on Kubernetes' capabilities, simplifying the orchestration of secure and efficient multi-tenancy. By addressing the unique needs of shared clusters, MTO helps cluster administrators overcome the inherent complexities of multi-tenancy, enabling them to harness its full potential.

## Installation

Refer to the [installation guide](./installation/overview.md) for setting up MTO.
