# Concepts

Here are the key concepts of Multi-Tenant Operator (MTO):

## Core Operators

### Tenant

A **Tenant** represents a logical grouping of namespaces, users, and resources within a Kubernetes cluster, enabling isolated environments for teams or projects. It defines access controls, resource quotas, and namespace configurations specific to each tenant.

### Quota

**Quota** enforces resource limits for tenants, such as CPU, memory, and storage, ensuring fair allocation. It also defines minimum and maximum resource usage per pod or container within tenant namespaces.

### Extensions

**Extensions** enhance MTO functionality by integrating external services like ArgoCD. They allow seamless configuration of AppProjects for tenants, extending multi-tenant workflows.

### Resource Supervisor

**Resource Supervisor** manages the hibernation of deployments and stateful sets, enabling scaling down during user defined schedule or by manual trigger, optimizing resource utilization and reducing costs.

## Child Operators

### Template Operator

**Template Operator** is responsible for resource distribution in multiple namespaces based on user defined `Templates`. Full documentation can be found at [Template Operator Docs](https://docs.stakater.com/template-operator/latest/index.html)
