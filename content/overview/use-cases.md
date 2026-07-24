# Use Cases

The first step in deciding how to share your cluster is understanding your specific use case. This understanding helps you evaluate the available patterns and tools best suited to your needs. Broadly, multi-tenancy in Kubernetes clusters can be categorized into two main types, though variations and hybrids often exist.

## 1. Multi-Team Tenancy

A common use case for multi-tenancy involves sharing a cluster among multiple teams within an organization. Each team may operate one or more workloads, which often need to communicate with:

* Other workloads within the same cluster.
* Workloads located in different clusters.

In this scenario:

* Team members usually access Kubernetes resources either directly (e.g., via kubectl) or indirectly through tools like GitOps controllers or release automation systems.
* There is typically some degree of trust between teams, but safeguards are crucial. Policies such as Role-Based Access Control (RBAC), resource quotas, and network policies are necessary to ensure clusters are shared securely and fairly.

## 2. Multi-Customer Tenancy

Another common use case involves running multiple instances of a workload for customers, often by a Software-as-a-Service (SaaS) provider. This is sometimes referred to as "SaaS tenancy," but a more accurate term might be multi-customer tenancy, as this model is not exclusive to SaaS.

In this scenario:

* Customers do not have direct access to the cluster. Kubernetes operates behind the scenes, used solely by the vendor to manage workloads.
* Strong workload isolation is essential to maintain security and prevent resource contention.
*Cost optimization is often a primary focus, achieved through Kubernetes policies that ensure efficient and secure resource usage.
