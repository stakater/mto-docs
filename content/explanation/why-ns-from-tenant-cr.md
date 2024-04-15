# Advantages of managing Namespaces from Tenant CR

* **Granular Control**: Tenant CRs provide fine-grained control over namespace management, allowing for precise configuration of access control, isolation, user management, and security policies specific to each namespace.

* **Centralized Management**: By utilizing Tenant CRs, namespace creation and management can be centralized, simplifying administrative tasks and ensuring consistent enforcement of policies across all namespaces.

* **Automated Prefix Model**: Tenant CRs support an automated prefix model for namespace creation, streamlining the addition of common prefixes like "dev" or "stage" to make namespaces unique for each tenant. This automation reduces manual effort and maintains naming convention consistency.

* **Efficient Label Management**: With Tenant CRs, labels and annotations across namespaces can be managed centrally, improving operational efficiency and providing better visibility into the environment.

* **Simplified GitOps**: Tenant CRs streamline GitOps practices by enabling the management of multiple namespaces from a single point. This integration simplifies deployment workflows and reduces the need to navigate through multiple repositories or folders for namespace-related changes.

* **Namespace provisioning for AppProjects**: Automated distribution of namespaces into their respective AppProjects.

[Creating Namespaces from Tenant CR](../tutorials/tenant/creating-namespaces.md)
