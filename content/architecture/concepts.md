# Concepts

Here are the key concepts of Multi-Tenant Operator (MTO):

## Tenant

A **Tenant** represents a logical grouping of namespaces, users, and resources within a Kubernetes cluster, enabling isolated environments for teams or projects. It defines access controls, resource quotas, and namespace configurations specific to each tenant.

## Quota

The **Quota** enforces resource limits for tenants, such as CPU, memory, and storage, ensuring fair allocation. It also defines minimum and maximum resource usage per pod or container within tenant namespaces.

## Template

A **Template** is a reusable blueprint in Multi-Tenant Operator (MTO) that defines configurations for Kubernetes resources. It supports raw manifests, Helm charts, or resource mappings, enabling standardization and automation across multiple tenants.

## Template Instance (TI)

A **Template Instance** is a concrete implementation of a **Template**, created with specific parameters tailored for a particular tenant or use case. It generates actual Kubernetes resources based on the defined template.

## Template Group Instance (TGI)

A **Template Group Instance** is a collection of **Template Instances** that are deployed together as a unified set of configurations. It simplifies managing multiple interdependent resources for complex tenant setups.

## Extensions

**Extensions** enhance MTO functionality by integrating external services like ArgoCD. They allow seamless synchronization of repositories and configuration of AppProjects for tenants, extending multi-tenant workflows.

## Resource Supervisor

The **Resource Supervisor** manages the hibernation of deployments and stateful sets, enabling scheduled scaling down during inactivity and scaling up during active periods, optimizing resource utilization and reducing costs.
